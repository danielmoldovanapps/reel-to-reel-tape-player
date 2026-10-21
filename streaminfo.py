# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Daniel Moldovan aka [RO]Daniel
# Contact: rodanielapps@yahoo.com
"""Read source-track properties, independent of the playback device rate."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent / 'vendor'))
import mutagen

def get_track_info(path):
    ext=Path(path).suffix.lstrip('.').upper()
    result={'format':ext or 'AUDIO'}
    try:
        track=mutagen.File(path)
        if not track:return result
        info=track.info;name=type(track).__name__
        format_names={'MP3':'MP3','FLAC':'FLAC','WAVE':'WAV','AAC':'AAC','OggVorbis':'OGG/VORBIS','OggOpus':'OGG/OPUS','OggFLAC':'OGG/FLAC','AIFF':'AIFF'}
        result['format']=format_names.get(name,ext or name.upper())
        if name=='MP4':
            codec=str(getattr(info,'codec','')).lower()
            result['format']='M4A/ALAC' if 'alac' in codec else 'M4A/AAC' if 'mp4a' in codec else 'M4A'
        for field in ('bitrate','sample_rate','channels','bits_per_sample'):
            value=getattr(info,field,None)
            if isinstance(value,(int,float)) and value>0:result[field]=round(value)
        if name=='OggOpus':result['sample_rate']=48000
        mode=str(getattr(info,'bitrate_mode','')).rsplit('.',1)[-1]
        if mode in ('CBR','VBR','ABR'):result['bitrate_mode']=mode
        elif mode=='UNKNOWN':result['estimated_bitrate']=True
    except Exception:
        pass
    return result
