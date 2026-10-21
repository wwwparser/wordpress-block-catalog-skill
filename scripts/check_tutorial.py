"""Check tutorial navigation, learning controls, local links and responsive layout."""
import json
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'tutorial'
html = BeautifulSoup((SITE / 'index.html').read_text(encoding='utf-8'), 'html.parser')
ids = [e['id'] for e in html.select('[id]')]
assert len(ids) == len(set(ids))
assert len(html.select('.chapter')) == 22
for element in html.select('[href],[src]'):
    link = element.get('href', element.get('src'))
    parts = urlsplit(link)
    if parts.scheme or parts.netloc: continue
    if parts.path:
        assert (SITE / unquote(parts.path)).is_file(), link
    if parts.fragment and not parts.path:
        assert parts.fragment in ids, link
assert '{{' not in (SITE / 'index.html').read_text(encoding='utf-8')
with zipfile.ZipFile(SITE / 'downloads/authored-source.zip') as archive:
    assert archive.testzip() is None
    assert not any(x.startswith('runtime/') or x.endswith('.env') or 'credentials.json' in x or 'cookies' in x for x in archive.namelist())
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width':1440, 'height':1000}, reduced_motion='reduce')
    errors=[]
    page.on('pageerror', lambda err: errors.append(str(err)))
    page.goto('http://127.0.0.1:8137/', wait_until='networkidle')
    assert page.title().startswith('Как создать каталог')
    assert page.locator('.chapter').count()==22
    page.locator('[data-set-mode=manual]').click()
    assert page.locator('.agent:visible').count()==0
    assert page.locator('.manual:visible').count()>0
    page.locator('[data-set-mode=agent]').click()
    assert page.locator('.manual:visible').count()==0
    page.locator('[data-set-mode=both]').click()
    page.locator('#search').fill('nonce')
    assert 0 < page.locator('.chapter:visible').count() < 22
    assert page.locator('.toc a:visible').count() == page.locator('.chapter:visible').count()
    page.locator('#search').fill('небывалыйзапрос987')
    assert page.locator('.chapter:visible').count()==0
    assert page.locator('.empty').is_visible()
    page.locator('#search').fill('')
    page.locator('.complete input').first.check()
    page.reload(wait_until='networkidle')
    assert page.locator('.complete input').first.is_checked()
    assert page.locator('.toc a.done').count()==1
    page.locator('#reset').click()
    for index, answer in enumerate(['b','a','c','b','a','c','b','a'],1):
        page.locator(f'input[name=q{index}][value={answer}]').check()
    page.locator('#check-quiz').click()
    assert '8 из 8' in page.locator('#quiz-result').inner_text()
    for width in [1440,990,768,390]:
        page.set_viewport_size({'width':width,'height':900})
        assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'), width
        page.evaluate('scrollTo(0,0)')
        page.screenshot(path=str(ROOT / f'research/tutorial-{width}.png'))
    page.get_by_role('button', name='Содержание').click()
    assert page.locator('.sidebar').evaluate('e=>e.getBoundingClientRect().left')==0
    page.keyboard.press('Escape')
    assert page.locator('.sidebar').evaluate('e=>e.getBoundingClientRect().right')<=0
    assert not errors, errors
    browser.close()
report={'chapters':22,'links_and_anchors':True,'source_archive_no_runtime':True,'modes':True,'search':True,'progress_persists':True,'quiz':'8/8','widths':[1440,990,768,390],'overflow':False,'mobile_menu':True,'javascript_errors':errors}
(ROOT / 'research/tutorial-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('All tutorial checks passed')
