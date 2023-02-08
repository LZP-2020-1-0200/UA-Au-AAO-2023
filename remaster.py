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
JPG_TIMESTAMPS_FILE_NAME = 'Aleksandrs/timestamps-jpg-0202.txt'
# SPECTRA_ZIP_FILE_NAME = '31.01.23.zip'
# SPECTRA_TIMESTAMPS_FILE_BASENAME = 'timestamps-asc-0201'
SPECTRA_ZIP_FILE_NAME = '31.01.23-02.02.23.zip'
SPECTRA_TIMESTAMPS_FILE_BASENAME = 'timestamps-asc-0202'


if os.path.exists(OUTFOLDER):
    for f in os.listdir(OUTFOLDER):
        os.remove(os.path.join(OUTFOLDER, f))
else:
    os.mkdir(OUTFOLDER)


con = sqlite3.connect(f"{OUTFOLDER}/{c.DBFILE}")
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
    {c.COL_POL} TEXT,
    {c.COL_NAME} TEXT,
    {c.COL_START_TIME} TEXT
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

cur.execute(f"DROP TABLE IF EXISTS {c.REF_SETS_TABLE}")
cur.execute(f"""CREATE TABLE IF NOT EXISTS {c.REF_SETS_TABLE}(
    {c.COL_WHITE} TEXT PRIMARY KEY,
    {c.COL_DARK_FOR_WHITE} TEXT NOT NULL,
    {c.DARK} TEXT NOT NULL,
    {c.COL_POL} TEXT NOT NULL,
    FOREIGN KEY ({c.COL_WHITE}) REFERENCES {c.FILE_TABLE} ({c.COL_MEMBER_FILE_NAME}),
    FOREIGN KEY ({c.COL_DARK_FOR_WHITE}) REFERENCES {c.FILE_TABLE} ({c.COL_MEMBER_FILE_NAME}),
    FOREIGN KEY ({c.DARK}) REFERENCES {c.FILE_TABLE} ({c.COL_MEMBER_FILE_NAME})
    )""")


ignorelist = ('31.01.23/pieraksti.txt',
              '31.01.23/timestamps-asc-0131.txt',
              '31.01.23/ekspozicija.png',
              '31.01.23/Kinetika/Kinetika_dns.asc',
              '31.01.23/timestamps-asc-0201.txt'
              )

with zipfile.ZipFile(SPECTRA_ZIP_FILE_NAME, "r") as spectra_zf:
    for member_file_name in spectra_zf.namelist():
        if member_file_name in ignorelist:
            continue
        if member_file_name[-1] == '/':
            continue
        if '/Kinetika/' in member_file_name:
            continue
        if '/imgs/experiments' in member_file_name:
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

            # print(member_file_name)
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

    # quit()
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
        if cur.rowcount > 1:
            print(cur.rowcount)
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

        if 'refs/white13' in specfilename:
            reference_sets.append({c.POL: c.P_POL})
            reference_sets[-1][c.WHITE] = specfilename
            continue
        if 'refs/darkForWhite12' in specfilename:
            reference_sets[-1][c.DARK_FOR_WHITE] = specfilename
            continue
        if 'refs/dark12' in specfilename:
            reference_sets[-1][c.DARK] = specfilename
            continue

        if 'refs/white12' in specfilename:
            reference_sets.append({c.POL: c.S_POL})
            reference_sets[-1][c.WHITE] = specfilename
            continue
        if 'refs/darkForWhite11' in specfilename:
            reference_sets[-1][c.DARK_FOR_WHITE] = specfilename
            continue
        if 'refs/dark11' in specfilename:
            reference_sets[-1][c.DARK] = specfilename
            continue

        if 'refs/white11' in specfilename:
            reference_sets.append({c.POL: c.UNPOL})
            reference_sets[-1][c.WHITE] = specfilename
            continue
        if 'refs/darkForWhite10' in specfilename:
            reference_sets[-1][c.DARK_FOR_WHITE] = specfilename
            continue
        if 'refs/dark10' in specfilename:
            reference_sets[-1][c.DARK] = specfilename
            continue

        print(specfilename)
#        ref_spec = load_andor_asc('', spectra_zf.read(specfilename))
#        nm = ref_spec['col1']
#        counts = ref_spec['col2']
#        print(f"Exposure Time (secs) = {ref_spec['Exposure Time (secs)']}")
#        print( f"Number of Accumulations = {ref_spec['Number of Accumulations']}")

    ref_fig_ratio, ref_fig_width = 6/4, 7
    fig, (axs) = plt.subplots(3, figsize=(
        ref_fig_width, ref_fig_width*ref_fig_ratio))
    (ax_white, ax_dfw, ax_dark) = axs
    refset_dict = {}
    for refset in reference_sets:
        print(f"refset = {refset}")
        refset_name = refset[c.WHITE].split('/')[2].split('.')[0]
        refset_dict[refset_name] = refset
        print(f"refset_name = {refset_name}")
        cur.execute(f"""INSERT INTO {c.REF_SETS_TABLE}
            ({c.COL_WHITE},{c.COL_DARK_FOR_WHITE},{c.DARK},{c.COL_POL})
            VALUES (?,?,?,?)""",
                    [refset[c.WHITE], refset[c.DARK_FOR_WHITE], refset[c.DARK], refset[c.POL]])
        if cur.rowcount != 1:
            print(refset)
        raw_white = load_andor_asc('', spectra_zf.read(refset[c.WHITE]))
        ax_white.plot(
            raw_white['col1'], raw_white['col2'], label=f"{refset[c.POL]} {refset[c.WHITE].split('/')[-1]}")

        raw_dfw = load_andor_asc(
            '', spectra_zf.read(refset[c.COL_DARK_FOR_WHITE]))
        ax_dfw.plot(
            raw_dfw['col1'], raw_dfw['col2'], label=f"{refset[c.POL]} {refset[c.COL_DARK_FOR_WHITE].split('/')[-1]}")

        raw_dark = load_andor_asc(
            '', spectra_zf.read(refset[c.DARK]))
        ax_dark.plot(
            raw_dark['col1'], raw_dark['col2'], label=f"{refset[c.POL]} {refset[c.DARK].split('/')[-1]}")

    nm = raw_dark['col1']
    for ax in axs:
        ax.set(xlabel='$\\lambda$, nm')
        ax.set(ylabel='counts')
        ax.set(xlim=[min(nm), max(nm)])
        ax.legend(loc="best")
        ax.grid()

    ax_dfw.title.set_text(c.DARK_FOR_WHITE)
    ax_dark.title.set_text(c.DARK)
    ax_white.title.set_text(c.WHITE)
    plt.tight_layout()
    # plt.show()
    plt.savefig(f"{OUTFOLDER}/references.png", dpi=300)
    plt.close()

    print("REFERENCES OK")

    experiments = session_json_object['experiments']
    print(experiments[0].keys())
    for experiment in experiments:
        #print(f"{experiment['folder']} {experiment['name']}")
        print(experiment)
        series = experiment['folder'].split('\\')[-1]
        white = None
        dark_for_white = None
        dark = None
        reference_set = {c.POL: None, c.WHITE: None,
                         c.DARK_FOR_WHITE: None, c.DARK: None}
        medium = None
        pol = None
        name = experiment['name']
        start_time = experiment['timestamp']

        if 'reflectance' in name:
            pol = c.UNPOL
        elif 's-pol' in name:
            pol = c.S_POL
        elif 'p-pol' in name:
            pol = c.P_POL

        if c.VEGF1000 in name:
            medium = c.VEGF1000
        elif c.VEGF500 in name:
            medium = c.VEGF500
        elif c.VEGF100 in name:
            medium = c.VEGF100
        elif c.BSA in name:
            medium = c.BSA
        elif c.DNS2h in name:
            medium = c.DNS2h
        elif c.DNS in name:
            medium = c.DNS
        elif c.PBS in name:
            medium = c.PBS

        elif c.NaCl_22 in name:
            medium = c.NaCl_22
        elif c.NaCl_16 in name:
            medium = c.NaCl_16
        elif c.NaCl_10 in name:
            medium = c.NaCl_10
        elif 'NaCl4' in name:
            medium = c.NaCl_04
        elif 'ater' in name:
            medium = c.H2O
        elif c.AIR in name:
            medium = c.AIR

        if series in ['011', '013', '019', '020', '025']:
            reference_set = refset_dict['white07']
        elif series in ['010', '014', '018', '021', '024']:  # 017 = fail
            reference_set = refset_dict['white08']
        elif series in ['009', '015', '016', '022', '023']:
            reference_set = refset_dict['white10']
        elif series in ['027', '032', '036', '040', '043', '046', '049']:
            reference_set = refset_dict['white11']
        elif series in ['028', '030', '034', '038', '041', '044', '047']:
            reference_set = refset_dict['white12']
        elif series in ['029', '031', '035', '039', '042', '045', '048']:
            reference_set = refset_dict['white13']

        if pol == reference_set[c.POL]:
            white = reference_set[c.WHITE]
            dark_for_white = reference_set[c.DARK_FOR_WHITE]
            dark = reference_set[c.COL_DARK]

        print(series)

        cur.execute(f"""UPDATE {c.EXPERIMENTS_TABLE} SET
            {c.COL_WHITE} = ?,
            {c.COL_DARK_FOR_WHITE} = ?,
            {c.COL_DARK} = ?,
            {c.COL_MEDIUM} = ?,
            {c.COL_POL} = ?,
            {c.COL_NAME} = ?,
            {c.COL_START_TIME} =?
        WHERE {c.COL_SERIES} = ? """,
                    [white, dark_for_white, dark, medium, pol, name, start_time, series])
        if cur.rowcount != 1:
            print(point)

    # print(ref_spec.keys())
    #dict_keys(['Date and Time', 'Software Version', 'Temperature (C)', 'Model', 'Data Type', 'Acquisition Mode', 'Trigger Mode', 'Exposure Time (secs)', 'Accumulate Cycle Time (secs)', 'Frequency (Hz)', 'Number of Accumulations', 'Readout Mode', 'Horizontal binning', 'Extended Data Range', 'Horizontally flipped', 'Vertical Shift Speed (usecs)', 'Pixel Readout Time (usecs)', 'Serial Number', 'Pre-Amplifier Gain', 'Spurious Noise Filter Mode', 'Photon counted', 'Data Averaging Filter Mode', 'SR163', 'Wavelength (nm)', 'Grating Groove Density (l/mm)', 'col1', 'col2'])

con.commit()
quit()
# print()
#cur.execute(f"""SELECT * from {c.FILE_TABLE}""")
#cur.execute(f"""SELECT * from {c.SPOTS_TABLE}""")
cur.execute(f"""SELECT * from {c.EXPERIMENTS_TABLE}""")
results = cur.fetchall()
for rezult in results:
    print(rezult)
