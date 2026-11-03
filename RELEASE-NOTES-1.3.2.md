# Reel-to-Reel Tape Player 1.3.2

This release matches the tested and published **Snap Store stable 1.3.2, revision 3** (same application source, separately packaged for each format).

## Changes since 1.3.1

- Restored functional **Network** and **Other Locations** selection in the strictly confined Snap by using GTK's native file chooser and the desktop portal. The ordinary native Linux packages retain their desktop chooser.
- The analogue VU needle meters now say **LEVEL** instead of PEAK, reflecting their intentionally smooth, tape-deck-style motion. The independent LED strip remains a peak-level display.
- The About dialog shows **Version 1.3.2**.
- Retains the smoother VU needle behavior, local/network music playback, playlist persistence, and customizable artwork and branding.

## Downloads

- **Debian / Ubuntu:** `reelplayer_1.3.2_all.deb` — native system-dependent Debian package, installed via `sudo apt install ./reelplayer_1.3.2_all.deb`.
- **AppImage (x86_64):** `Reel-to-Reel-Tape-Player-1.3.2-WebKitGTK-x86_64.AppImage` — lightweight extract-and-run image. Requires the host system's Python 3, GTK3, PyGObject, WebKitGTK **4.1**, GStreamer and codecs; **not a self-contained AppImage**. Mark executable and launch it.
- **Fedora-oriented RPM (noarch):** `reelplayer-1.3.2-1.noarch.rpm` — contains architecture-independent Python and application assets but **requires Fedora's host packages**, including GTK3, PyGObject and WebKitGTK 4.1. Install with `sudo dnf install ./reelplayer-1.3.2-1.noarch.rpm`. Some codecs and FFmpeg may require additional packages/repositories. RPM-family distributions have different dependency names; openSUSE and others have **not been verified**.
- **Snap Store:** [Reel-to-Reel Tape Player](https://snapcraft.io/reel-to-reel-tape-player) — `sudo snap install reel-to-reel-tape-player` gives the tested 1.3.2 stable release.
- `SHA256SUMS` — checksums of all three GitHub binaries.

Automated checks verify the Linux packages' metadata and that each contains the final matching `index.html`, plus basic Python and JavaScript syntax and native-chooser regression tests. The native Linux downloads and Fedora RPM are **not claimed to be desktop-tested on every distribution**; please report reproducible problems in GitHub Issues.

All first-party code is GPL-3.0-only; bundled third-party components retain their licenses.
