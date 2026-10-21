# Reel-to-Reel Tape Player

A vintage-inspired music player for Linux with animated tape reels, needle VU
meters, LED level meters, album artwork, persistent playlists, and customizable
deck and reel branding.

Supports music from your computer and accessible mounted network locations.
Tape-style transport changes both speed and pitch during braking, starting,
and winding. The current application version is **1.3.0**.

Proudly made by Daniel Moldovan, aka [RO]Daniel, from Brasov-Romania.

## Run from source on Debian 13 / Ubuntu

```bash
sudo apt install python3 python3-gi gir1.2-gtk-3.0 gir1.2-webkit2-4.1 ffmpeg zenity gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-libav
bash AppRun
```

Open a folder from the player, or provide audio files as arguments:

```bash
bash AppRun /path/to/song.flac
```

The interface runs in WebKitGTK inside a GTK3 desktop window. Playback uses
Web Audio, with GStreamer providing WebKit's audio decoding. A token-protected
HTTP backend listens on a random localhost port. Python and WebKitGTK are
required; this is not a native Cairo/GStreamer interface rewrite.

## Features

- MP3, FLAC, OGG/Opus, WAV and M4A/AAC playback, subject to installed codecs.
- Synchronized tape animation, braking and startup effects.
- Reverse-sample winding and fast-forward at reduced transport volume.
- Embedded/folder artwork and track information.
- Playlist, volume, repeat/shuffle and custom branding persistence.
- Single-instance file-manager integration.
- Keyboard shortcuts documented in the app's About window.

Long or high-resolution files may require substantial RAM because the transport
engine decodes audio to PCM, with additional buffers for reverse playback.
Network locations must be accessible as filesystem paths; this is not a
Spotify/Deezer streaming-service client.

## Build packages

### Debian installer

```bash
python3 build.py --output dist
sudo apt install ./dist/reelplayer_1.3.0_all.deb
```

### Snap

```bash
snapcraft pack
```

The Snap recipe uses `core24`, the GNOME extension, and system-provided Python
from the base. It includes the fixes used during the desktop testing of the
first Store submission. A build and desktop test are still required whenever
the source or packaging changes. Publication is controlled by the project owner.

### AppImage

```bash
python3 build-appimage.py --output dist
```

This lightweight AppImage uses **host Python/GTK/WebKitGTK dependencies** and is
not a dependency-free portable installer. Do not advertise it as working on
all distributions without prerequisites.

### Flatpak

A direct-distribution Flatpak candidate is being tested separately. This
repository intentionally does not supply a Flathub submission manifest.
Contributors interested in Flathub packaging should read CONTRIBUTING.md and
AI-ASSISTANCE.md and independently follow Flathub's current requirements.

## Contributing and ownership

Contributions are welcome through forks and pull requests. The project owner
reviews and approves changes and controls upstream releases. Contributions do
not require write access to this repository. See CONTRIBUTING.md.

The project was developed with substantial AI assistance. See AI-ASSISTANCE.md
for the affected areas and packaging/submission considerations.

## Support and donations

Report reproducible bugs through this repository's Issues after it is published.
Contact: rodanielapps@yahoo.com

If you like the app, please consider donating to the developer:
[PayPal](https://www.paypal.me/danielmoldovanapps).
The application also contains the owner's existing optional crypto donation
addresses. Donations are never required to use the player.

## License

First-party application code is distributed under **GPL-3.0-only**. Bundled
third-party software retains its own licenses. See LICENSE, COPYRIGHT,
THIRD-PARTY-NOTICES.txt and metadata-reader-LICENSES.txt.
