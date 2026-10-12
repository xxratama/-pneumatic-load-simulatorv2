
import json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
artifact=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).with_name('index.html')
results=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,channel='msedge')
 pg=b.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);errors=[];pg.on('pageerror',lambda e:errors.append(str(e)));pg.goto(artifact.as_uri());pg.evaluate('document.fonts.ready')
 for w,h in [(360,640),(360,780),(390,844),(412,915),(430,932)]:
  pg.set_viewport_size({'width':w,'height':h});pg.wait_for_function("document.querySelector('.mobile-load-selection').parentElement.className==='pls-machine-panel'")
  d=pg.evaluate('''() => {let r=s=>{let b=document.querySelector(s).getBoundingClientRect();return {top:b.top,bottom:b.bottom,height:b.height}};return {w:innerWidth,h:innerHeight,page:document.documentElement.scrollWidth,rig:r('.pls-machine-wrap'),input:r('#pls-target-number'),presets:r('.pls-presets'),start:r('#pls-start'),reading:r('.arcade-telemetry')};}''')
  assert d['page']<=w,d
  assert 0<=d['input']['top']-d['rig']['bottom']<=55,d
  assert d['presets']['top']>=d['input']['bottom'],d
  assert d['start']['top']>d['presets']['bottom'],d
  assert d['reading']['top']>=d['start']['bottom'],d
  assert d['start']['bottom']<=h,d
  assert d['rig']['top']>=0 and d['rig']['bottom']<h,d
  results.append(d)
 pg.set_viewport_size({'width':390,'height':844});pg.locator('.pls-presets button[data-target="5"]').click();pg.clock.install();pg.locator('#pls-start').click();pg.clock.run_for(22000)
 initial=pg.evaluate('plsApp.getState()');assert initial['stable'] and abs(initial['mass']-5)<.01
 piston_before=pg.locator('#pls-moving-head').get_attribute('transform');gauge_before=pg.locator('#pls-gauge-needle').get_attribute('d')
 pg.locator('.pls-presets button[data-target="15"]').click();pg.clock.run_for(22000);loaded=pg.evaluate('plsApp.getState()')
 assert loaded['stable'] and abs(loaded['mass']-15)<.01,loaded
 assert pg.locator('#pls-gauge-needle').get_attribute('d')!=gauge_before
 assert pg.evaluate('scrollY')==0,'Changing preset should not scroll away from rig'
 assert pg.locator('.pls-machine-wrap').bounding_box()['y']>=0
 pg.locator('#pls-record').click();assert pg.locator('#pls-count').inner_text()=='1'
 pg.locator('#pls-emergency').click();pg.clock.run_for(5000);assert pg.evaluate('plsApp.getState().pressure')==0;pg.locator('#pls-start').click()
 # Input focus with reduced available height keeps rig and input visible together.
 pg.set_viewport_size({'width':390,'height':500});pg.locator('#pls-target-number').focus();pg.clock.run_for(150)
 focused=pg.evaluate('''() => ({rig:document.querySelector('.pls-machine-wrap').getBoundingClientRect().toJSON(),input:document.querySelector('#pls-target-number').getBoundingClientRect().toJSON(),scroll:scrollY})''')
 assert 0<=focused['rig']['top']<focused['rig']['bottom']<=500,focused
 assert focused['input']['top']>=focused['rig']['bottom'] and focused['input']['bottom']<=500,focused
 pg.fill('#pls-target-number','12.5');pg.locator('#pls-target-number').dispatch_event('change');assert pg.evaluate('plsApp.getState().target')==12.5
 pg.locator('#pls-target-number').blur();pg.set_viewport_size({'width':390,'height':844});pg.clock.run_for(100)
 pg.locator('#pls-phone-focus').click();assert pg.locator('#pls-focus-electronics').is_visible();pg.locator('#pls-focus-electronics').click();pg.locator('#pls-zoom').click();assert pg.locator('#pls-apparatus-dialog').evaluate('e=>e.open');pg.keyboard.press('Escape');pg.wait_for_function("document.querySelector('.pls-machine-wrap').parentElement.className==='pls-machine-panel'")
 pg.locator('.studio-hotspot[data-component-select="7"]').click();assert pg.locator('#pls-component-details').evaluate('e=>e.open');assert pg.locator('#pls-inspector-title').inner_text()=='HX711'
 pg.set_viewport_size({'width':1440,'height':1050});pg.wait_for_function("document.querySelector('.mobile-load-selection').parentElement.className==='pls-console'");assert pg.locator('.pls-console #pls-start').count()==1
 pg.set_viewport_size({'width':390,'height':844});pg.wait_for_function("document.querySelector('.mobile-load-selection').parentElement.className==='pls-machine-panel'")
 assert pg.locator('#pls-target-number').count()==1 and pg.locator('#pls-start').count()==1
 assert not errors,errors
 print(json.dumps({'layouts':results,'running_target_change':{'from_kg':initial['mass'],'to_kg':loaded['mass'],'gauge_changed':True,'scroll_kept_at_top':True},'keyboard_reduced_viewport':focused,'controls_and_inspection':'passed','duplicate_controls':False,'browser_errors':errors},indent=2));b.close()
