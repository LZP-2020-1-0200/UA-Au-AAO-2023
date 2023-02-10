import cv2
import matplotlib.image as mpimg
import numpy as np
import os
from matplotlib import pyplot as plt
from andor_asc import load_andor_asc
import json
import sqlite3
import zipfile
print("hallo word")
print("hello word 2")

#import cnst as c


def list_jpg_in_dir(dir_name):
    files_list = []
    for file in os.listdir(dir_name):
        if file.endswith(".jpg"):
            files_list.append(os.path.join(dir_name, file))
            if "0201145817" in file:
                files_list.append('no_img.jpg')
    return files_list


water_files = list_jpg_in_dir('Aleksandrs/paao_400nm_w3/point52water0102_2')
print(len(water_files))

NaCl04_files = list_jpg_in_dir(
    'Aleksandrs/paao_400nm_w3/012_refl_01feb_NaCl04')
print(len(NaCl04_files))

NaCl10_files = list_jpg_in_dir(
    'Aleksandrs/paao_400nm_w3/013_refl_01feb_NaCl10')
print(len(NaCl10_files))

NaCl16_files = list_jpg_in_dir(
    'Aleksandrs/paao_400nm_w3/018_refl_01feb_NaCl16')
print(len(NaCl16_files))

NaCl22_files = list_jpg_in_dir(
    'Aleksandrs/paao_400nm_w3/019_refl_01feb_NaCl22')
print(len(NaCl22_files))


# quit()
OUTFOLDER = 'pictures'

if os.path.exists(OUTFOLDER):
    for f in os.listdir(OUTFOLDER):
        os.remove(os.path.join(OUTFOLDER, f))
else:
    os.mkdir(OUTFOLDER)

for n in range(52):
    print(n)
    # continue

    #ratio = 6/4
    #width = 7

    # C:\Riga2023\Aleksandrs\paao_400nm_w3\point52water0102_2
    # 0201135012.jpg

    fig = plt.figure()
    fig.set_figheight(9)
    fig.set_figwidth(12)

    #ax1 = plt.subplot2grid(shape=(3, 3), loc=(0, 0), colspan=2, rowspan=2)
    ax2 = plt.subplot2grid(shape=(3, 3), loc=(0, 2))
    ax3 = plt.subplot2grid(shape=(3, 3), loc=(1, 2))
    ax4 = plt.subplot2grid((3, 3), (2, 2))
    ax5 = plt.subplot2grid((3, 3), (2, 1))
    ax6 = plt.subplot2grid((3, 3), (2, 0))

    jpg_file_name = water_files[n]
    # 'Aleksandrs/paao_400nm_w3/point52water0102_2/0201135012.jpg'
    original_jpg = mpimg.imread(jpg_file_name)

    ax2.imshow(original_jpg)
    ax2.axis('off')
    ax2.set_title('water')

    # C:\Riga2023\Aleksandrs\paao_400nm_w3\012_refl_01feb_NaCl04
    # 0201145628.jpg

    jpg_file_name = NaCl04_files[n]
    # 'Aleksandrs/paao_400nm_w3/012_refl_01feb_NaCl04/0201145628.jpg'
    original_jpg = mpimg.imread(jpg_file_name)

    ax3.imshow(original_jpg)
    ax3.axis('off')
    ax3.set_title('NaCl04')

    # C:\Riga2023\Aleksandrs\paao_400nm_w3\013_refl_01feb_NaCl10
    # 0201151641.jpg

    jpg_file_name = NaCl10_files[n]
    # 'Aleksandrs/paao_400nm_w3/013_refl_01feb_NaCl10/0201151641.jpg'
    original_jpg = mpimg.imread(jpg_file_name)

    ax4.imshow(original_jpg)
    ax4.axis('off')
    ax4.set_title('NaCl10')

    # C:\Riga2023\Aleksandrs\paao_400nm_w3\018_refl_01feb_NaCl16
    # 0201162141.jpg

    jpg_file_name = NaCl16_files[n]
    # 'Aleksandrs/paao_400nm_w3/018_refl_01feb_NaCl16/0201162141.jpg'
    original_jpg = mpimg.imread(jpg_file_name)

    ax5.imshow(original_jpg)
    ax5.axis('off')
    ax5.set_title('NaCl16')

    # C:\Riga2023\Aleksandrs\paao_400nm_w3\019_refl_01feb_NaCl22
    # 0201163347.jpg

    jpg_file_name = NaCl22_files[n]
    # 'Aleksandrs/paao_400nm_w3/019_refl_01feb_NaCl22/0201163347.jpg'
    original_jpg = mpimg.imread(jpg_file_name)

    ax6.imshow(original_jpg)
    ax6.axis('off')
    ax6.set_title('NaCl22')

    plt.tight_layout()
    # plt.show()
    plt.savefig((os.path.join(OUTFOLDER, str(n).zfill(5))))
    plt.close()
