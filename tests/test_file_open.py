from pathlib import Path
import runpy, tempfile, threading, json, urllib.request, socket
p=Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0,str(p))
namespace=runpy.run_path(str(p/'reelplayer'),run_name='test_reel')
open_file=namespace['add_external_paths']
code=open_file.__globals__
with tempfile.TemporaryDirectory() as d:
    song=Path(d)/'Artist - Song.flac';song.write_bytes(b'fLaC')
    track2=Path(d)/'Artist - Second.mp3';track2.write_bytes(b'ID3')
    one=open_file([str(song)])
    assert one['play']==0 and len(one['tracks'])==1 and len(code['FILES'])==1
    again=open_file([str(song)])
    assert again['play']==0 and again['tracks']==[] and len(code['FILES'])==1
    two=open_file([str(track2)])
    assert two['play']==1 and len(code['FILES'])==2
    # The frontend reads these events by token-authenticated HTTP polling.
    Server=namespace['ThreadingHTTPServer']; Handler=namespace['H']
    http=Server(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=http.serve_forever,daemon=True);thread.start()
    url=f'http://127.0.0.1:{http.server_port}/api/open-events?k={namespace["TOKEN"]}'
    try:
        with urllib.request.urlopen(url) as res: events=json.load(res)
        assert len(events)==3 and [ev['play'] for ev in events]==[0,0,1],events
        with urllib.request.urlopen(url) as res: assert json.load(res)==[]
        with urllib.request.urlopen(url.replace('/api/open-events','/api/library')) as res:
            data=json.load(res);assert len(data['tracks'])==2
        try:
            urllib.request.urlopen(url.split('?')[0]+'?k=incorrect')
        except urllib.error.HTTPError as e: assert e.code==403
        else:raise AssertionError('Unauthenticated HTTP events allowed')
    finally:
        http.shutdown();http.server_close();thread.join(3)
print('PASS: duplicate open deduped, events deliver correct autoplay IDs, token enforced')
