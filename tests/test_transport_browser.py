from pathlib import Path
import base64
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'index.html'
import tempfile,subprocess
with tempfile.NamedTemporaryFile(suffix='.ogg',delete=False) as f: TEST_TONE=Path(f.name)
subprocess.run(['ffmpeg','-loglevel','error','-f','lavfi','-i','sine=frequency=440:sample_rate=44100:duration=45','-c:a','libvorbis','-q:a','1','-y',str(TEST_TONE)],check=True)
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--autoplay-policy=no-user-gesture-required'])
    page=browser.new_page()
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    html=HTML.read_text().replace('<script src="metadata-reader.js"></script>', '<script>'+ (HTML.parent/'metadata-reader.js').read_text()+'</script>')
    page.set_content(html,wait_until='domcontentloaded')
    page.wait_for_timeout(500)
    assert page.evaluate('!!window.__reel'),errors
    song='data:audio/ogg;base64,'+base64.b64encode(TEST_TONE.read_bytes()).decode()
    page.evaluate('''(song) => {const r=window.__reel;
      r.tracks.push({file:null,url:song,name:'test.ogg',title:'Test',artist:'Test Artist',album:'',dur:45});
      r.loadTrack(0,false);
    }''',song)
    page.wait_for_timeout(400)
    page.evaluate('window.__reel.play()')
    page.wait_for_timeout(1200)
    def snap():return page.evaluate('''() => {const r=window.__reel;return {state:r.S.state,paused:r.audio.paused,rate:r.audio.playbackRate,time:r.audio.currentTime,reels:r.S.om,volume:r.audio.volume}}''')
    print('start',snap())
    page.evaluate('window.__reel.pause()')
    page.wait_for_timeout(850)
    s=snap(); print('pause',s); assert s['state']=='pause' and s['paused'] and s['reels']==[0,0],s
    page.evaluate('window.__reel.play()')
    page.wait_for_timeout(1100)
    s=snap();print('resume',s);assert s['state']=='play' and not s['paused'] and 0.9<=s['rate']<=1.01,s
    page.evaluate('window.__reel.audio.currentTime=25')
    page.wait_for_timeout(300)
    page.evaluate('window.__reel.startSpool(1)')
    page.wait_for_timeout(950)
    s=snap();print('ff',s); assert s['state']=='ff' and 1.9<=s['rate']<=2.01 and not s['paused'],s
    assert abs(page.evaluate('transportVolume')-0.5)<0.001
    page.evaluate('window.__reel.startSpool(-1)')
    page.wait_for_timeout(1200)
    s=snap();print('rew',s);assert s['state'] in ['rew','play'] and 0.6<=s['rate']<=2,s
    page.evaluate('window.__reel.pause()')
    page.wait_for_timeout(160)
    s=snap();print('pause after rewind',s);assert s['state']=='pause' and s['paused'] and s['reels']==[0,0],s
    page.evaluate('window.__reel.play()')
    page.wait_for_timeout(350)
    page.evaluate('window.__reel.stop()')
    page.wait_for_timeout(850)
    s=snap();print('stop',s);assert s['state']=='stop' and s['paused'] and s['reels']==[0,0] and s['time']==0,s
    for _ in range(3):
        page.evaluate('window.__reel.play()')
        page.wait_for_timeout(90)
        page.evaluate('window.__reel.pause()')
        page.wait_for_timeout(90)
        page.evaluate('window.__reel.stop()')
        page.wait_for_timeout(720)
        s=snap();assert s['state']=='stop' and s['paused'] and s['reels']==[0,0],s
    print('Rapid-transport cycles: PASS')
    print('ERRORS',errors[:6]);assert not errors,errors
    browser.close()

TEST_TONE.unlink(missing_ok=True)
