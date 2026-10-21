from pathlib import Path
from playwright.sync_api import sync_playwright
from http.server import ThreadingHTTPServer
import threading, tempfile, subprocess, runpy, os, math, sys, base64
sys.path.insert(0,str(Path(__file__).parent/'reel-to-reel-tape-player-1.3.0'))
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
    song=Path(tmp)/'440.wav'
    subprocess.run(['ffmpeg','-loglevel','error','-f','lavfi','-i','sine=frequency=440:sample_rate=44100:duration=40','-c:a','pcm_s16le','-y',str(song)],check=True)
    ns=runpy.run_path(str(root/'reelplayer'))
    ns['FILES'].append((str(song.parent),str(song)))
    server=ThreadingHTTPServer(('127.0.0.1',0),ns['H']);server.daemon_threads=True
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--autoplay-policy=no-user-gesture-required'])
        page=browser.new_page()
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        html=(root/'index.html').read_text()
        html=html.replace('<script src="metadata-reader.js"></script>','<script>'+ (root/'metadata-reader.js').read_text()+'</script>')
        html=html.replace('<script src="tape-engine.js"></script>','<script>'+ (root/'tape-engine.js').read_text()+'</script>')
        page.set_content(html,wait_until='domcontentloaded')
        page.wait_for_function('window.__reel',timeout=15000)
        data='data:audio/wav;base64,'+base64.b64encode(song.read_bytes()).decode()
        page.evaluate("(data)=>{const r=window.__reel;r.tracks.push({file:null,url:data,name:'440.wav',title:'440Hz Test',artist:'Test',album:'',dur:40});}",data)
        # Real WebAudio PCM signal: verify transport engine pitch in offline render.
        result=page.evaluate('''async () => {
          const rates=[0.5,1,2,3], out=[];
          for(const r of rates){
            const sr=44100;
            const ctx=new OfflineAudioContext(1,sr,sr);
            const tape=new TapeAudio();tape.setAudioContext(ctx);
            const data=ctx.createBuffer(1,sr,sr), ch=data.getChannelData(0);
            for(let i=0;i<ch.length;i++)ch[i]=Math.sin(2*Math.PI*440*i/sr);
            tape._buffer=data;tape._paused=false;tape.playbackRate=r;
            tape.connect(ctx.destination);tape._startSource();
            const rendered=await ctx.startRendering(), samples=rendered.getChannelData(0);
            let crossings=0;for(let i=2000;i<13000;i++)if(samples[i-1]<0&&samples[i]>=0)crossings++;
            out.push([r, crossings*sr/11000]);
          }
          return out;
        }''')
        print('ACTUAL RENDERED PITCHES',result)
        for rate,pitch in result:assert abs(pitch-rate*440)<rate*40,(rate,pitch)
        page.evaluate('window.__reel.loadTrack(0,true)')
        page.wait_for_timeout(1200)
        def snap():return page.evaluate('''() => {const r=window.__reel;return {state:r.S.state,paused:r.audio.paused,rate:r.audio.playbackRate,time:r.audio.currentTime,duration:r.audio.duration,direction:r.audio.direction,reels:r.S.om,buffer:!!r.audio._buffer}}''')
        print('start',snap())
        assert snap()['buffer'] and snap()['state']=='play' and not snap()['paused']
        page.evaluate('window.__reel.pause()')
        page.wait_for_timeout(1050)
        s=snap();print('pause',s);assert s['paused'] and s['state']=='pause' and s['reels']==[0,0],s
        page.evaluate('window.__reel.play()')
        page.wait_for_timeout(1050)
        s=snap();print('resume',s);assert not s['paused'] and .9<=s['rate']<=1.02,s
        page.evaluate('window.__reel.audio.currentTime=25')
        page.wait_for_timeout(150)
        page.evaluate('window.__reel.startSpool(1)')
        page.wait_for_timeout(1050)
        s=snap();print('ff',s);assert s['state']=='ff' and s['rate']==3 and s['direction']==1,s
        page.evaluate('window.__reel.startSpool(-1)')
        page.wait_for_timeout(1250)
        s=snap();print('rew',s);assert s['state']=='rew' and s['rate']==3 and s['direction']==-1,s
        page.evaluate('window.__reel.startSpool(-1)')
        page.wait_for_timeout(1080)
        s=snap();print('from rewind',s);assert s['state']=='play' and s['direction']==1 and s['rate']==1,s
        page.evaluate('window.__reel.stop()')
        page.wait_for_timeout(1100)
        s=snap();print('stop',s);assert s['paused'] and s['time']==0 and s['reels']==[0,0],s
        for cycle in range(4):
            page.evaluate('window.__reel.play()')
            page.wait_for_timeout(100)
            page.evaluate('window.__reel.pause()')
            page.wait_for_timeout(80)
            page.evaluate('window.__reel.startSpool(1)')
            page.wait_for_timeout(120)
            page.evaluate('window.__reel.startSpool(-1)')
            page.wait_for_timeout(120)
            page.evaluate('window.__reel.stop()')
            page.wait_for_timeout(950)
            ss=snap();assert ss['state']=='stop' and ss['paused'] and ss['time']==0 and ss['reels']==[0,0],ss
        print('rapid transport test: 4 cycles passed')
        print('JS ERRORS',errors)
        assert not errors,errors
        browser.close()
    server.shutdown();server.server_close()
