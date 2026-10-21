# Reporting security problems

Please report suspected security vulnerabilities privately to the project
owner at **rodanielapps@yahoo.com**. Include the version, distribution, package
format, reproduction steps and potential impact. Avoid public exploit details
until the owner has had an opportunity to investigate.

General playback or UI bugs can be filed in repository Issues.

The application runs a localhost-only HTTP service with a per-launch random
token and uses WebKitGTK/GStreamer to process media. Keep the operating system
and runtime dependencies updated. Package sandboxing and code review reduce
risk but do not guarantee that an application or contribution is safe.
