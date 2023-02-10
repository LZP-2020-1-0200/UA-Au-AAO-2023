from andor_asc import load_andor_asc
from matplotlib import pyplot as plt
import numpy as np

OUTPUTFOLDER="process/"

print("hallo word")
whitefilename="refs/white10.asc"
ref_white = load_andor_asc(whitefilename)
nm = ref_white['col1']
countswhite = ref_white['col2']
plt.plot(nm,countswhite,label=whitefilename)

darkforwhitefilename="refs/darkForWhite09.asc"
ref_dark_for_white = load_andor_asc(darkforwhitefilename)
nm = ref_dark_for_white['col1']
countsdark_for_white = ref_dark_for_white['col2']
plt.plot(nm,countsdark_for_white,label=darkforwhitefilename)

darkfilename="refs/dark09.asc"
ref_dark = load_andor_asc(darkfilename)
nm = ref_dark['col1']
countsdark = ref_dark['col2']
plt.plot(nm,countsdark,label=darkfilename)


plt.legend(loc="upper left")
plt.xlabel("λ, nm")
plt.ylabel("counts")
plt.grid()
plt.xlim([min(nm), max(nm)])
#plt.show()
plt.tight_layout()
plt.savefig(OUTPUTFOLDER+"references.png",dpi=300)
plt.close()



w = np.array(countswhite)
dfw = np.array(countsdark_for_white)
d = np.array(countsdark)


#waterfilename="experiments/010/00001.asc"
#water = load_andor_asc(waterfilename)
#nm = water['col1']
#countswater = water['col2']
#h2o=np.array(countswater)-d
#reflecanceH2O=np.divide(h2o,w-dfw)
#plt.plot(nm,reflecanceH2O,label=waterfilename)

#NaCl4filename="experiments/015/00001.asc"
#NaCl4 = load_andor_asc(NaCl4filename)
#nm = NaCl4['col1']
#countsNaCl4 = NaCl4['col2']
#NaCl4=np.array(countsNaCl4)-d
#reflecanceNaCl4=np.divide(NaCl4,w-dfw)
#plt.plot(nm,reflecanceNaCl4,label=NaCl4filename)

def plotsinglespec(fname,medium,colr,ri):
    spec = load_andor_asc(fname)
    counts=spec['col2']
    clincaunts=np.array(counts)-d
    reflecance=np.divide(clincaunts,w-dfw)
    plt.plot(nm,reflecance,".",markersize=1.5,color=colr)
    pfit = np.polyfit(nm, reflecance, 7)
    pval=np.polyval(pfit,nm)
    plt.plot(nm,pval,color=colr,label=medium)
    d1=np.polyder(pfit)
    d2=np.polyder(pfit,2)
    r1=np.roots(d1)
    print(r1)
   # res = np.where(np.logical_and(r1 >= min(nm), r1 <= max(nm)))
    goodroots = r1 [ (r1 >=min(nm)) * (r1 <= max(nm))]
    print(goodroots)
    goodextreems=np.polyval(pfit,goodroots)
    max_nm=None
    max_val=None
    min_nm=None
    min_val=None
    for rx in goodroots:
        if np.polyval(d2,rx) <0:
            max_nm=rx
            max_val=np.polyval(pfit,max_nm)
            plt.plot(max_nm,max_val,"+",markersize=25,color=colr)
        else:
            min_nm=rx
            min_val=np.polyval(pfit,min_nm)
            plt.plot(min_nm,min_val,"x",markersize=25,color=colr)
    return (ri,max_nm,max_val,min_nm,min_val)
#plotsinglespec("experiments/009/00001.asc")
#plotsinglespec("experiments/015/00001.asc")
#plotsinglespec("experiments/016/00001.asc")
#plotsinglespec("experiments/022/00001.asc")
#plotsinglespec("experiments/023/00001.asc")

#plt.legend(loc="upper left")
#plt.xlabel("λ, nm")
#plt.ylabel("counts")
#plt.grid()
#plt.xlim([min(nm), max(nm)])

#plt.savefig("00001.png",dpi=300)
#plt.close()
#RI = {AIR: 1.0,
     # H2O: 1.333,
    #  EtOH: 1.3630,
     # NaCl_04: 1.3400,
      #NaCl_10: 1.3505,
      #NaCl_16: 1.3612,
      #NaCl_22: 1.3721}

def plotdiferentmedia(point):
    rezults=[]
    plt.figure(figsize=(16,9))
    plt.subplot(2, 3, 1)
    rezults.append(plotsinglespec(f"experiments/009/{point}.asc","H₂O","cyan",1.333))
    rezults.append(plotsinglespec(f"experiments/015/{point}.asc", "NaCl 4%","blue",1.3400))
    rezults.append(plotsinglespec(f"experiments/016/{point}.asc","NaCl 10%","purple", 1.3505))
    rezults.append(plotsinglespec(f"experiments/022/{point}.asc","NaCl 16%","green", 1.3612)) 
    rezults.append(plotsinglespec(f"experiments/023/{point}.asc","NaCl 22%","red", 1.3721))

    plt.title(point, y=1.0, pad=-14)
    #plt.legend(bbox_to_anchor=(1.7, 1.4),loc='upper center',ncol=5)
    plt.legend(loc='lower center',ncol=2)
    plt.xlabel("λ, nm")
    plt.ylabel("counts")
    plt.grid()
    plt.xlim([min(nm), max(nm)])
    plt.ylim([0.1, 0.7])
    #plt.tight_layout()
    #plt.savefig(OUTPUTFOLDER+f"{point}.png",dpi=300)
    #plt.close()
    print(rezults)
    out_ri=[]
    out_max_nm=[]
    out_max_val=[]
    out_min_nm=[]
    out_min_val=[]
    for r in rezults:
        out_ri.append(r[0])
        out_max_nm.append(r[1])
        out_max_val.append(r[2])
        out_min_nm.append(r[3])
        out_min_val.append(r[4])
    plt.subplot(2, 3, 2)
    plt.plot(out_ri,out_max_nm)

    plt.xlabel("reflaction (n)")
    plt.ylabel("λ, nm")
    plt.grid()
    plt.title("max point",y=1.0, pad=-14)


    
    plt.subplot(2, 3, 3)
    plt.plot(out_ri,out_min_nm)
    plt.xlabel("reflaction (n)")
    plt.ylabel("λ, nm")
    plt.grid()
    plt.title("min point",y=1.0, pad=-14)



    plt.subplot(2, 3, 4)
    plt.plot(out_ri,out_max_val)
    plt.xlabel("reflaction (n)")
    plt.ylabel("λ, nm")
    plt.grid()
    plt.title("max val",y=1.0, pad=-14)

    
    plt.subplot(2, 3, 5)
    plt.plot(out_ri,out_min_val)
    plt.xlabel("reflaction (n)")
    plt.ylabel("λ, nm")
    plt.grid()
    plt.title("min val",y=1.0, pad=-14)



    #plt.legend(loc="upper left")



    #plt.savefig(OUTPUTFOLDER+"max point",dpi=300)
    plt.tight_layout()
    #plt.show()
    plt.savefig(OUTPUTFOLDER+f"{point}.png",dpi=300)
    plt.close()



   

#plotdiferentmedia('00001')
#plotdiferentmedia('00002')
#plotdiferentmedia('00003')
#plotdiferentmedia('00004')

   
     




for x in range(1, 53):
  plotdiferentmedia(str(x).zfill(5))

#In [3]: str(1).zfill(2)
#Out[3]: '01'

#refset = {'pol': 'S-pol', 'white': '31.01.23/refs/white07.asc', 'dark_for_white': '31.01.23/refs/darkForWhite07.asc', 'dark': '31.01.23/refs/dark07.asc'}
#refset = {'pol': 'P-pol', 'white': '31.01.23/refs/white08.asc', 'dark_for_white': '31.01.23/refs/darkForWhite08.asc', 'dark': '31.01.23/refs/dark08.asc'}
#refset = {'pol': 'unpol', 'white': '31.01.23/refs/white10.asc', 'dark_for_white': '31.01.23/refs/darkForWhite09.asc', 'dark': '31.01.23/refs/dark09.asc'}
#refset = {'pol': 'unpol', 'white': '31.01.23/refs/white11.asc', 'dark_for_white': '31.01.23/refs/darkForWhite10.asc', 'dark': '31.01.23/refs/dark10.asc'}
#refset = {'pol': 'S-pol', 'white': '31.01.23/refs/white12.asc', 'dark_for_white': '31.01.23/refs/darkForWhite11.asc', 'dark': '31.01.23/refs/dark11.asc'}
#refset = {'pol': 'P-pol', 'white': '31.01.23/refs/white13.asc', 'dark_for_white': '31.01.23/refs/darkForWhite12.asc', 'dark': '31.01.23/refs/dark12.asc'}