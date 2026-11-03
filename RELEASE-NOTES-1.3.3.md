# Reel-to-Reel Tape Player 1.3.3

This release uses the same application source as **Snap Store stable 1.3.3, revision 4**, with separate package builds for each format. The 1.3.3 network fallback worked on the maintainer's Debian machine; **the original Ubuntu Live issue has not yet been retested**.

## Changes since 1.3.2

- Improved **Ubuntu Live** and installed Snap network-media handling: when the GTK desktop portal returns a network folder or file path that is unreadable, the player offers a second native chooser rooted in the actual GVFS mounts. This addresses an Ubuntu Live regression and still needs direct testing on that environment.
- Preserves native desktop file selection for .deb, AppImage, and RPM packages.
- Preserves the analogue **LEVEL** needle meter label and smoothly damped motion. The independent LED strip retains its peak-level indicator.
- The About dialog shows **Version 1.3.3**.
- Retains the smoother VU needle behavior, local/network music playback, playlist persistence, and customizable artwork and branding.

## Downloads

- **Debian / Ubuntu:** `reelplayer_1.3.3_all.deb` — native system-dependent Debian package, installed via `sudo apt install ./reelplayer_1.3.3_all.deb`.
- **AppImage (x86_64):** `Reel-to-Reel-Tape-Player-1.3.3-WebKitGTK-x86_64.AppImage` — lightweight extract-and-run image. Requires the host system's Python 3, GTK3, PyGObject, WebKitGTK **4.1**, GStreamer and codecs; **not a self-contained AppImage**. Mark executable and launch it.
- **Fedora-oriented RPM (noarch):** `reelplayer-1.3.3-1.noarch.rpm` — contains architecture-independent Python and application assets but **requires Fedora's host packages**, including GTK3, PyGObject and WebKitGTK 4.1. Install with `sudo dnf install ./reelplayer-1.3.3-1.noarch.rpm`. Some codecs and FFmpeg may require additional packages/repositories. RPM-family distributions have different dependency names; openSUSE and others have **not been verified**.
- **Snap Store:** [Reel-to-Reel Tape Player](https://snapcraft.io/reel-to-reel-tape-player) — `sudo snap install reel-to-reel-tape-player` gives the tested 1.3.3 stable release.
- `SHA256SUMS` — checksums of all three GitHub binaries.

Automated checks verify the Linux packages' metadata and that each contains the final matching `index.html`, plus basic Python and JavaScript syntax and native-chooser regression tests. The native Linux downloads and Fedora RPM are **not claimed to be desktop-tested on every distribution**; please report reproducible problems in GitHub Issues.

All first-party code is GPL-3.0-only; bundled third-party components retain their licenses.
