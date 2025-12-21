import sys
import soundfile as sf
import glob
import os,tqdm
import re
from pathlib import Path

p2root = sys.argv[1]

manifest = p2root+"/manifest/"
aud_ext_pattrn = re.compile(r"\.(mp3|flac|wav)$")

if not os.path.exists(manifest):
    os.makedirs(manifest)

charset = set()
for folder_path in tqdm.tqdm(Path(p2root).iterdir()):
    if folder_path.is_file():
        continue

    folder = folder_path.name
    if 'manifest' == folder:
        continue
    data_fol = Path(f"{p2root}/{folder}")
    # wavs = [glob.glob(p2root+'/'+folder+'/**/*.flac',recursive=True)]
    wavs = [file_path.as_posix() for file_path in data_fol.iterdir() if file_path.is_file() and aud_ext_pattrn.search(file_path.as_posix())]
    samples = [len(sf.read(w)[0]) for w in wavs]
    #print(wavs)
    root = os.path.abspath(os.path.split(wavs[0])[0])	
    wavs = [os.path.split(x)[-1] for x in wavs]

    wav2trans = dict()

    with open(p2root+'/'+folder+'/transcription.txt','r') as transcrip:
        lines = transcrip.read().strip().split('\n')
    for line in lines:
        if '\t' in line:
            file, trans = line.split("\t")
        else:
            splitted_line = line.split(" ")
            file, trans = splitted_line[0], " ".join(splitted_line[1:])
        wav2trans[file] = trans
        charset.update(trans.replace(" ","|"))
    

    with open(manifest+folder+".tsv",'w') as tsv, \
        open(manifest+folder+".wrd","w") as wrd, \
        open(manifest+folder+".ltr",'w') as ltr:
        print(root,file=tsv)
        for n,d in zip(wavs,samples):
            print(n,d,sep='\t',file=tsv)
            print(wav2trans[os.path.splitext(n)[0]],file=wrd)
            print(" ".join(list(wav2trans[os.path.splitext(n)[0]].replace(" ", "|"))) + " |", file=ltr)


with open(manifest+"dict.ltr.txt",'w') as dct:
    for e,c in enumerate(charset):
        print(c,e,file=dct)
