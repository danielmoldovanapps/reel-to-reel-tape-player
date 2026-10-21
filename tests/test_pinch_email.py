"""Regression checks: instant pinch release with independently finishing pitch spin-down."""
from pathlib import Path
import base64, subprocess, tempfile
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as work:
    tone=Path(work)/'tone.wav'
    subprocess.run(['ffmpeg','-nostdin','-loglevel','error','-f','lavfi','-i','sine=frequency=440:sample_rate=22050:duration=9', '-c:a','pcm_s16le','-y',str(tone)],check=True)
    audio_url='data:audio/wav;base64,'+base64.b64encode(tone.read_bytes()).decode()
    html=(ROOT/'index.html').read_text()
    for name in ('metadata-reader.js','tape-engine.js'):
        html=html.replace(f'<script src="{name}"></script>',f'<script>{(ROOT/name).read_text()}</script>')
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--autoplay-policy=no-user-gesture-required'])
        page=browser.new_page()
        errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
        page.set_content(html,wait_until='domcontentloaded')
        page.wait_for_function('window.__reel')
        page.evaluate('''(url)=>{const r=window.__reel;r.tracks.push({url,name:'tone.wav',title:'Tone',artist:'Test',album:'',dur:9});r.loadTrack(0,true)}''',audio_url)
        page.wait_for_timeout(680)
        def snap():
            return page.evaluate('''()=>{const r=window.__reel;return {pinch:r.S.pinch,state:r.S.state,paused:r.audio.paused,rate:r.audio.playbackRate}}''')
        first=snap(); print('Playing',first)
        assert first['state']=='play' and first['pinch']<3 and not first['paused'],first
        page.evaluate('window.__reel.pause()')
        paused=snap(); print('IMMEDIATELY AFTER PAUSE',paused)
        assert paused['state']=='pause' and paused['pinch']==9 and not paused['paused'],paused
        page.wait_for_timeout(1050)
        assert snap()['paused'] and snap()['pinch']==9,snap()
        page.evaluate('window.__reel.play()')
        page.wait_for_timeout(620)
        playing=snap();print('Resumed',playing)
        assert playing['state']=='play' and playing['pinch']<3 and not playing['paused'],playing
        page.evaluate('window.__reel.stop()')
        stopping=snap();print('IMMEDIATELY AFTER STOP',stopping)
        assert stopping['state']=='stop' and stopping['pinch']==9 and not stopping['paused'],stopping
        page.wait_for_timeout(1050)
        assert snap()['paused'] and snap()['pinch']==9,snap()
        page.evaluate('window.__reel.play()')
        page.wait_for_timeout(450)
        page.evaluate('window.__reel.startSpool(1)')
        winding=snap();print('IMMEDIATELY AFTER WIND',winding)
        assert winding['pinch']==9 and winding['state']=='ff',winding
        assert 'rodanielapps@yahoo.com' in page.locator('body').inner_text()
        assert not errors,errors
        browser.close()
print('PASS: pinch roller releases instantly, motor effects keep running, new email in interface')
