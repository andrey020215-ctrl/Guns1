#!/usr/bin/env python3
"""Browser regression for the offline report: images must actually paint, including zoom/print.
Requires playwright, Pillow and Chromium (or `python -m playwright install chromium`).
Run: python tests/test_overview_images.py
"""
from hashlib import sha256
from io import BytesIO
import os
from pathlib import Path
import shutil

from PIL import Image, ImageStat
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'preview/winter-arsenal-overview.html'
IDS=['mp9','famas','nova','glock18','ak47','m4a1s','ssg08','usp_s','awp','xm1014','negev','deagle']


def painted(locator):
    """A missing CSS image left a flat panel; require substantial painted image variation."""
    pixels=locator.screenshot(animations='disabled')
    image=Image.open(BytesIO(pixels)).convert('RGB')
    assert image.width>=250 and image.height>=120, 'Image has collapsed'
    assert min(ImageStat.Stat(image).stddev)>12, 'Model image is blank or not painted'
    return sha256(pixels).hexdigest()


def assets_decoded(page):
    page.evaluate('''async () => {
        const source=document.getElementById('arsenal-render-sheet');
        if(!source) throw new Error('Embedded model source missing');
        const image=new Image(); image.src=source.getAttribute('href'); await image.decode();
        if(image.naturalWidth!==2880 || image.naturalHeight!==2710) throw new Error('Model image did not decode');
        const tracer=document.querySelector('img.tracer'); await tracer.decode();
        if(tracer.naturalWidth!==1600) throw new Error('Tracer image did not decode');
    }''')


with sync_playwright() as p:
    executable=os.environ.get('OVERVIEW_CHROMIUM') or shutil.which('chromium') or shutil.which('google-chrome')
    options={'headless':True,'args':['--no-sandbox']}
    if executable: options['executable_path']=executable
    browser=p.chromium.launch(**options)
    source=REPORT.read_text()
    desktop=browser.new_context(viewport={'width':1440,'height':1000},offline=True)
    page=desktop.new_page()
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.set_content(source,wait_until='load')
    assets_decoded(page)
    assert page.locator('.card').count()==12
    hashes=[]
    for ident in IDS:
        card=page.locator('#'+ident)
        hashes.append(painted(card.locator('.weapon-image')))
        name=card.locator('h3').inner_text()
        card.locator('.zoom').click()
        assert page.locator('#modal').is_visible()
        assert page.locator('#modal h3').inner_text()==name
        painted(page.locator('#modal .weapon-image'))
        page.locator('#modal .close').click()
    assert len(set(hashes))==12,'Models unexpectedly render as the same image'
    painted(page.locator('img.tracer'))
    page.locator('#free').check()
    for role,count in [('0',0),('1',4),('2',8),('3',12)]:
        page.locator('#role').select_option(role)
        assert page.locator('.card:visible').count()==count
    page.locator('#free').uncheck()
    page.locator('#search').fill('Кобальт')
    assert page.locator('.card:visible').count()==1
    painted(page.locator('#ak47 .weapon-image'))
    page.locator('#search').fill('')
    page.emulate_media(media='print')
    for ident in IDS: painted(page.locator('#'+ident+' .weapon-image'))
    assert not errors,errors
    desktop.close()
    for scripts in [True,False]:
        context=browser.new_context(viewport={'width':390,'height':844},offline=True,java_script_enabled=scripts)
        mobile=context.new_page()
        mobile.set_content(source,wait_until='load')
        for ident in IDS: painted(mobile.locator('#'+ident+' .weapon-image'))
        painted(mobile.locator('img.tracer'))
        assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Mobile report overflows horizontally'
        context.close()
    browser.close()
print('PASS: all 12 model images paint offline; 12 zoom dialogs, VIP filters, search, print, mobile and JavaScript-disabled viewing verified.')
