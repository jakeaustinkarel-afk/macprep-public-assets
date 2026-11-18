import sys, json
sys.path.insert(0, '/home/claude/macprep-public-assets/build/2026-11-static')
import render_v4 as R
from PIL import Image
from playwright.sync_api import sync_playwright
SRC = '/home/claude/macprep-public-assets/assets/2026-11-static'
OUT = sys.argv[1]
TOTAL = 8
NUMCSS = "position:absolute;left:92px;top:1267px;font-family:Inter;font-size:26px;line-height:1;color:rgb(74,85,80)"
def renumber(pg, im, n):
    pg.set_content(f"<html><body style='margin:0;width:1080px;height:1350px;background:rgb(250,247,240);-webkit-font-smoothing:antialiased'><div style='{NUMCSS}'>{n:02d} / {TOTAL:02d}</div></body></html>")
    pg.wait_for_timeout(100); pg.screenshot(path=f'{OUT}/_num.png')
    num = Image.open(f'{OUT}/_num.png').convert('RGB')
    im.paste(num.crop((80, 1255, 400, 1305)), (80, 1255)); return im
specs = json.load(open('specs_first_offer_v6.json'))
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1350})
    for s in specs:
        old = Image.open(f'{SRC}/{s["old"]}.png').convert('RGB')
        pg.set_content(R.build(s)); pg.wait_for_timeout(150)
        end = pg.evaluate("document.getElementById('end').getBoundingClientRect().top")
        pg.screenshot(path=f'{OUT}/_t.png'); im = Image.open(f'{OUT}/_t.png').convert('RGB')
        cut = R.bottom_start(old) if s['type']=='sources' else 1225
        im.paste(old.crop((0, 0, 1080, 140)), (0, 0)); im.paste(old.crop((0, cut, 1080, 1350)), (0, cut))
        n = int(s['out'].split('-')[-1][:2]); renumber(pg, im, n).save(f'{OUT}/{s["out"]}.png')
        print(s['out'], round(end), 'OK' if end < (R.bottom_start(old)-10 if s['type']=='sources' else 1215) else 'OVERFLOW')
    for src, out, n in [('first-offer-01v2', 'first-offer-01v6', 1), ('first-offer-05', 'first-offer-07v6', 7)]:
        renumber(pg, Image.open(f'{SRC}/{src}.png').convert('RGB'), n).save(f'{OUT}/{out}.png'); print(out)
    b.close()
