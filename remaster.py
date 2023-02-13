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
import matplotlib.cm as cm
from subprocess import check_output

#clr = []
# for clrindex in range(10):
#    clr.append(cm.plasma(clrindex*0.01))

#print (clr)
# quit()

OUTPUTTYPE = ".pdf"
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


def list_jpg_in_dir(dir_name):
    files_list = []
    for file in os.listdir(dir_name):
        if file.endswith(".jpg"):
            #            if "0202172116" in file:
            #                 continue
            files_list.append(os.path.join(dir_name, file))
            if "0201145817" in file:
                files_list.append(None)
#            if "0202172116" in file:
#                files_list.append(None)
    return files_list


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
                    [jpg_filename.replace("\\", "/"), jpg_ts])

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

#    ref_fig_ratio, ref_fig_width = 6/4, 7
    fig, (axs) = plt.subplots(3, figsize=c.A4_size_in)
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
    plt.savefig(f"{OUTFOLDER}/references{OUTPUTTYPE}", dpi=300)
    plt.close()

    print("REFERENCES OK")

    experiments = session_json_object['experiments']
    print(experiments[0].keys())
    for experiment in experiments:
        # print(f"{experiment['folder']} {experiment['name']}")
        # print(experiment)
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

        # print(series)

        # print('UPDATE EXPERIMENTS_TABLE')
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
    print('UPDATE EXPERIMENTS_TABLE OK')
    ##################################################################################
    ##################################################################################
    ##################################################################################
    ##################################################################################
    known_img_folders = [
        ('009', 'Aleksandrs/paao_400nm_w3/point52water0102_2'),
        ('015', 'Aleksandrs/paao_400nm_w3/012_refl_01feb_NaCl04'),
        ('016', 'Aleksandrs/paao_400nm_w3/013_refl_01feb_NaCl10'),
        ('022', 'Aleksandrs/paao_400nm_w3/018_refl_01feb_NaCl16'),
        ('023', 'Aleksandrs/paao_400nm_w3/019_refl_01feb_NaCl22'),
        #
        ('027', 'Aleksandrs/paao_400nm_w3/200_PBS_02feb_refl'),
        ('032', 'Aleksandrs/paao_400nm_w3/205_DNS_refl_02feb'),
        ('036', 'Aleksandrs/paao_400nm_w3/208_DNS2h_refl_02feb'),
        ('040', 'Aleksandrs/paao_400nm_w3/211_BSA_refl_02feb')

    ]

# 027	31.01.23/refs/dark10.asc	31.01.23/refs/darkForWhite10.asc	31.01.23/refs/white11.asc	PBS	unpol	PBS-reflectance	2023-02-02 12:53:33.697851
# 032	31.01.23/refs/dark10.asc	31.01.23/refs/darkForWhite10.asc	31.01.23/refs/white11.asc	DNS	unpol	DNS-reflectance	2023-02-02 15:43:59.135533
# 036	31.01.23/refs/dark10.asc	31.01.23/refs/darkForWhite10.asc	31.01.23/refs/white11.asc	DNS2h	unpol	DNS2h-reflectance	2023-02-02 17:28:23.240183
# 040	31.01.23/refs/dark10.asc	31.01.23/refs/darkForWhite10.asc	31.01.23/refs/white11.asc	BSA	unpol	BSA-reflectance	2023-02-02 19:51:07.481109
# 043	31.01.23/refs/dark10.asc	31.01.23/refs/darkForWhite10.asc	31.01.23/refs/white11.asc	VEGF100	unpol	VEGF100-reflectance	2023-02-02 21:00:48.710967
# 046	31.01.23/refs/dark10.asc	31.01.23/refs/darkForWhite10.asc	31.01.23/refs/white11.asc	VEGF500	unpol	VEGF500-reflectance	2023-02-02 22:05:24.455062
# 049	31.01.23/refs/dark10.asc	31.01.23/refs/darkForWhite10.asc	31.01.23/refs/white11.asc	VEGF1000	unpol	VEGF1000-reflectance	2023-02-02 23:04:04.689127

    for folder_pair in known_img_folders:
        imglist = list_jpg_in_dir(folder_pair[1])
        print(len(imglist))
        cur.execute(f"""SELECT
            {c.COL_MEMBER_FILE_NAME}
                FROM {c.FILE_TABLE}
                WHERE {c.COL_SERIES} = ?
                ORDER BY {c.COL_SPOT}
        """, [folder_pair[0]])

        img_index = -1
        for sel_filename_rez in cur.fetchall():
            img_index += 1
            print(sel_filename_rez[0])
            if imglist[img_index] is None:
                jpegfilename = None
            else:
                jpegfilename = imglist[img_index].replace("\\", "/")
            print(jpegfilename)

            cur.execute(f"""UPDATE {c.FILE_TABLE} SET
            {c.COL_JPG_FILE_NAME} = ?
        WHERE {c.COL_MEMBER_FILE_NAME} = ? """,
                        [jpegfilename, sel_filename_rez[0]])
        if cur.rowcount != 1:
            print(sel_filename_rez[0]+'MISSING JPG')

#    HERE
#    HERE
#    HERE
#    HERE
#    HERE
#    HERE
    cur.execute(f"""SELECT
            {c.COL_MEMBER_FILE_NAME},
            {c.COL_TSTAMP}
                FROM {c.FILE_TABLE}
                WHERE {c.COL_SPOT} NOT NULL
                AND {c.COL_JPG_FILE_NAME} IS NULL
                ORDER BY {c.COL_TSTAMP}
        """)
    for rez_spot_wo_jpg in cur.fetchall():
        print(rez_spot_wo_jpg)
        cur.execute(
            f"""SELECT {c.COL_JPG_FILE_NAME}, {c.COL_TSTAMP}
                FROM {c.JPG_FILE_TABLE}
                WHERE {c.COL_TSTAMP} < ?
                ORDER BY {c.COL_TSTAMP} DESC
                LIMIT 1""", [rez_spot_wo_jpg[1]])
        for rez_jpg_select in cur.fetchall():
            # print(rez_jpg_select)
            cur.execute(f"""UPDATE {c.FILE_TABLE} SET
                    {c.COL_JPG_FILE_NAME} = ?
                WHERE {c.COL_MEMBER_FILE_NAME} = ? """,
                        [rez_jpg_select[0], rez_spot_wo_jpg[0]])
            if cur.rowcount != 1:
                print(rez_jpg_select)

#    quit()

# cur.execute(f"""CREATE TABLE IF NOT EXISTS {c.FILE_TABLE}(
#    {c.COL_MEMBER_FILE_NAME} TEXT PRIMARY KEY,
#    {c.COL_FILE_TYPE} TEXT NOT NULL,
#    {c.COL_SERIES} TEXT,
#    {c.COL_SPOT} TEXT,
#    {c.COL_TSTAMP} TEXT,
#    {c.COL_JPG_FILE_NAME} TEXT,
#    FOREIGN KEY ({c.COL_SERIES}) REFERENCES {c.EXPERIMENTS_TABLE} ({c.COL_SERIES}) ,
#    FOREIGN KEY ({c.COL_SPOT}) REFERENCES {c.SPOTS_TABLE} ({c.COL_SPOT}),
#    FOREIGN KEY ({c.COL_JPG_FILE_NAME}) REFERENCES {c.JPG_FILE_TABLE} ({c.COL_JPG_FILE_NAME})
#    )""")

 #   quit()
    for white_ref in refset_dict.keys():
        # for white_ref in ['white12']:
        andor_dark = load_andor_asc(
            '', spectra_zf.read(refset_dict[white_ref][c.DARK]))
        series_nm = np.array(andor_dark['col1'])
        series_dark = np.array(andor_dark['col2'])
        series_dfw = load_andor_asc(
            '', spectra_zf.read(refset_dict[white_ref][c.DARK_FOR_WHITE]))['col2']
        series_white = load_andor_asc(
            '', spectra_zf.read(refset_dict[white_ref][c.WHITE]))['col2']
        ref = np.array(series_white)-np.array(series_dfw)
        print(white_ref)

        cur.execute(f"""SELECT
            {c.COL_SPOT},
            {c.COL_XPOS},
            {c.COL_YPOS},
            {c.COL_LINE}
                FROM {c.SPOTS_TABLE}
                ORDER BY {c.COL_SPOT}
                LIMIT 333
        """)
        for sel_spots_rez in cur.fetchall():
            print(sel_spots_rez)
            selected_spot = sel_spots_rez[0]

            fig = plt.figure()
            plt.rcParams.update({'font.size': 8})
            fig.set_figheight(c.A4_width_in)
            fig.set_figwidth(c.A4_height_in)

        #ax1 = plt.subplot2grid(shape=(3, 3), loc=(0, 0), colspan=2, rowspan=2)
            subplot_shape = (4, 4)
            ax_spectra = plt.subplot2grid(
                shape=subplot_shape, loc=(0, 0), colspan=2, rowspan=2)
            ax_delta = plt.subplot2grid(
                shape=subplot_shape, loc=(2, 0), colspan=2, rowspan=2)
            ax_img0 = plt.subplot2grid(
                shape=subplot_shape, loc=(0, 2))
            ax_img1 = plt.subplot2grid(
                shape=subplot_shape, loc=(0, 3))
            ax_img2 = plt.subplot2grid(
                shape=subplot_shape, loc=(1, 2))
            ax_img3 = plt.subplot2grid(
                shape=subplot_shape, loc=(1, 3))
            ax_img4 = plt.subplot2grid(
                shape=subplot_shape, loc=(2, 2))
            ax_img5 = plt.subplot2grid(
                shape=subplot_shape, loc=(2, 3))
            ax_img6 = plt.subplot2grid(
                shape=subplot_shape, loc=(3, 2))
            ax_imgs = (ax_img0, ax_img1, ax_img2,
                       ax_img3, ax_img4, ax_img5, ax_img6)

            cur.execute(f"""SELECT
                {c.COL_SERIES},
                {c.COL_DARK},
                {c.COL_DARK_FOR_WHITE},
                {c.COL_WHITE},
                {c.COL_MEDIUM},
                {c.COL_POL},
                {c.COL_NAME},
                {c.COL_START_TIME}
                    FROM    {c.EXPERIMENTS_TABLE}
                    WHERE   {c.COL_WHITE}  LIKE ?
                    ORDER BY {c.COL_START_TIME}
            """, ['%'+white_ref+'.asc'])

            plot_index = -1
            for sel_experiment_rez in cur.fetchall():
                plot_index += 1
                print(sel_experiment_rez)
                selected_series = sel_experiment_rez[0]
                selected_name = sel_experiment_rez[6]
                cur.execute(f"""SELECT
                    {c.COL_MEMBER_FILE_NAME},
                    {c.COL_FILE_TYPE},
                    {c.COL_SERIES},
                    {c.COL_SPOT},
                    {c.COL_TSTAMP},
                    {c.COL_JPG_FILE_NAME}
                        FROM    {c.FILE_TABLE}
                        WHERE   {c.COL_SERIES} = ?
                        AND     {c.COL_SPOT} =?
                    ORDER BY {c.COL_TSTAMP}
                    """, [selected_series, selected_spot])

                for sel_file_rez in cur.fetchall():

                    print(sel_file_rez)
                    sel_file_name = sel_file_rez[0]
                    raw_spec = np.array(load_andor_asc(
                        '', spectra_zf.read(sel_file_name))['col2'])
                    Q = np.divide(raw_spec-series_dark, ref)
                    ax_spectra.plot(series_nm, Q,
                                    label=f"{sel_file_name[21:24]}, {selected_name}", color=cm.jet(plot_index/7))
                    if plot_index == 0:
                        baseline = Q
                    else:
                        dQ = Q - baseline
                        ax_delta.plot(series_nm, dQ,
                                      label=f"{sel_file_name[21:24]}, {selected_name}", color=cm.jet(plot_index/7))
                    jpg_file_name = sel_file_rez[5]
                    if not jpg_file_name is None:
                        original_jpg = mpimg.imread(jpg_file_name)
                        ax_imgs[plot_index].imshow(original_jpg)

                        ax_imgs[plot_index].set_title(
                            jpg_file_name[25:], fontdict={'fontsize': 7})

                for ax_img in ax_imgs:
                    ax_img.axis('off')


#        plt.plot(series_nm, series_white)
#       plt.plot(series_nm, ref)
            ax_spectra.legend(bbox_to_anchor=(0.0, -0.1),
                              loc='upper left', ncol=3)
            # (loc='upper left', ncol=2)
            ax_spectra.set(title=selected_spot)
            ax_delta.set(title='difference')

            for ax in [ax_spectra, ax_delta]:
                ax.set(xlabel="λ, nm")
                ax.set(ylabel="counts")
                ax.grid()
                ax.set(xlim=[min(nm), max(nm)])

            plt.tight_layout()
            # plt.show()
            plt.savefig(
                f"{OUTFOLDER}/{white_ref}_{selected_spot.split('.')[0]}{OUTPUTTYPE}", dpi=300)
            plt.close()

    # print(ref_spec.keys())
    #dict_keys(['Date and Time', 'Software Version', 'Temperature (C)', 'Model', 'Data Type', 'Acquisition Mode', 'Trigger Mode', 'Exposure Time (secs)', 'Accumulate Cycle Time (secs)', 'Frequency (Hz)', 'Number of Accumulations', 'Readout Mode', 'Horizontal binning', 'Extended Data Range', 'Horizontally flipped', 'Vertical Shift Speed (usecs)', 'Pixel Readout Time (usecs)', 'Serial Number', 'Pre-Amplifier Gain', 'Spurious Noise Filter Mode', 'Photon counted', 'Data Averaging Filter Mode', 'SR163', 'Wavelength (nm)', 'Grating Groove Density (l/mm)', 'col1', 'col2'])

con.commit()

check_output(
    f"pdftk {OUTFOLDER}\\*.pdf cat output all_spectra.pdf", shell=True).decode()


quit()
# print()
#cur.execute(f"""SELECT * from {c.FILE_TABLE}""")
#cur.execute(f"""SELECT * from {c.SPOTS_TABLE}""")
cur.execute(f"""SELECT * from {c.EXPERIMENTS_TABLE}""")
results = cur.fetchall()
for rezult in results:
    print(rezult)
