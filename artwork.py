# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Daniel Moldovan aka [RO]Daniel
# Contact: rodanielapps@yahoo.com
"""Read local embedded artwork, falling back to an album-folder image."""
from pathlib import Path
import base64
import sys
sys.path.insert(0, str(Path(__file__).parent / 'vendor'))
import mutagen
from mutagen.flac import Picture
from mutagen.id3 import ID3

MAX_ART = 16 * 1024 * 1024

def image_type(data):
    if data.startswith(b'\xff\xd8\xff'): return 'image/jpeg'
    if data.startswith(b'\x89PNG\r\n\x1a\n'): return 'image/png'
    if data.startswith((b'GIF87a', b'GIF89a')): return 'image/gif'
    if data.startswith(b'RIFF') and data[8:12] == b'WEBP': return 'image/webp'
    return None

def get_artwork(path):
    """Return (bytes, MIME) or None; never fetch remote artwork."""
    candidates = []
    try:
        audio = mutagen.File(path)
        tags = audio.tags if audio else None
        pictures = getattr(audio, 'pictures', [])
        candidates.extend((getattr(p, 'type', 0), p.data) for p in pictures)
        if tags is not None:
            if hasattr(tags, 'getall'):
                candidates.extend((getattr(p, 'type', 0), p.data) for p in tags.getall('APIC'))
            for cover in tags.get('covr', []):
                candidates.append((3, bytes(cover)))
            for encoded in tags.get('metadata_block_picture', []):
                if len(encoded) <= MAX_ART * 2:
                    p = Picture(base64.b64decode(encoded))
                    candidates.append((p.type, p.data))
            for encoded in tags.get('coverart', []):
                if len(encoded) <= MAX_ART * 2:
                    candidates.append((3, base64.b64decode(encoded)))
    except Exception:
        # ID3-only files can still contain usable covers even with damaged audio.
        try:
            candidates.extend((p.type, p.data) for p in ID3(path).getall('APIC'))
        except Exception:
            pass
    for _, data in sorted(candidates, key=lambda item: item[0] != 3):
        mime = image_type(data)
        if mime and len(data) <= MAX_ART:
            return data, mime
    folder = Path(path).parent
    try:
        by_name = {p.name.casefold(): p for p in folder.iterdir() if p.is_file()}
        for stem in ('cover', 'folder', 'front', 'artwork', 'album'):
            for ext in ('.jpg', '.jpeg', '.png', '.webp', '.gif'):
                p = by_name.get(stem + ext)
                if p and p.stat().st_size <= MAX_ART:
                    data = p.read_bytes()
                    mime = image_type(data)
                    if mime: return data, mime
    except OSError:
        pass
    return None
