# Historical source snapshots

This project has source snapshots predating its first GitHub upload. These were supplied by the project owner on 2026-10-21 and inspected as ZIP archives. They are **not evidence of earlier public Git releases**, and archive member dates are **unverified metadata**, not authenticated commit or release dates. Several archives share a version label but differ in source content.

| Supplied snapshot | Main `index.html` SHA-256 prefix | ZIP member date(s) |
| --- | --- | --- |
| `reelplayer-source(1).zip` (README: 1.1.2 patch) | `83ea4ece7c7f` | 2026-10-12 |
| `reelplayer-source-1.2.0.zip` | `e86ca5384086` | 2026-10-12 |
| `reelplayer-source-1.2.4.zip` | `e925b69f4bd8` | 2026-10-12 |
| `reelplayer-source-1.2.5.zip` | `369d13ca5656` | 2026-10-12 |
| `reelplayer-source-1.2.7(1).zip` | `572978dadd32` | 2026-10-12 |
| `reelplayer-source-1.2.9(2).zip` | `d994877897c0` | 2026-10-12 |
| `reelplayer-source-1.2.9 Final.zip` | `68385affade8` | 2026-10-12 to 2026-10-13 |
| `reelplayer-source-1.2.9-reel-sync(3).zip` | `91a647496802` | 2026-10-13 |
| `Reel-to-Reel-Tape-Player-1.3.0 source code(1).zip` | `806fc95a76c1` | 2026-10-14 |
| `Reel-to-Reel-Tape-Player-1.3.0.zip` (README: WebKitGTK edition) | `90d2c50f9350` | 2026-10-14 |

Each main application HTML file listed above has a different SHA-256 digest. Some older archives contain Flatpak-related source or build files, but this does **not** imply a Flathub submission or approval. Earlier builds used differing browser integration approaches; the precise architecture should be checked in each archive. The current GitHub 1.3.0 source is a later snapshot, not a reconstructed historical commit.

These ZIP files are **not being presented as release tags or retroactively dated Git commits**. They are retained separately for future independent review, including license and privacy review before any public archival distribution.

## Future practice

From this point forward, maintain normal dated Git commits; publish real, tagged releases with changelogs; preserve tests and build evidence; and document real feedback and maintenance activity. Do not fabricate commit history or imply that a snapshot was publicly published when it was not.
