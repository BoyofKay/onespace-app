#!/usr/bin/env python3
"""Render the marketing images in assets/press/ (needs Playwright + Chrome).
    python3 tools/render_press.py
"""
import asyncio, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

CSS = (ROOT / 'assets' / 'os.css').read_text()
MARK = (ROOT / 'assets' / 'mark.svg').as_uri()


# Brand fonts bundled in tools/fonts (SIL Open Font License), so images never fall back to a default serif.
FONT_DIR = Path(__file__).resolve().parent / 'fonts'
FONTS = ''.join(f"@font-face{{font-family:'Plus Jakarta Sans';font-weight:{w};src:url('{(FONT_DIR / f'plus-jakarta-sans-latin-{w}-normal.woff2').as_uri()}') format('woff2')}}" for w in (400, 500, 600, 700, 800)) + \
    ''.join(f"@font-face{{font-family:'IBM Plex Sans Arabic';font-weight:{w};src:url('{(FONT_DIR / f'ibm-plex-sans-arabic-arabic-{w}-normal.woff2').as_uri()}') format('woff2')}}" for w in (400, 600, 700))


def doc(w, h, inner, bg):
    return f'''<!doctype html><html><head><meta charset="utf-8"><base href="{ROOT.as_uri()}/">
<style>{FONTS}{CSS} body{{font-family:'Plus Jakarta Sans','IBM Plex Sans Arabic',sans-serif}} body{{margin:0;width:{w}px;height:{h}px;overflow:hidden;background:{bg}}} .phone::before{{}} .card-x{{position:absolute;inset:0}}</style>
</head><body><div class="card-x">{inner}</div></body></html>'''


def brand(size=30, color='#14213D'):
    return f'<div style="display:flex;align-items:center;gap:12px;font-weight:800;font-size:{size}px;color:{color};letter-spacing:-.02em"><img src="assets/mark.svg" style="width:{size*1.3}px">OneSpace</div>'


def tag(text, color='#1F6E78'):
    return f'<div style="color:{color};font-weight:800;letter-spacing:.12em;text-transform:uppercase;font-size:20px">● {text}</div>'


HERO_BG = 'radial-gradient(700px 500px at 85% 15%, rgba(232,116,90,.25), transparent 70%), radial-gradient(600px 500px at 5% 95%, rgba(31,110,120,.18), transparent 70%), #FFF8F3'
P = lambda fn, th, scale: f'<div style="transform:scale({scale});transform-origin:top left">{build.phone(fn(), th)}</div>'

def real_device(name, lang, width, extra=''):
    src = (ROOT / 'assets' / 'app' / lang / f'{name}.webp')
    if not src.exists():
        src = ROOT / 'assets' / 'app' / 'en' / f'{name}.webp'
    return f'<div class="device" style="width:{width}px;{extra}"><img src="{src.as_uri()}" loading="eager"></div>'


STORE = [  # (screen, English caption, Arabic caption, background)
    ('today', 'Your shared day, at a glance', 'يومكما المشترك في لمحة', '#FFF1EA'),
    ('counters', 'Count the days that matter', 'عدّا الأيام المهمة', '#F0EBFB'),
    ('activity', 'Decide together, calmly', 'قرّرا معًا بهدوء', '#E6F3F3'),
    ('trip', 'Every trip, planned for two', 'كل رحلة مُخطط لها لشخصين', '#FFF4DC'),
    ('letters', 'Letters that wait for the right day', 'رسائل تنتظر اليوم المناسب', '#FCE7EE'),
    ('places_map', 'Your places on your own map', 'أماكنكما على خريطتكما', '#E5F2E7'),
]


def store_images():
    out = {}
    for lang in ('en', 'ar'):
        for i, (shot, en, ar, bg) in enumerate(STORE, 1):
            cap = ar if lang == 'ar' else en
            d = 'rtl' if lang == 'ar' else 'ltr'
            out[f'store-{lang}-{i}.png'] = (1080, 1920, bg, f'''<div dir="{d}" style="position:absolute;inset:0;font-family:{"'IBM Plex Sans Arabic','Plus Jakarta Sans',sans-serif" if lang == 'ar' else "'Plus Jakarta Sans',sans-serif"}">
              <div style="position:absolute;top:110px;left:80px;right:80px;text-align:center">{brand(40)}
                <h1 style="font-size:{82 if lang == 'en' else 76}px;line-height:1.15;margin:46px 0 0;letter-spacing:{'-.03em' if lang == 'en' else '0'}">{cap}</h1></div>
              <div style="position:absolute;left:50%;top:560px;transform:translateX(-50%)">{real_device(shot, lang, 640)}</div></div>''')
    return out


IMAGES = {
    'og-image.png': (1200, 630, HERO_BG, f'''
      <div style="position:absolute;left:70px;top:70px;width:640px">{brand(34)}
        <div style="height:46px"></div>{tag('Two of us. One Space.')}
        <h1 style="font-size:66px;margin:16px 0 18px">The private home for the life <span class="accent">you share.</span></h1>
        <p class="lead" style="font-size:24px">Plans, reminders, trips, little gestures and memories — for couples near or far.</p></div>
      <div style="position:absolute;left:800px;top:60px">{P(lambda: build.scr_today(True), 'clean', 0.95)}</div>'''),
    'social-square.png': (1080, 1080, HERO_BG, f'''
      <div style="position:absolute;left:80px;top:80px;width:520px">{brand(36)}
        <div style="height:60px"></div>{tag('Founding 500')}
        <h1 style="font-size:76px;margin:18px 0 22px">Be one of the first 250 couples.</h1>
        <p class="lead" style="font-size:28px">The first 250 couples become Founder Members. Free early access.</p>
        <div class="btn btn-primary" style="margin-top:30px;font-size:24px;padding:20px 30px">Join at onespace.live</div></div>
      <div style="position:absolute;left:640px;top:170px">{P(scr := build.scr_counters, 'lavender', 1.15)}</div>'''),
    'social-story.png': (1080, 1920, HERO_BG, f'''
      <div style="position:absolute;left:90px;top:130px;right:90px">{brand(44)}
        <div style="height:70px"></div>{tag('Two of us. One Space.')}
        <h1 style="font-size:96px;margin:20px 0 26px">Plan together. Stay close.</h1>
        <p class="lead" style="font-size:36px">The private couples app — near or far.</p></div>
      <div style="position:absolute;left:255px;top:790px">{P(lambda: build.scr_love(), 'rose', 1.85)}</div>'''),
    'store-feature.png': (1024, 500, 'linear-gradient(135deg,#14213D,#1E3354)', f'''
      <div style="position:absolute;left:60px;top:80px;width:560px">{brand(32, '#fff')}
        <h1 style="font-size:58px;margin:30px 0 16px;color:#fff">Two of us.<br><span class="accent">One Space.</span></h1>
        <p style="font-size:23px;color:#C3CCDD;margin:0">Plans, love and memories — just for the two of you.</p></div>
      <div style="position:absolute;left:620px;top:40px">{P(lambda: build.scr_ourspace(), 'coral', 0.72)}</div>
      <div style="position:absolute;left:790px;top:110px">{P(lambda: build.scr_arabic(), 'midnight', 0.66)}</div>'''),
}


if (ROOT / 'assets' / 'app' / 'en' / 'today.webp').exists():
    IMAGES.update(store_images())
    IMAGES['og-image.png'] = (1200, 630, HERO_BG, f'''
      <div style="position:absolute;left:70px;top:70px;width:600px">{brand(34)}
        <div style="height:46px"></div>{tag('Two of us. One Space.')}
        <h1 style="font-size:62px;margin:16px 0 18px">The private home for the life <span class="accent">you share.</span></h1>
        <p class="lead" style="font-size:24px">The couples app for plans, love and memories — near or far.</p></div>
      <div style="position:absolute;left:690px;top:120px;transform:rotate(-6deg)">{real_device('counters', 'en', 230)}</div>
      <div style="position:absolute;left:880px;top:50px">{real_device('today', 'en', 270)}</div>''')


async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        for name, (w, h, bg, inner) in IMAGES.items():
            pg = await b.new_page(viewport={'width': w, 'height': h})
            tmp = ROOT / '_press_tmp.html'
            tmp.write_text(doc(w, h, inner, bg), encoding='utf-8')
            await pg.goto(tmp.as_uri(), wait_until='networkidle')
            await pg.evaluate('document.fonts.ready')
            tmp.unlink()
            await pg.wait_for_timeout(300)
            await pg.screenshot(path=str(ROOT / 'assets' / 'press' / name))
            await pg.close()
        await b.close()
    previews()
    print('rendered', list(IMAGES))


def previews():
    """Light WebP copies for showing on the Share kit page; the full PNGs stay the downloads."""
    from PIL import Image
    out = ROOT / 'assets' / 'press' / 'preview'
    out.mkdir(exist_ok=True)
    for png in sorted((ROOT / 'assets' / 'press').glob('*.png')):
        im = Image.open(png).convert('RGB')
        im.thumbnail((720, 720 if 'story' not in png.name else 1280))
        im.save(out / (png.stem + '.webp'), 'WEBP', quality=82, method=6)


if __name__ == '__main__':
    asyncio.run(main())
