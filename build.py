#!/usr/bin/env python3
# Build Chromium-free GTK3/WebKit2 Debian package.
import shutil, subprocess, argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--output',default='dist');args=parser.parse_args()
out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
root=out/'build'/'debian-reelplayer'
if root.exists():shutil.rmtree(root)
app=root/'usr/share/reelplayer';app.mkdir(parents=True)
assets=('reelplayer','AppRun','index.html','tape-engine.js','artwork.py','streaminfo.py',
        'metadata-reader.js','metadata-reader-LICENSES.txt','icon.svg',
        'README.md','donation-qr.png','STORE-DESCRIPTION.md','LICENSE','COPYRIGHT',
        'THIRD-PARTY-NOTICES.txt','crypto-donations','vendor','third_party')
for name in assets:
    src=ROOT/name;dest=app/name
    if src.is_dir():shutil.copytree(src,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    else:shutil.copy2(src,dest)
for name in ('reelplayer','AppRun'):(app/name).chmod(0o755)
bin=root/'usr/bin/reelplayer';bin.parent.mkdir(parents=True)
bin.write_text('#!/bin/sh\nexec /usr/share/reelplayer/AppRun "$@"\n');bin.chmod(0o755)
entry=root/'usr/share/applications/reelplayer.desktop';entry.parent.mkdir(parents=True)
shutil.copy2(ROOT/'reelplayer.desktop',entry)
icon=root/'usr/share/icons/hicolor/scalable/apps/reelplayer.svg';icon.parent.mkdir(parents=True)
shutil.copy2(ROOT/'icon.svg',icon)
license_dest=root/'usr/share/doc/reelplayer/copyright';license_dest.parent.mkdir(parents=True)
shutil.copy2(ROOT/'debian/copyright',license_dest)
debian=root/'DEBIAN';debian.mkdir();debian.chmod(0o755)
installed=sum(p.stat().st_size for p in root.rglob('*') if p.is_file())//1024+1
(debian/'control').write_text(f'''Package: reelplayer
Version: 1.3.0
Section: sound
Priority: optional
Architecture: all
Maintainer: Daniel Moldovan aka [RO]Daniel <rodanielapps@yahoo.com>
Installed-Size: {installed}
Depends: ffmpeg, python3 (>= 3.9), python3-gi, gir1.2-gtk-3.0, gir1.2-webkit2-4.1, gstreamer1.0-plugins-base, gstreamer1.0-plugins-good
Recommends: gstreamer1.0-plugins-bad, gstreamer1.0-libav, zenity | kdialog, desktop-file-utils
Description: Reel-to-Reel Tape Player
 Vintage animated reel deck and VU meters with native WebKitGTK window.
 Single-instance file manager integration with automatic playback.
 Customizable branding, playlist persistence and artwork.
 Proudly made by Daniel Moldovan, aka [RO]Daniel, from Brasov-Romania.
''')
for name in ('postinst','postrm'):
    f=debian/name;f.write_text('#!/bin/sh\nset -e\nif command -v update-desktop-database >/dev/null 2>&1; then update-desktop-database -q /usr/share/applications || true; fi\nexit 0\n');f.chmod(0o755)
file=out/'reelplayer_1.3.0_all.deb'
subprocess.run(['dpkg-deb','--root-owner-group','--build',str(root),str(file)],check=True)
print(file)
