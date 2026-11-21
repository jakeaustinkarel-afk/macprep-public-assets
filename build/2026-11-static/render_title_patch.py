"""Replace only the title of an existing slide (used Nov 21, 2026 for pyloric-stenosis-03)."""
import sys
from PIL import Image
from playwright.sync_api import sync_playwright
from render_v4 import page, md, SRC
def main(old, out, title, y0, y1, style=''):
    with sync_playwright() as p:
        b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1350})
        pg.set_content(page(f'<h1 id="h" style="{style}">{md(title)}</h1>')); pg.wait_for_timeout(150)
        box=pg.evaluate("(()=>{const r=document.getElementById('h').getBoundingClientRect();return [r.top,r.bottom]})()")
        pg.screenshot(path='/tmp/_t.png'); b.close()
    new=Image.open('/tmp/_t.png').convert('RGB'); im=Image.open(f'{SRC}/{old}.png').convert('RGB')
    im.paste(new.crop((0,y0,1080,y1)),(0,y0)); im.save(f'{SRC}/{out}.png'); print('title box',box,'patched',y0,y1)
if __name__=='__main__': main(sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]),int(sys.argv[5]),sys.argv[6] if len(sys.argv)>6 else '')
