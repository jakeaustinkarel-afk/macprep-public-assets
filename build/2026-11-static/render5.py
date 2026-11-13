"""Re-render slide 5 ("why") of a November case carousel.
Header and footer strips are copied from the existing slide so branding is pixel-identical."""
import sys, json, html, re
from PIL import Image
from playwright.sync_api import sync_playwright
SRC='/home/claude/macprep-public-assets/assets/2026-11-static'
CSS="""
*{box-sizing:border-box;margin:0;padding:0}
body{width:1080px;height:1350px;background:rgb(250,247,240);font-family:'Inter';color:rgb(23,32,28);position:relative;-webkit-font-smoothing:antialiased}
h1{position:absolute;left:92px;top:152px;font-family:'Inter Display';font-weight:800;font-size:64px;letter-spacing:-0.9px;line-height:80px}
.wrap{position:absolute;left:92px;top:258px;width:896px}
.dx{background:rgb(227,239,231);border-radius:20px;padding:26px 30px 28px;margin-bottom:34px}
.dx .lab{font-size:22px;font-weight:700;letter-spacing:3px;color:rgb(30,122,76);margin-bottom:10px}
.dx .name{font-family:'Inter Display';font-weight:800;font-size:44px;letter-spacing:-0.8px;line-height:52px;margin-bottom:8px}
.dx .txt{font-size:FSpx;line-height:LHpx}
.it{display:flex;gap:25px;margin-bottom:GAPpx}
.n{flex:none;width:54px;height:54px;border-radius:13px;background:rgb(30,122,76);color:#fff;font-weight:700;font-size:28px;display:flex;align-items:center;justify-content:center}
.n.w{background:rgb(178,58,46)}
.t{font-size:FSpx;line-height:LHpx;padding-top:1px}
b{font-weight:700}
"""
def md(s):
    s=html.escape(s,quote=False)
    return re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
def build(spec):
    fs=spec.get('fs',36); lh=round(fs*1.4); gap=spec.get('gap',26)
    css=CSS.replace('FS',str(fs)).replace('LH',str(lh)).replace('GAP',str(gap))
    items=''
    k=0
    for it in spec['items']:
        if it.startswith('!'):
            items+=f'<div class="it"><div class="n w">!</div><div class="t">{md(it[1:].strip())}</div></div>'
        else:
            k+=1; items+=f'<div class="it"><div class="n">{k}</div><div class="t">{md(it)}</div></div>'
    d=spec['dx']
    return f'''<html><head><style>{css}</style></head><body><h1>{md(spec["title"])}</h1><div class="wrap">
<div class="dx"><div class="lab">{md(d["label"])}</div><div class="name">{md(d["name"])}</div><div class="txt">{md(d["text"])}</div></div>
{items}<div id="end"></div></div></body></html>'''
def main(specfile,outdir):
    specs=json.load(open(specfile))
    with sync_playwright() as p:
        b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1350})
        for s in specs:
            pg.set_content(build(s)); pg.wait_for_timeout(150)
            end=pg.evaluate("document.getElementById('end').getBoundingClientRect().top")
            tmp=f'{outdir}/_{s["slug"]}.png'; pg.screenshot(path=tmp)
            im=Image.open(tmp).convert('RGB'); old=Image.open(f'{SRC}/{s["slug"]}-05.png').convert('RGB')
            im.paste(old.crop((0,0,1080,140)),(0,0)); im.paste(old.crop((0,1225,1080,1350)),(0,1225))
            im.save(f'{outdir}/{s["slug"]}-05v2.png'); print(s['slug'],'content bottom',round(end),'(limit 1215)')
        b.close()
main(sys.argv[1],sys.argv[2])
