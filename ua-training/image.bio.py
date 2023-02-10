print("hallo word")
print("hello word 2")

import zipfile
import sqlite3
import json
from andor_asc import load_andor_asc
#import cnst as c
from matplotlib import pyplot as plt
import os
import numpy as np
import matplotlib.image as mpimg
import cv2

import os

def list_jpg_in_dir(dir_name):
    files_list=[]
    for file in os.listdir(dir_name):
        if file.endswith(".jpg"):
            files_list.append(os.path.join(dir_name, file))
            if "0201145817" in file:
                files_list.append('no_img.jpg')
    return files_list

PBS_files= list_jpg_in_dir('Aleksandrs/paao_400nm_w3/200_PBS_02feb_refl')
print(len(PBS_files))

DNS_files= list_jpg_in_dir('Aleksandrs/paao_400nm_w3/205_DNS_refl_02feb')
print(len(DNS_files))

DNS2h_files= list_jpg_in_dir('Aleksandrs/paao_400nm_w3/208_DNS2h_refl_02feb')
print(len(DNS2h_files))

BSA_files= list_jpg_in_dir('Aleksandrs/paao_400nm_w3/211_BSA_refl_02feb')
print(len(BSA_files))


OUTFOLDER = 'pictures.bio'

if os.path.exists(OUTFOLDER):
    for f in os.listdir(OUTFOLDER):
        os.remove(os.path.join(OUTFOLDER, f))
else:
    os.mkdir(OUTFOLDER)

for n in range(52):
    print(n)

    fig = plt.figure()
    fig.set_figheight(9)
    fig.set_figwidth(12)

    #ax1 = plt.subplot2grid(shape=(3, 3), loc=(0, 0), colspan=2, rowspan=2)
    ax2 = plt.subplot2grid(shape=(3, 3), loc=(0, 2))
    ax3 = plt.subplot2grid(shape=(3, 3), loc=(1, 2))
    ax4 = plt.subplot2grid((3, 3), (2, 2))
    ax5 = plt.subplot2grid((3, 3), (2, 1))
   # ax6 = plt.subplot2grid((3, 3), (2, 0))

    jpg_file_name=PBS_files[n]
    #'Aleksandrs/paao_400nm_w3/200_PBS_02feb_refl/0202124519.jpg'
    original_jpg = mpimg.imread(jpg_file_name)

    ax2.imshow(original_jpg)
    ax2.axis('off')
    ax2.set_title('PBS')


    jpg_file_name=DNS_files[n]
    #'Aleksandrs/paao_400nm_w3/205_DNS_refl_02feb/0202153812.jpg'
    original_jpg = mpimg.imread(jpg_file_name)

    ax3.imshow(original_jpg)
    ax3.axis('off')
    ax3.set_title('DNS')



    jpg_file_name=DNS2h_files[n]
    #'Aleksandrs/paao_400nm_w3/208_DNS2h_refl_02feb/0202172105.jpg'
    original_jpg = mpimg.imread(jpg_file_name)

    ax4.imshow(original_jpg)
    ax4.axis('off')
    ax4.set_title('DNS2h')

    jpg_file_name=BSA_files[n]
    #'Aleksandrs/paao_400nm_w3/211_BSA_refl_02feb/0202193944.jpg'
    original_jpg = mpimg.imread(jpg_file_name)

    ax5.imshow(original_jpg)
    ax5.axis('off')
    ax5.set_title('BSA')



    plt.tight_layout()
    plt.show()
    plt.savefig((os.path.join(OUTFOLDER, str(n).zfill(5))))
    plt.close()