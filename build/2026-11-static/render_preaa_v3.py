"""Rebuild the pre-AA carousel (v3) from eight AA programs' published admissions requirements.
Header logo and footer strips are copied from the v2 slides; the date and body are re-rendered."""
import sys, html, re
from PIL import Image
from playwright.sync_api import sync_playwright

SRC = '/home/claude/macprep-public-assets/assets/2026-11-static'
BG = 'rgb(250,247,240)'
INK = 'rgb(23,32,28)'
GRAY = 'rgb(74,85,80)'
GREEN = 'rgb(30,122,76)'

BASE = f"""
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:1350px;background:{BG};font-family:'Inter';color:{INK};position:relative;-webkit-font-smoothing:antialiased}}
.date{{position:absolute;right:92px;top:95px;font-weight:600;font-size:26px;letter-spacing:0.4px}}
h1{{position:absolute;left:92px;top:152px;font-family:'Inter Display';font-weight:800;font-size:64px;letter-spacing:-0.9px;line-height:80px}}
.wrap{{position:absolute;left:92px;top:262px;width:896px}}
.it{{display:flex;gap:25px;margin-bottom:GAPpx}}
.n{{flex:none;width:54px;height:54px;border-radius:13px;background:{GREEN};color:#fff;font-weight:700;font-size:28px;display:flex;align-items:center;justify-content:center}}
.t{{font-size:FSpx;line-height:LHpx;padding-top:1px}}
.src{{font-size:28px;line-height:42px;color:{GRAY};padding-left:28px;position:relative;margin-bottom:6px}}
.src:before{{content:'';position:absolute;left:4px;top:18px;width:9px;height:9px;border-radius:50%;background:{GRAY}}}
.note{{font-size:28px;line-height:42px;color:{INK};margin-top:26px;font-weight:600}}
.lab{{font-size:22px;font-weight:700;letter-spacing:3px;color:{GREEN};margin:30px 0 12px}}
.sub{{position:absolute;left:92px;top:468px;font-size:41px;line-height:56px;color:{GRAY};width:896px}}
b{{font-weight:700}}
"""


def md(s):
    s = html.escape(s, quote=False)
    return re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)


def page(body, fs=36, gap=30):
    css = BASE.replace('FS', str(fs)).replace('LH', str(round(fs * 1.42))).replace('GAP', str(gap))
    return f'<html><head><style>{css}</style></head><body>{body}<div id="end"></div></body></html>'


def list_slide(date, title, items, fs=36, gap=30):
    rows = ''.join(f'<div class="it"><div class="n">{i}</div><div class="t">{md(t)}</div></div>'
                   for i, t in enumerate(items, 1))
    return page(f'<div class="date">{date}</div><h1>{md(title)}</h1><div class="wrap">{rows}<div id="last"></div></div>', fs, gap)


def main(date, outdir):
    slides = []
    # 01 cover: keep the v2 cover, replace only the date and the subtitle line.
    slides.append(('01', page(f'<div class="date">{date}</div><div class="sub">What 8 AA programs actually ask for.</div>'),
                   [('old', (0, 0, 1080, 1350)), ('blank', (0, 60, 1080, 140)), ('blank', (0, 455, 1080, 545)),
                    ('new', (0, 455, 1080, 545)), ('new', (700, 60, 1080, 140)), ('oldhdr', None)], 'pre-aa-01v2'))
    slides.append(('02', list_slide(date, 'The application', [
        '**CASAA.** All 8 programs we checked apply through CASAA, the central AA application. Some add a Casper test or an interview.',
        '**Entrance exam.** Most accept the GRE or the MCAT. CU Anschutz takes only the MCAT. Scores usually need to be from the last 3 to 5 years.',
        '**Letters.** Three is standard. Check who each program wants them from.',
    ], fs=36, gap=30), None, 'pre-aa-02'))
    slides.append(('03', list_slide(date, 'The experience', [
        '**Shadow in anesthesia.** Most programs ask for at least 8 hours. Case Western recommends 16 or more. More is better.',
        'Shadowing can be with a CAA, an anesthesiologist or a CRNA. Case Western prefers a CAA.',
        '**Patient care helps.** None of the 8 programs require it, but several weigh healthcare work, paid or volunteer.',
    ], fs=36, gap=30), None, 'pre-aa-03'))
    slides.append(('04', list_slide(date, 'The coursework', [
        '**GPA.** Stated minimums run 3.0 to 3.1. Admitted students often average 3.5 or higher.',
        '**Prerequisites.** Biology, general and organic chemistry, and physics everywhere. Most add biochemistry, statistics, and anatomy and physiology; many add calculus and English.',
        '**Watch the clock.** Several programs want key science courses from the last 5 to 7 years.',
    ], fs=36, gap=30), None, 'pre-aa-04'))
    # 05 tip: unchanged body, new date.
    slides.append(('05', page(f'<div class="date">{date}</div>'), 'dateonly', 'pre-aa-05'))
    srcs = ['Emory University', 'Case Western Reserve University', 'Indiana University School of Medicine',
            'University of Colorado Anschutz', 'Medical College of Wisconsin', 'University of Missouri–Kansas City',
            'Nova Southeastern University', 'South University']
    body = (f'<div class="date">{date}</div><h1>Where this comes from</h1><div class="wrap">'
            '<div class="lab">AA PROGRAM ADMISSIONS PAGES, NOV 2026</div>'
            + ''.join(f'<div class="src">{md(s)}</div>' for s in srcs) +
            '<div class="lab">ADVISING</div><div class="src">UGA Pre-Professional Advising Office, Pre-AA Quick Facts 2026</div>'
            '<div class="note">Requirements change every cycle. Confirm on each program\'s page before you apply.</div>'
            '<div id="last"></div></div>')
    slides.append(('06', page(body), 'sources', 'pre-aa-06'))

    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1080, 'height': 1350})
        for num, doc, mode, old in slides:
            pg.set_content(doc)
            pg.wait_for_timeout(200)
            last = pg.evaluate("(document.getElementById('last')||document.getElementById('end')).getBoundingClientRect().top")
            tmp = f'{outdir}/_preaa{num}.png'
            pg.screenshot(path=tmp)
            new = Image.open(tmp).convert('RGB')
            o = Image.open(f'{SRC}/{old}.png').convert('RGB')
            if num == '01':
                out = o.copy()
                out.paste(new.crop((0, 455, 1080, 545)), (0, 455))
                out.paste(new.crop((700, 60, 1080, 140)), (700, 60))
            elif mode == 'dateonly':
                out = o.copy()
                out.paste(new.crop((700, 60, 1080, 140)), (700, 60))
            elif mode == 'sources':
                out = new
                out.paste(o.crop((0, 0, 700, 140)), (0, 0))
                out.paste(o.crop((0, 1140, 1080, 1350)), (0, 1140))
            else:
                out = new
                out.paste(o.crop((0, 0, 700, 140)), (0, 0))
                out.paste(o.crop((0, 1225, 1080, 1350)), (0, 1225))
            out.save(f'{outdir}/pre-aa-{num}v3.png')
            print(num, 'content bottom', round(last))
        b.close()


main(sys.argv[1], sys.argv[2])
