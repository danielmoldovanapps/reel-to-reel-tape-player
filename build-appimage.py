#!/usr/bin/env python3
# Self-extracting SquashFS AppImage using system WebKitGTK.
# Runtime and SquashFS writer included in build-support/.
from pathlib import Path
import argparse,shutil,subprocess,tarfile,os
root=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',default='dist');a=p.parse_args()
out=Path(a.output).resolve();out.mkdir(exist_ok=True,parents=True)
stage=out/'build/appimage';shutil.rmtree(stage,ignore_errors=True);stage.mkdir(parents=True)
inner=stage/'payload/app';inner.mkdir(parents=True)
for name in ('reelplayer','AppRun','index.html','tape-engine.js','artwork.py','streaminfo.py','metadata-reader.js',
             'metadata-reader-LICENSES.txt','icon.svg','README.md','donation-qr.png',
             'STORE-DESCRIPTION.md','LICENSE','COPYRIGHT','THIRD-PARTY-NOTICES.txt',
             'crypto-donations','vendor'):
    src=root/name;dst=inner/name
    if src.is_dir():shutil.copytree(src,dst)
    else:shutil.copy2(src,dst)
for name in ('reelplayer','AppRun'):(inner/name).chmod(0o755)
appdir=stage/'AppDir';appdir.mkdir()
with tarfile.open(appdir/'payload.tar.gz','w:gz') as tar:tar.add(stage/'payload/app',arcname='app')
shutil.copy2(root/'icon.svg',appdir/'reelplayer.svg')
shutil.copy2(root/'reelplayer.desktop',appdir/'reelplayer.desktop')
shutil.copy2(root/'build-support/AppRun',appdir/'AppRun');(appdir/'AppRun').chmod(0o755)
subprocess.run(['python3',str(root/'build-support/make_sqfs.py'),str(appdir),str(stage/'app.squashfs')],check=True)
runtime=stage/'runtime'
subprocess.run(['gcc','-Os',str(root/'build-support/appimage_runner.c'),'-o',str(runtime)],check=True)
img=out/'Reel-to-Reel-Tape-Player-1.3.0-WebKitGTK-x86_64.AppImage'
with img.open('wb') as dst:
    with runtime.open('rb') as f:shutil.copyfileobj(f,dst)
    padding=(-img.stat().st_size)%4096
    dst.write(b'\0'*padding)
    with (stage/'app.squashfs').open('rb') as f:shutil.copyfileobj(f,dst)
img.chmod(0o755)
print(img)
