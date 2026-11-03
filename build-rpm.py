#!/usr/bin/env python3
"""Build a Fedora-oriented, host-dependent RPM from the exact current source.

The player is written in Python and uses system GTK3/WebKitGTK/GStreamer; this
RPM contains application files only, not a bundled WebKit engine. The RPM's
runtime dependency names target Fedora, not openSUSE's differing package names.
"""
import argparse
import re
import shutil
import subprocess
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
version_match = re.search(r"^version:\s*'([^']+)'", (ROOT / 'snap/snapcraft.yaml').read_text(), re.M)
if version_match is None:
    raise SystemExit('Cannot determine application version from snap/snapcraft.yaml')
VERSION = version_match.group(1)
parser = argparse.ArgumentParser()
parser.add_argument('--output', default='dist')
args = parser.parse_args()

out = Path(args.output).resolve()
out.mkdir(parents=True, exist_ok=True)
top = out / 'build' / 'rpmbuild'
if top.exists():
    shutil.rmtree(top)
for directory in ('SOURCES', 'SPECS', 'BUILD', 'BUILDROOT', 'RPMS', 'SRPMS'):
    (top / directory).mkdir(parents=True, exist_ok=True)

source_root = top / 'source' / ('reelplayer-' + VERSION)
app = source_root / 'usr/share/reelplayer'
app.mkdir(parents=True)
assets = (
    'reelplayer', 'AppRun', 'index.html', 'tape-engine.js',
    'artwork.py', 'streaminfo.py', 'metadata-reader.js',
    'metadata-reader-LICENSES.txt', 'icon.svg', 'README.md',
    'donation-qr.png', 'STORE-DESCRIPTION.md', 'LICENSE', 'COPYRIGHT',
    'THIRD-PARTY-NOTICES.txt', 'crypto-donations', 'vendor', 'third_party'
)
for name in assets:
    source, destination = ROOT / name, app / name
    if source.is_dir():
        shutil.copytree(source, destination,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    else:
        shutil.copy2(source, destination)
for name in ('reelplayer', 'AppRun'):
    (app / name).chmod(0o755)

launcher = source_root / 'usr/bin/reelplayer'
launcher.parent.mkdir(parents=True)
launcher.write_text('#!/bin/sh\nexec /usr/share/reelplayer/AppRun "$@"\n')
launcher.chmod(0o755)
desktop = source_root / 'usr/share/applications/reelplayer.desktop'
desktop.parent.mkdir(parents=True)
shutil.copy2(ROOT / 'reelplayer.desktop', desktop)
icon = source_root / 'usr/share/icons/hicolor/scalable/apps/reelplayer.svg'
icon.parent.mkdir(parents=True)
shutil.copy2(ROOT / 'icon.svg', icon)

archive = top / 'SOURCES' / ('reelplayer-' + VERSION + '.tar.gz')
with tarfile.open(archive, 'w:gz') as tar:
    tar.add(source_root, arcname=source_root.name)

spec = """Name:           reelplayer
Version:        __VERSION__
Release:        1
Summary:        Vintage reel-to-reel tape player for Linux
License:        GPL-3.0-only
URL:            https://github.com/danielmoldovanapps/reel-to-reel-tape-player
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch
Requires:       python3 >= 3.9
Requires:       python3-gobject
Requires:       gtk3
Requires:       webkit2gtk4.1
Requires:       gstreamer1-plugins-base
Requires:       gstreamer1-plugins-good
Recommends:     ffmpeg
Recommends:     zenity

%description
A vintage-style audio player with animated tape reels, analogue VU meters,
LED peak-level meters, custom branding, and local and network music playback.
Uses system Python, GTK3, WebKitGTK 4.1, and GStreamer.

%prep
%setup -q

%build

%install
mkdir -p %{buildroot}/usr
cp -a usr/. %{buildroot}/usr/

%files
/usr/bin/reelplayer
/usr/share/reelplayer
/usr/share/applications/reelplayer.desktop
/usr/share/icons/hicolor/scalable/apps/reelplayer.svg

%changelog
* Tue Nov 03 2026 Daniel Moldovan <rodanielapps@yahoo.com> - __VERSION__-1
- Package 1.3.3 with Ubuntu GVFS portal fallback and LEVEL VU labels
""".replace('__VERSION__', VERSION)
spec_path = top / 'SPECS/reelplayer.spec'
spec_path.write_text(spec)

subprocess.run(['rpmbuild', '--define', '_topdir ' + str(top), '-bb',
                str(spec_path)], check=True)
built = top / 'RPMS/noarch' / ('reelplayer-' + VERSION + '-1.noarch.rpm')
if not built.is_file():
    raise SystemExit('Expected RPM missing: ' + str(built))
destination = out / built.name
shutil.copy2(built, destination)
print(destination)
