# Preparation checks

- Application source files match the latest tested 1.3.0 smooth-braking / LED-clipping application.
- Python syntax checked.
- Debian package rebuilt successfully from this repository layout.
- Snap staging script tested with repository-root sources; application assets match.
- No private-key blocks or common GitHub/AWS credential token patterns detected. This is not a comprehensive security audit.

The adjusted repository-root Snap recipe still needs a complete sandbox build
before release. This preparation does not repeat the previous desktop tests.
No GitHub repository, release, branch protection, collaborator access or
Flathub submission has been created. Source assets and notices are retained.
