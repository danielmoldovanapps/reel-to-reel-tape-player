"""Volume persisted by the app's localhost API across server-port changes."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
from http.server import ThreadingHTTPServer
from importlib.machinery import SourceFileLoader
from urllib.request import Request, urlopen
from urllib.error import HTTPError

root=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
loader=SourceFileLoader('reelplayer_module_for_test',str(root/'reelplayer'))
spec=importlib.util.spec_from_loader(loader.name,loader)
mod=importlib.util.module_from_spec(spec)
loader.exec_module(mod)

with tempfile.TemporaryDirectory() as d:
    old=os.environ.get('XDG_CONFIG_HOME')
    os.environ['XDG_CONFIG_HOME']=d
    try:
        assert mod.read_preferences()=={'vol':1.0,'repeat':0,'shuffle':False}
        for idx in (0,1):
            server=ThreadingHTTPServer(('127.0.0.1',0),mod.H)
            th=threading.Thread(target=server.serve_forever,daemon=True)
            th.start()
            url=f'http://127.0.0.1:{server.server_port}/api/prefs?k={mod.TOKEN}'
            with urlopen(url) as response:
                data=json.load(response)
            assert data['vol']==(1.0 if idx==0 else 0.37),data
            if idx==0:
                payload=json.dumps({'vol':0.37,'repeat':2,'shuffle':True}).encode()
                req=Request(url,data=payload,headers={'Content-Type':'application/json'},method='POST')
                with urlopen(req) as response: assert response.status==204
                assert mod.read_preferences()=={'vol':0.37,'repeat':2,'shuffle':True}
            server.shutdown();server.server_close();th.join(timeout=3)
        # Malformed value must not overwrite saved volume.
        for bad in ({'vol':2},{'vol':'nope'},{'vol':float('nan')}):
            try: mod.write_preferences(bad)
            except ValueError: pass
            else: raise AssertionError(f'Invalid preference accepted: {bad}')
        assert mod.read_preferences()['vol']==0.37
        print('PASS: new install defaults to max; a user change persists through new localhost ports')
    finally:
        if old is None: os.environ.pop('XDG_CONFIG_HOME',None)
        else: os.environ['XDG_CONFIG_HOME']=old
