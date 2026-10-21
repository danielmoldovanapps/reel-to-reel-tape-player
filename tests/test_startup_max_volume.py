"""Checks GTK startup and browser preferences after older saved volume values."""
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
shell=(root/'reelplayer').read_text()
assert 'self.window.maximize()' in shell
html=(root/'index.html').read_text()
shim='''<script>
window.__stored={'reel.prefs':JSON.stringify({vol:0.12,repeat:2,shuffle:true}),'reel.legal-notice':'GPL-3.0-only-Daniel-Moldovan-2026'};
Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>window.__stored[k]||null,setItem:(k,v)=>{window.__stored[k]=v}}});
</script>'''
html=html.replace('<script src="metadata-reader.js"></script>',shim+'<script>'+(root/'metadata-reader.js').read_text()+'</script>')
html=html.replace('<script src="tape-engine.js"></script>','<script>'+(root/'tape-engine.js').read_text()+'</script>')
with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
  page=browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.set_content(html,wait_until='domcontentloaded');page.wait_for_function('window.__reel')
  assert abs(page.evaluate('window.__reel.S.vol')-.12)<.001, 'Saved volume must be restored'
  assert page.evaluate('window.__reel.S.repeat')==2
  assert page.evaluate('window.__reel.S.shuffle') is True
  page.keyboard.press('ArrowDown')
  assert abs(page.evaluate('window.__reel.S.vol')-.07)<.001
  assert abs(page.evaluate('JSON.parse(window.__stored["reel.prefs"]).vol')-.07)<.001
  assert not errors,errors
  # A brand-new user has no stored preference and starts at 100%.
  page2=browser.new_page();errors2=[];page2.on('pageerror',lambda e:errors2.append(str(e)))
  fresh=html.replace("'reel.prefs':JSON.stringify({vol:0.12,repeat:2,shuffle:true}),",'')
  page2.set_content(fresh,wait_until='domcontentloaded');page2.wait_for_function('window.__reel')
  assert page2.evaluate('window.__reel.S.vol')==1
  assert not errors2,errors2
  browser.close()
print('PASS: GTK maximizes, new volume defaults to 100%, saved volume restores and edits are stored')
