import zipfile
import sqlite3
import json
from andor_asc import load_andor_asc
import cnst as c
from matplotlib import pyplot as plt
import os
import numpy as np
import matplotlib.image as mpimg
import cv2

OUTFOLDER = 'tmp_7r'
JPG_TIMESTAMPS_FILE_NAME = 'Aleksandrs/timestamps-jpg-0201.txt'
SPECTRA_ZIP_FILE_NAME = '31.01.23.zip'
SPECTRA_TIMESTAMPS_FILE_BASENAME = 'timestamps-asc-0201'

if os.path.exists(OUTFOLDER):
    for f in os.listdir(OUTFOLDER):
        os.remove(os.path.join(OUTFOLDER, f))
else:
    os.mkdir(OUTFOLDER)


con = sqlite3.connect(c.DBFILE)
cur = con.cursor()
cur.execute("PRAGMA foreign_keys = ON")

cur.execute(f"DROP TABLE IF EXISTS {c.JPG_FILE_TABLE}")
cur.execute(f"""CREATE TABLE IF NOT EXISTS {c.JPG_FILE_TABLE}(
    {c.COL_JPG_FILE_NAME} TEXT PRIMARY KEY,
    {c.COL_TSTAMP} TEXT UNIQUE NOT NULL
    )""")

with open(JPG_TIMESTAMPS_FILE_NAME, "r", encoding='utf-8') as jpg_timestamps_fails:
    jpg_timestamp_lines = jpg_timestamps_fails.readlines()
for jpg_timestamp_line in jpg_timestamp_lines:
    jpg_ts_parts = jpg_timestamp_line.strip("\n\r").split("\t")
    # print(jpg_ts_parts)
    if '.jpg' in jpg_ts_parts[0]:
        jpg_filename = jpg_ts_parts[0][3:]
        jpg_ts = jpg_ts_parts[1]
        # print(jpg_filename)
        cur.execute(f"""INSERT INTO {c.JPG_FILE_TABLE}
            ({c.COL_JPG_FILE_NAME},{c.COL_TSTAMP})
            VALUES (?,?)""",
                    [jpg_filename, jpg_ts])

cur.execute(f"DROP TABLE IF EXISTS {c.EXPERIMENTS_TABLE}")
cur.execute(f"""CREATE TABLE IF NOT EXISTS {c.EXPERIMENTS_TABLE}(
    {c.COL_SERIES} TEXT PRIMARY KEY,
    {c.COL_DARK} TEXT,
    {c.COL_DARK_FOR_WHITE} TEXT,
    {c.COL_WHITE} TEXT,
    {c.COL_MEDIUM} TEXT,
    {c.COL_POL} TEXT
    )""")

cur.execute(f"DROP TABLE IF EXISTS {c.SPOTS_TABLE}")
cur.execute(f"""CREATE TABLE IF NOT EXISTS {c.SPOTS_TABLE}(
    {c.COL_SPOT} TEXT PRIMARY KEY,
    {c.COL_XPOS} INTEGER,
    {c.COL_YPOS} INTEGER,
    {c.COL_LINE} INTEGER )""")

cur.execute(f"DROP TABLE IF EXISTS {c.FILE_TABLE}")
cur.execute(f"""CREATE TABLE IF NOT EXISTS {c.FILE_TABLE}(
    {c.COL_MEMBER_FILE_NAME} TEXT PRIMARY KEY,
    {c.COL_FILE_TYPE} TEXT NOT NULL,
    {c.COL_SERIES} TEXT,
    {c.COL_SPOT} TEXT,
    {c.COL_TSTAMP} TEXT,
    {c.COL_JPG_FILE_NAME} TEXT,
    FOREIGN KEY ({c.COL_SERIES}) REFERENCES {c.EXPERIMENTS_TABLE} ({c.COL_SERIES}) ,
    FOREIGN KEY ({c.COL_SPOT}) REFERENCES {c.SPOTS_TABLE} ({c.COL_SPOT}),
    FOREIGN KEY ({c.COL_JPG_FILE_NAME}) REFERENCES {c.JPG_FILE_TABLE} ({c.COL_JPG_FILE_NAME})
    )""")


ignorelist = ('31.01.23/pieraksti.txt',
              '31.01.23/timestamps-asc-0131.txt',
              '31.01.23/ekspozicija.png'
              )

with zipfile.ZipFile(SPECTRA_ZIP_FILE_NAME, "r") as spectra_zf:
    for member_file_name in spectra_zf.namelist():
        if member_file_name in ignorelist:
            continue
        if member_file_name[-1] == '/':
            continue
        if SPECTRA_TIMESTAMPS_FILE_BASENAME in member_file_name:
            spectra_timestamps_file_name = member_file_name
            continue
        if 'session.json' in member_file_name:
            session_json_file_name = member_file_name
            continue
        if '/refs/white' in member_file_name:
            cur.execute(f"""INSERT INTO {c.FILE_TABLE}
            ({c.COL_MEMBER_FILE_NAME},{c.COL_FILE_TYPE})
            VALUES (?,?)""",
                        [member_file_name, c.WHITE])
            continue
        if '/refs/darkForWhite' in member_file_name:
            cur.execute(f"""INSERT INTO {c.FILE_TABLE}
            ({c.COL_MEMBER_FILE_NAME},{c.COL_FILE_TYPE})
            VALUES (?,?)""",
                        [member_file_name, c.DARK_FOR_WHITE])
            continue
        if '/refs/dark' in member_file_name:
            cur.execute(f"""INSERT INTO {c.FILE_TABLE}
            ({c.COL_MEMBER_FILE_NAME},{c.COL_FILE_TYPE})
            VALUES (?,?)""",
                        [member_file_name, c.DARK])
            continue

        if '.asc' in member_file_name:
            file_name_parts = member_file_name.split('/')
            series = file_name_parts[2]
            cur.execute(f"""INSERT OR IGNORE INTO {c.EXPERIMENTS_TABLE}
            ({c.COL_SERIES}) VALUES (?)""", [series])

            spot = file_name_parts[3]
            # print(spot)
            cur.execute(f"""INSERT OR IGNORE INTO {c.SPOTS_TABLE}
            ({c.COL_SPOT}) VALUES (?)""", [spot])

            cur.execute(f"""INSERT INTO {c.FILE_TABLE}
            ({c.COL_MEMBER_FILE_NAME},{c.COL_FILE_TYPE},{c.COL_SERIES},{c.COL_SPOT})
            VALUES (?,?,?,?)""",
                        [member_file_name, c.SPECTRUM, series, spot])
            continue
        print(member_file_name)

    print(f"spectra_timestamps_file_name = {spectra_timestamps_file_name}")
    print(f"session_json_file_name = {session_json_file_name}")

    with spectra_zf.open(session_json_file_name) as session_jsf:
        session_json_object = json.load(session_jsf)
    print(session_json_object.keys())
    points = session_json_object['points']
    point_nr = 0
    lines = {}
    for point in points:
        #        print(point)
        line = point_nr // 100
        lines[line] = line
#        print(line)
        cur.execute(f"""UPDATE {c.SPOTS_TABLE} SET
            {c.COL_XPOS} = ?,
            {c.COL_YPOS} = ?,
            {c.COL_LINE} = ?
        WHERE {c.COL_SPOT} = ? """,
                    [point['x'], point['y'], line, point['filename']])
        if cur.rowcount != 1:
            print(point)
        point_nr += 1

    with spectra_zf.open(spectra_timestamps_file_name) as spectra_timestamps_file:
        spectra_timestamps_data = spectra_timestamps_file.read()
        timestamps_lines = spectra_timestamps_data.decode('ascii').splitlines()
    for timestamps_line in timestamps_lines:
        #        print(timestamps_line)
        timestamps_line_parts = timestamps_line.split("\t")
        # print(timestamps_line_parts)
        timestamp = timestamps_line_parts[1]
        member_file_name = timestamps_line_parts[0][3:].replace('\\', '/')
        # print(member_file_name)

        cur.execute(f"""UPDATE {c.FILE_TABLE} SET
            {c.COL_TSTAMP} = ?
        WHERE {c.COL_MEMBER_FILE_NAME} = ? """,
                    [timestamp, member_file_name])
        if cur.rowcount != 1:
            # print(cur.rowcount)
            print(timestamps_line_parts)

    cur.execute(f"""SELECT
                {c.COL_TSTAMP},
                {c.COL_MEMBER_FILE_NAME},
                {c.COL_FILE_TYPE}
        FROM    {c.FILE_TABLE}
        WHERE   {c.COL_FILE_TYPE} ='{c.DARK}'
            OR  {c.COL_FILE_TYPE} ='{c.DARK_FOR_WHITE}'
            OR  {c.COL_FILE_TYPE} ='{c.WHITE}'
        ORDER BY {c.COL_TSTAMP}
        """)

    reference_sets = []
    reference_sets.append({c.POL: c.S_POL})
    for sel_refs_rez in cur.fetchall():
        # print(sel_refs_rez)
        specfilename = sel_refs_rez[1]

        if 'refs/white10.asc' in specfilename:
            reference_sets.append({c.POL: c.UNPOL})
            reference_sets[-1][c.WHITE] = specfilename
            continue
        if 'refs/darkForWhite09' in specfilename:
            reference_sets[-1][c.DARK_FOR_WHITE] = specfilename
            continue
        if 'refs/dark09' in specfilename:
            reference_sets[-1][c.DARK] = specfilename
            continue

        if 'refs/white09' in specfilename:  # FAIL
            continue

        if 'refs/white08' in specfilename:
            reference_sets.append({c.POL: c.P_POL})
            reference_sets[-1][c.WHITE] = specfilename
            continue
        if 'refs/darkForWhite08' in specfilename:
            reference_sets[-1][c.DARK_FOR_WHITE] = specfilename
            continue
        if 'refs/dark08' in specfilename:
            reference_sets[-1][c.DARK] = specfilename
            continue

        if 'refs/white07' in specfilename:
            reference_sets[-1][c.WHITE] = specfilename
            continue
        if 'refs/darkForWhite07' in specfilename:
            reference_sets[-1][c.DARK_FOR_WHITE] = specfilename
            continue
        if 'refs/dark07' in specfilename:
            reference_sets[-1][c.DARK] = specfilename
            continue

        # print(specfilename)
        ref_spec = load_andor_asc('', spectra_zf.read(specfilename))
        nm = ref_spec['col1']
        counts = ref_spec['col2']
#        print(f"Exposure Time (secs) = {ref_spec['Exposure Time (secs)']}")
#        print( f"Number of Accumulations = {ref_spec['Number of Accumulations']}")

    for refset in reference_sets:
        print(refset)

    experiments = session_json_object['experiments']
    for experiment in experiments:
        print(experiment)



        # print(ref_spec.keys())
        #dict_keys(['Date and Time', 'Software Version', 'Temperature (C)', 'Model', 'Data Type', 'Acquisition Mode', 'Trigger Mode', 'Exposure Time (secs)', 'Accumulate Cycle Time (secs)', 'Frequency (Hz)', 'Number of Accumulations', 'Readout Mode', 'Horizontal binning', 'Extended Data Range', 'Horizontally flipped', 'Vertical Shift Speed (usecs)', 'Pixel Readout Time (usecs)', 'Serial Number', 'Pre-Amplifier Gain', 'Spurious Noise Filter Mode', 'Photon counted', 'Data Averaging Filter Mode', 'SR163', 'Wavelength (nm)', 'Grating Groove Density (l/mm)', 'col1', 'col2'])


quit()
# print()
#cur.execute(f"""SELECT * from {c.FILE_TABLE}""")
#cur.execute(f"""SELECT * from {c.SPOTS_TABLE}""")
cur.execute(f"""SELECT * from {c.EXPERIMENTS_TABLE}""")
results = cur.fetchall()
for rezult in results:
    print(rezult)
