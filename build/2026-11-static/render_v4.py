"""November 2026 multi-source pass (v4).
Re-renders explanation, list, text and sources slides from specs_v4.json.
Header (logo + date) and the bottom strip (share line + footer) are copied from the existing slide,
so branding and dates stay pixel-identical."""
import sys, json, html, re
from PIL import Image
from playwright.sync_api import sync_playwright

SRC = '/home/claude/macprep-public-assets/assets/2026-11-static'
BG = (250, 247, 240)
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:1080px;height:1350px;background:rgb(250,247,240);font-family:'Inter';color:rgb(23,32,28);position:relative;-webkit-font-smoothing:antialiased}
h1{position:absolute;left:92px;top:152px;width:896px;font-family:'Inter Display';font-weight:800;font-size:64px;letter-spacing:-0.9px;line-height:80px}
.wrap{position:absolute;left:92px;width:896px}
.dx{background:rgb(227,239,231);border-radius:20px;padding:26px 30px 28px;margin-bottom:34px}
.dx .lab,.fr .lab,.lab{font-size:22px;font-weight:700;letter-spacing:3px;color:rgb(30,122,76)}
.dx .lab{margin-bottom:10px}
.dx .name{font-family:'Inter Display';font-weight:800;font-size:44px;letter-spacing:-0.8px;line-height:52px;margin-bottom:8px}
.dx .txt{font-size:FSpx;line-height:LHpx}
.it{display:flex;gap:25px;margin-bottom:GAPpx}
.n{flex:none;width:54px;height:54px;border-radius:13px;background:rgb(30,122,76);color:#fff;font-weight:700;font-size:28px;display:flex;align-items:center;justify-content:center}
.n.w{background:rgb(178,58,46)}
.t{font-size:FSpx;line-height:LHpx;padding-top:1px}
.p{font-size:40px;line-height:58px;color:rgb(74,85,80);margin-bottom:28px}
.p b{color:rgb(23,32,28)}
.sec{margin:6px 0 12px}
.src+.sec{margin-top:30px}
.src{font-size:SFpx;line-height:SLpx;color:rgb(74,85,80);padding-left:26px;position:relative;margin-bottom:8px}
.src:before{content:'';position:absolute;left:4px;top:SDpx;width:8px;height:8px;border-radius:50%;background:rgb(74,85,80)}
.fr{background:rgb(227,239,231);border-radius:20px;padding:22px 28px 24px;margin-top:22px}
.fr .lab{margin-bottom:8px}
.fr .txt{font-size:29px;line-height:42px}
.note{font-size:26px;line-height:38px;color:rgb(23,32,28);font-weight:600;margin-top:20px}
b{font-weight:700}
"""


def md(s):
    s = html.escape(s, quote=False)
    return re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)


def page(body, fs=33, gap=20, sf=26):
    css = (CSS.replace('SFpx', f'{sf}px').replace('SLpx', f'{round(sf*1.45)}px').replace('SDpx', f'{round(sf*0.62)}px')
           .replace('FSpx', f'{fs}px').replace('LHpx', f'{round(fs*1.4)}px').replace('GAPpx', f'{gap}px'))
    return f'<html><head><style>{css}</style></head><body>{body}</body></html>'


def items_html(items):
    out, k = '', 0
    for it in items:
        if it.startswith('!'):
            out += f'<div class="it"><div class="n w">!</div><div class="t">{md(it[1:].strip())}</div></div>'
        else:
            k += 1
            out += f'<div class="it"><div class="n">{k}</div><div class="t">{md(it)}</div></div>'
    return out


def build(s):
    t = s['type']
    title = f'<h1 id="h">{md(s["title"])}</h1>' if s.get('title') else ''
    top = s.get('top', 258)
    if t == 'case5':
        d = s['dx']
        body = (f'<div class="dx"><div class="lab">{md(d["label"])}</div><div class="name">{md(d["name"])}</div>'
                f'<div class="txt">{md(d["text"])}</div></div>' + items_html(s['items']))
    elif t == 'list':
        body = items_html(s['items'])
    elif t == 'text':
        body = ''.join(f'<div class="p">{md(p)}</div>' for p in s['paras'])
    elif t == 'sources':
        body = s.get('lead', '') and f'<div class="p">{md(s["lead"])}</div>'
        for g in s['groups']:
            body += f'<div class="lab sec">{md(g["label"])}</div>' + ''.join(f'<div class="src">{md(x)}</div>' for x in g['items'])
        if s.get('further'):
            body += f'<div class="fr"><div class="lab">FURTHER READING</div><div class="txt">{md(s["further"])}</div></div>'
        if s.get('note'):
            body += f'<div class="note">{md(s["note"])}</div>'
    else:
        raise ValueError(t)
    wrap = f'<div class="wrap" id="w" style="top:{top}px">{body}<div id="end"></div></div>'
    return page(title + wrap, s.get('fs', 33), s.get('gap', 20), s.get('sf', 26))


def bottom_start(old):
    """First row of the share line / footer strip, scanning up from the footer rule."""
    px = old.load()
    def ink(y):
        return any(sum(abs(a - b) for a, b in zip(px[x, y], BG)) > 60 for x in range(92, 988, 4))
    y = 1215
    while y > 900 and not ink(y):
        y -= 1
    # y is the last ink row of the share line; walk up to its first row
    while y > 900 and ink(y):
        y -= 1
    return y - 14


def main(specfile, outdir, only=None):
    specs = json.load(open(specfile))
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1080, 'height': 1350})
        for s in specs:
            if only and s['out'] not in only:
                continue
            old = Image.open(f'{SRC}/{s["old"]}.png').convert('RGB')
            cut = s.get('cut') or (bottom_start(old) if s.get('share', True) else 1225)
            pg.set_content(build(s))
            pg.wait_for_timeout(150)
            end = pg.evaluate("document.getElementById('end').getBoundingClientRect().top")
            tmp = f'{outdir}/_{s["out"]}.png'
            pg.screenshot(path=tmp)
            im = Image.open(tmp).convert('RGB')
            im.paste(old.crop((0, 0, 1080, 140)), (0, 0))
            im.paste(old.crop((0, cut, 1080, 1350)), (0, cut))
            im.save(f'{outdir}/{s["out"]}.png')
            flag = 'OK' if end < cut - 10 else 'OVERFLOW'
            print(f'{s["out"]}: content bottom {round(end)}, keep-from {cut} -> {flag}')
        b.close()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3:] or None)
