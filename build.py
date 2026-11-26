#!/usr/bin/env python3
"""OneSpace website generator — one design system for every page.

    python3 build.py        # writes the .html pages, assets/ar.js, sitemap.xml, robots.txt

All copy lives here and in content/ (English + Arabic). Illustrations are
HTML/CSS recreations of real app screens with example people (Omar & Lina) —
never screenshots with real data.
"""
import hashlib
import json
import re
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
BASE = 'https://onespace.live/'
TODAY = date.today().isoformat()
# Privacy-friendly, cookieless analytics (https://www.goatcounter.com, free). Set to your code, e.g. 'onespace', then rebuild.
GOATCOUNTER = 'onespace'
# Search engine ownership checks. Paste the content="..." value Google Search Console / Bing Webmaster Tools gives you
# for the "HTML tag" method (or verify by DNS and leave these empty).
GOOGLE_VERIFY = ''
BING_VERIFY = ''
# IndexNow key (Bing, Yandex, Seznam, Naver): the file <key>.txt is published at the site root.
INDEXNOW_KEY = '5f0c3a9e7b2d4c18a6e1f4b9d2c7e3a1'
AR: dict[str, str] = {}
LEGAL = json.loads((ROOT / 'content' / 'legal.json').read_text(encoding='utf-8'))
import sys as _sys
_sys.path.insert(0, str(ROOT / 'content'))
from deep_pages import DEEP, COMPARE  # noqa: E402
from arabic_copy_overrides import revise
from full_localization import NEW_LANGS, LANGS, build_locales
from launch_enrichment import STORY_UI, FAQ_MORE, GUIDE_MORE
from journeys_apart_01 import JOURNEYS as J_APART_1
from journeys_apart_02 import JOURNEYS as J_APART_2
from journeys_together_01 import JOURNEYS as J_TOGETHER_1
from journeys_together_02 import JOURNEYS as J_TOGETHER_2
from journeys_ui import UI as JOURNEY_UI, FEATURES as JOURNEY_FEATURES
from faq_additions import FAQ_ADDITIONS
from tutorial_additions import TUTORIAL_ADDITIONS
from tutorial_journeys import JOURNEY_TUTORIAL_ADDITIONS, JOURNEY_LABEL
from guide_additions_1 import GUIDE_ADDITIONS_1
from guide_additions_2 import GUIDE_ADDITIONS_2
from structured_locale import localize_structured
# New content is additive; previously approved sections and pages remain unchanged.
for _group, _entries in FAQ_ADDITIONS.items():
    FAQ_MORE.setdefault(_group, []).extend([(q[:2], answer[:2]) for q, answer in _entries])
from journey_links import linkify_journeys
from journeys_solo_01 import JOURNEYS as J_SOLO_1
from nov22_updates import ar as _nov_ar, SOLO_GUIDE, ROWS_BY_EN

JOURNEYS = J_APART_1 + J_APART_2 + J_TOGETHER_1 + J_TOGETHER_2 + J_SOLO_1


def T(en, ar, tag='span', cls='', attrs=''):
    """Text that switches to Arabic. Keys are stable hashes of the English."""
    key = 'k' + hashlib.sha1(en.encode()).hexdigest()[:10]
    AR[key] = ar
    c = f' class="{cls}"' if cls else ''
    a = f' {attrs}' if attrs else ''
    return f'<{tag}{c}{a} data-i18n="{key}">{en}</{tag}>'


def N(en, tag='span', cls='', attrs=''):
    """22 Nov 2026 copy: Arabic (and ES/FR/DE) come from content/nov22_updates.py."""
    return T(en, _nov_ar(en), tag, cls, attrs)


def K(en, ar):
    """Register a translation and return its key (for attributes)."""
    key = 'k' + hashlib.sha1(en.encode()).hexdigest()[:10]
    AR[key] = ar
    return key


# ------------------------------------------------------------------ shell
NAV = [
    ('features.html', 'Features', 'المزايا'),
    ('how-it-works.html', 'Demo', 'العرض'),
    ('tutorials.html', 'Tutorials', 'الدروس'),
    ('guides.html', 'Guides', 'الأدلة'),
    ('faq.html', 'FAQ', 'الأسئلة'),
]


def head(page, title, title_ar, desc, desc_ar=''):
    canonical = BASE + ('' if page == 'index.html' else page)
    def link(href, en, ar):
        cur = ' aria-current="page"' if href == page else ''
        return f'<a href="{href}"{cur}>{T(en, ar)}</a>'

    def mega_link(item):
        href, _icon, label_en, label_ar, detail_en, detail_ar = item
        return (f'<a class="mega-link" href="{href}">'
                f'<span class="mega-link-copy">{T(label_en, label_ar, "b")}'
                f'{T(detail_en, detail_ar, "small")}</span>'
                '<span class="mega-link-arrow" aria-hidden="true">↗</span></a>')

    def drop(label, label_ar, groups, pages, intro_heading, intro_heading_ar,
             intro_description, intro_description_ar, lead_link):
        """One typographic navigation system — no emoji tile/card grid."""
        panel_id = 'mega-' + ('features' if label == 'Features' else 'couples' if label == 'Who it’s for' else 'learn')
        cur = ' aria-current="page"' if page in pages else ''
        group_html = ''.join(
            '<section class="mega-section">'
            + T(heading, heading_ar, 'h3', 'mega-section-label')
            + '<div class="mega-links">' + ''.join(mega_link(item) for item in items) + '</div></section>'
            for heading, heading_ar, items in groups
        )
        href, title_en, title_ar = lead_link
        intro = (f'<aside class="mega-intro">{T(label, label_ar, "span", "mega-eyebrow")}'
                 f'{T(intro_heading, intro_heading_ar, "p", "mega-intro-title")}'
                 f'{T(intro_description, intro_description_ar, "p", "mega-intro-desc")}'
                 f'<a class="mega-intro-link" href="{href}">{T(title_en, title_ar)}'
                 '<span aria-hidden="true">↗</span></a></aside>')
        return (f'<div class="drop" data-menu="{panel_id}">'
                f'<button type="button" aria-expanded="false" aria-controls="{panel_id}"{cur}>'
                f'{T(label, label_ar)} <span aria-hidden="true">▾</span></button>'
                f'<div class="drop-panel mega-panel" id="{panel_id}" role="group" aria-label="{escape(label)}">'
                f'<div class="mega-inner">{intro}<div class="mega-sections">{group_html}</div></div>'
                '</div></div>')

    feature_by_slug = {d['slug']: (d['slug'], d['icon'], d['nav'][0], d['nav'][1], d['navd'][0], d['navd'][1]) for d in DEEP}
    # Feature navigation describes the in-app workflows. Competitive positioning
    # is a separate top-level "Why OneSpace" destination, not a feature.
    groups_features = [
        ('Collect & share', 'اجمعا وشاركا', [
            ('smart-sharing.html','', 'Smart sharing & unified lists', 'مشاركة ذكية وقوائم موحّدة',
             'From any app into one list for both', 'من أي تطبيق إلى قائمة واحدة لكليكما'),
            feature_by_slug['watchlists.html'],
            feature_by_slug['everyday.html'],
            feature_by_slug['memories.html'],
        ]),
        ('Plan & decide', 'خططا وقررا', [
            ('decide-together.html','', 'Compare options together', 'قارنا الخيارات معًا',
             'Prices, specs, both opinions, one decision', 'الأسعار والمواصفات ورأي كل منكما وقرار واحد'),
            feature_by_slug['trips.html'],
            feature_by_slug['occasions.html'],
        ]),
        ('Connect & care', 'تواصلا واهتما', [
            ('connect-care.html#letters','', 'Love letters', 'رسائل الحب',
             'Write now; open on a chosen day', 'اكتبا الآن وافتحا في يوم تختارانه'),
            ('connect-care.html#gestures','', 'A little love', 'لمسة حب',
             'Personal gestures in your own words', 'لفتات خاصة بكلماتكما'),
            ('connect-care.html#checkins','', 'Daily check-ins', 'التواصل اليومي',
             'Know how your partner is doing', 'اطمئنا على أحوال بعضكما'),
            ('connect-care.html#journal','', 'Feelings journal', 'يوميات المشاعر',
             'Make space for your feelings', 'مساحة للتعبير عن المشاعر'),
        ]),
    ]
    groups_couples = [
        ('Find your rhythm', 'اختارا ما يناسب حياتكما', [
            ('long-distance.html','', 'Living apart','متباعدان',
             'Two cities, two clocks, one life','مدينتان وساعتان وحياة واحدة'),
            ('living-together.html','', 'Living together','تحت سقف واحد',
             'One home, so much to share','بيت واحد وكثير لنتشاركه'),
            ('on-my-own.html','', 'On my own', _nov_ar('On my own'),
             'Your own space for everything', _nov_ar('Your own space for everything')),
        ]),
    ]
    groups_learn = [
        ('Get started', 'ابدأ الآن', [
            ('tutorials.html','', 'Tutorials','الدروس','Step-by-step how-tos','شروحات خطوة بخطوة'),
            ('guides.html','', 'Guides', _nov_ar('Guides'), 'Ideas for everyday life', _nov_ar('Ideas for everyday life')),
        ]),
        ('More to explore', 'استكشف المزيد', [
            ('scenarios.html','', *STORY_UI['nav'], *STORY_UI['navDesc']),
            ('faq.html','', 'FAQ','الأسئلة الشائعة','Privacy, pricing, help','الخصوصية والأسعار والمساعدة'),
            ('whats-new.html','', "What's new",'الجديد','Updates and availability','التحديثات والتوفر'),
        ]),
    ]
    menu = [
        drop('Features','المزايا',groups_features,
             ('features.html','connect-care.html') + tuple(d['slug'] for d in DEEP),
             'Explore the app','اكتشف التطبيق',
             'Everything, in one shared space','كل تفاصيل حياتكما في مساحة واحدة',
             ('features.html','See all features','عرض كل المزايا')),
        link('compare.html','Why OneSpace','لماذا OneSpace'),
        drop('Who it’s for',_nov_ar('Who it’s for'),groups_couples,
             ('long-distance.html','living-together.html','on-my-own.html'),
             'Built for your life',_nov_ar('Built for your life'),
             'Together, apart or on your own',_nov_ar('Together, apart or on your own'),
             ('scenarios.html','See real-life stories',_nov_ar('See real-life stories'))),
        link('how-it-works.html','Demo','العرض'),
        drop('Learn','تعلّم',groups_learn,
             ('guides.html','tutorials.html','scenarios.html','faq.html','whats-new.html') + tuple(g['slug'] for g in GUIDES),
             'Learn OneSpace','تعرّف على OneSpace',
             'Help, ideas and updates','مساعدة وأفكار وتحديثات',
             ('guides.html','Explore the guides','استكشف الأدلة')),
        link('index.html#get-the-app','Get the app','حمّل التطبيق')
    ]
    dk = K(desc, desc_ar or desc)
    verify = (f'\n<meta name="google-site-verification" content="{GOOGLE_VERIFY}">' if GOOGLE_VERIFY else '') + \
             (f'\n<meta name="msvalidate.01" content="{BING_VERIFY}">' if BING_VERIFY else '')
    site_ld = json.dumps({'@context': 'https://schema.org', '@graph': [
        {'@type': 'Organization', '@id': BASE + '#org', 'name': 'OneSpace', 'url': BASE, 'logo': BASE + 'assets/icon-512.png',
         'slogan': 'Two of Us. One Space.'},
        {'@type': 'WebSite', '@id': BASE + '#site', 'name': 'OneSpace', 'url': BASE, 'inLanguage': ['en', 'ar', 'es', 'fr', 'de'], 'publisher': {'@id': BASE + '#org'}}]})
    # Paths are counted without the query string or #fragment, so nothing typed into a URL (or a confirmation token) is sent.
    analytics = ('\n<script>window.goatcounter={path:function(){return location.pathname}};</script>'
                 f'\n<script data-goatcounter="https://{GOATCOUNTER}.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>') if GOATCOUNTER else ''
    return f'''<!doctype html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta http-equiv="Content-Security-Policy" content="object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests">
<title data-ar="{escape(title_ar)}">{escape(title)}</title>
<meta name="description" content="{escape(desc)}" data-i18n-attr="content:{dk}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="en" href="{canonical}">
<link rel="alternate" hreflang="ar" href="{BASE}ar/{'' if page == 'index.html' else page}">
{''.join(f'<link rel="alternate" hreflang="{k}" href="{BASE}{k}/{"" if page == "index.html" else page}">' for k in NEW_LANGS)}
<link rel="alternate" hreflang="x-default" href="{canonical}">{verify}
<meta property="og:site_name" content="OneSpace">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="website">
<meta property="og:image" content="{BASE}assets/press/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#14213D">
<link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32.png">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/os.css">{analytics}
<script type="application/ld+json">{site_ld}</script>
</head>
<body>
<a class="skip" href="#main">{T('Skip to content', 'انتقل إلى المحتوى')}</a>
<header class="top"><div class="wrap">
  <a class="brand" href="./"><img src="assets/mark.svg" alt="" width="48" height="48"><span class="brand-name">OneSpace</span></a>
  <nav class="menu" aria-label="Main">{''.join(menu)}<a class="btn btn-primary menu-cta" href="join.html">{T('Join the Founding 500', 'انضم إلى المؤسسين الـ500')}</a></nav>
  <div class="actions">
    <details class="os-intl-languages"><summary aria-label="Languages / اللغات">🌐 Language</summary><div class="os-intl-languages-list"><a href="{canonical}" data-language-switch="en" lang="en">English</a><a href="{BASE}ar/{'' if page == 'index.html' else page}" data-language-switch="ar" lang="ar">العربية</a><a href="{BASE}es/{'' if page == 'index.html' else page}" data-language-switch="es" lang="es">Español</a><a href="{BASE}fr/{'' if page == 'index.html' else page}" data-language-switch="fr" lang="fr">Français</a><a href="{BASE}de/{'' if page == 'index.html' else page}" data-language-switch="de" lang="de">Deutsch</a></div></details>
    <a class="btn btn-primary btn-sm nav-join" href="join.html">{T('Join free', 'انضم مجانًا')}</a>
    <button class="burger" type="button" aria-label="Menu" aria-expanded="false">☰</button>
  </div>
</div></header>
<main id="main">
'''


def foot():
    def col(title, title_ar, links):
        items = ''.join(f'<li><a href="{h}">{T(e, a)}</a></li>' for h, e, a in links)
        return f'<div>{T(title, title_ar, "h4")}<ul>{items}</ul></div>'
    return f'''</main>
<footer><div class="wrap">
  <div class="foot">
    <div>
      <a class="brand" href="./"><img src="assets/mark.svg" alt="" width="48" height="48"><span class="brand-name">OneSpace</span></a>
      {N('Two of Us. One Space. A private home for your life — on your own or together, near or far.', 'p')}
      <p class="foot-mail"><a href="mailto:hello@onespace.live">hello@onespace.live</a></p>
      <div class="footer-social" aria-label="Social media channels coming soon">
        <span class="footer-social-item" role="img" aria-label="Instagram — coming soon"><span aria-hidden="true">◎</span><span class="footer-social-tooltip">Instagram</span></span>
        <span class="footer-social-item" role="img" aria-label="Facebook — coming soon"><span aria-hidden="true">f</span><span class="footer-social-tooltip">Facebook</span></span>
        <span class="footer-social-item" role="img" aria-label="YouTube — coming soon"><span aria-hidden="true">▶</span><span class="footer-social-tooltip">YouTube</span></span>
        <span class="footer-social-item" role="img" aria-label="TikTok — coming soon"><span aria-hidden="true">♪</span><span class="footer-social-tooltip">TikTok</span></span>
        <span class="footer-social-item" role="img" aria-label="LinkedIn — coming soon"><span aria-hidden="true">in</span><span class="footer-social-tooltip">LinkedIn</span></span>
      </div>
      <p class="footer-social-note">{T('Social channels coming soon', 'حسابات التواصل الاجتماعي قريبًا')}</p>
    </div>
    {col('Product', 'المنتج', [('features.html', 'Features', 'المزايا'), ('how-it-works.html', 'Interactive demo', 'العرض التفاعلي'), ('tutorials.html', 'Tutorials', 'الدروس'), ('whats-new.html', "What's new", 'الجديد'), ('whats-new.html#status', 'Availability', 'التوفر'), ('join.html', 'Founding 500', 'المؤسسون الـ500')])}
    {col('Who it’s for', _nov_ar('Who it’s for'), [('long-distance.html', 'Living apart', 'متباعدان'), ('living-together.html', 'Living together', 'تحت سقف واحد'), ('on-my-own.html', 'On my own', _nov_ar('On my own'))])}
    {col('Help', 'المساعدة', [('guides.html', 'Guides', _nov_ar('Guides')), ('faq.html', 'FAQ', 'الأسئلة الشائعة'), ('support.html', 'Contact & support', 'التواصل والدعم'), ('support.html#signin', "Can't sign in?", 'لا تستطيع الدخول؟'), ('share-kit.html', 'Share kit', 'مواد المشاركة')])}
    {col('Legal', 'قانوني', [('privacy.html', 'Privacy policy', 'سياسة الخصوصية'), ('terms.html', 'Terms of use', 'شروط الاستخدام'), ('delete-account.html', 'Delete your account', 'حذف حسابك')])}
  </div>
  <div class="foot-bottom">
    <span>© <span id="year">2026</span> OneSpace · {T('Founder registration open: Android & iPhone · App releases follow separately', 'التسجيل في عضوية المؤسسين مفتوح لأندرويد وآيفون · إصدار التطبيق لكل منصة في موعده')}</span>
    <span>{T('No ads. No data selling. Ever.', 'بلا إعلانات. بلا بيع للبيانات. أبدًا.')}</span>
  </div>
</div></footer>
<div class="sticky-cta" data-sticky-cta hidden><span>{T('The Founding 500 · free early access', 'المؤسسون الـ500 · وصول مبكر مجاني')}</span><a class="btn btn-primary btn-sm" href="join.html" data-track="sticky_join">{T('Join free', 'انضم مجانًا')}</a></div>
<script src="assets/ar.js" defer></script>
<script src="assets/os.js" defer></script>
</body>
</html>
'''


def page_hero(eyebrow, eyebrow_ar, h1, h1_ar, lead, lead_ar, crumbs=True, extra='', headline_html=None):
    c = f'<div class="crumbs"><a href="./">{T("Home", "الرئيسية")}</a> › {T(eyebrow, eyebrow_ar)}</div>' if crumbs else ''
    return f'''<section class="page-hero"><div class="wrap">
  {c}
  {f'<h1 class="editorial-hero-title">{headline_html}</h1>' if headline_html else T(h1, h1_ar, 'h1')}
  {T(lead, lead_ar, 'p', 'lead')}
  {extra}
</div></section>'''



def store_section():
    """Honest availability cards; no non-existent live store URLs or false launch claims."""
    return f'''<section id="get-the-app" class="store-arrival" aria-labelledby="get-app-title">
  <div class="wrap">
    <div class="sec-head center">
      {T('YOUR SPACE, SOON ON YOUR PHONE', 'مساحتكما قريبًا على هاتفكما', 'span', 'eyebrow')}
      <h2 id="get-app-title">{T('Find OneSpace on', 'ستجد OneSpace على')} <span class="serif accent">{T('your favorite phone.', 'هاتفك المفضّل.')}</span></h2>
      {T('Join the Founding 500 today — registration is open to both Android and iPhone users. We will invite you when your version is ready.', 'انضم الآن إلى المؤسسين الـ500. التسجيل مفتوح لمستخدمي أندرويد وآيفون، وسنرسل دعوتك عند جاهزية نسختك.', 'p', 'lead')}
    </div>
    <div class="store-arrival-grid">
      <article class="store-arrival-card android">
        <div class="store-arrival-head">
          <span class="store-emblem store-platform-google" aria-hidden="true"><svg class="store-platform-symbol" viewBox="0 0 48 48" focusable="false"><path d="M8 4.5v39l21-19.5z" fill="#34A853"/><path d="M8 4.5 32 17 29 24z" fill="#4285F4"/><path d="m29 24 3-7 11 5.8a3.5 3.5 0 0 1 0 6.2L32 31z" fill="#FBBC04"/><path d="m8 43.5 24-12.5-3-7z" fill="#EA4335"/></svg></span>
          <div>{T('ANDROID · FIRST', 'أندرويد · أولاً', 'span', 'store-eyebrow')}
            <h3>Google Play</h3></div>
        </div>
        <span class="store-status"><span aria-hidden="true">●</span>{N('Closed test on Google Play')}</span>
        {N('The Android app is in a closed test on Google Play. Join the Founding 500 and we will send your invitation. iPhone users are equally welcome to register.', 'p')}
        <a href="join.html" class="btn btn-primary" data-track="store_android_waitlist">{T('Join Android early access →', 'سجّل لتجربة أندرويد ←')}</a>
        {T('Not publicly available for download yet.', 'غير متاح للتحميل العام حتى الآن.', 'small', 'store-disclaimer')}
      </article>
      <article class="store-arrival-card iphone">
        <div class="store-arrival-head">
          <span class="store-emblem apple" aria-hidden="true"><svg class="store-platform-symbol" viewBox="0 0 48 48" focusable="false"><rect x="2" y="2" width="44" height="44" rx="10" fill="#1677ED"/><path d="M18.2 11.5 34 37.6M31.4 11.5 15.2 37.6M10.6 29.3h26.9" stroke="#fff" stroke-width="4.7" stroke-linecap="round"/><path d="m18.2 11.5 2.3 3.9" stroke="#fff" stroke-width="4.7" stroke-linecap="round"/></svg></span>
          <div>{T('IPHONE · COMING NEXT', 'آيفون · لاحقاً', 'span', 'store-eyebrow')}
            <h3>App Store</h3></div>
        </div>
        <span class="store-status"><span aria-hidden="true">●</span>{N('Coming soon via TestFlight')}</span>
        {N('Have an iPhone? Register now. The iPhone test is coming through TestFlight, and we will email you when it is ready.', 'p')}
        <a href="join.html" class="btn btn-ghost" data-track="store_iphone_waitlist">{T('Join as an iPhone Founder →', 'انضم كمؤسس على آيفون ←')}</a>
        {T('App Store link will be added after release.', 'هنضيف رابط App Store بعد الإطلاق.', 'small', 'store-disclaimer')}
      </article>
    </div>
    <p class="store-arrival-note">{T('Both buttons open Founder registration, not a download. You can register on either platform now, even though the release schedules differ.', 'كلا الزرين يؤدي إلى تسجيل المؤسسين لا إلى تنزيل التطبيق. يمكنك التسجيل الآن على أي من المنصتين رغم اختلاف مواعيد الإصدار.', 'span')}</p>
  </div>
</section>'''


def cta_band(h2='Ready when you are.', h2_ar=_nov_ar('Ready when you are.'),
             lead='Founder registration is open now on Android and iPhone. The first 500 people to join — on their own or as a couple — become Founder Members for free. The iPhone app follows the Android test.',
             lead_ar=_nov_ar('Founder registration is open now on Android and iPhone. The first 500 people to join — on their own or as a couple — become Founder Members for free. The iPhone app follows the Android test.')):
    return f'''<section><div class="wrap"><div class="band reveal"><div class="cta-band">
  <div>{T(h2, h2_ar, 'h2')}{T(lead, lead_ar, 'p', 'lead')}</div>
  <div class="cta-row" style="justify-content:flex-end">
    <a class="btn btn-primary" href="join.html">{T('Join the Founding 500', 'انضم إلى المؤسسين الـ500')}</a>
    <a class="btn btn-ghost" href="how-it-works.html">{T('Try the demo', 'جرّب العرض')}</a>
  </div>
</div></div></div></section>'''


# ------------------------------------------------------------------ phone illustrations
def phone(inner, theme='clean', cls='', label='', label_ar='', themable=True):
    t = ' data-themable' if themable else ''
    lk = K(label or 'OneSpace app screen', label_ar or 'شاشة من تطبيق OneSpace')
    return f'''<div class="phone {cls}" data-theme="{theme}"{t} role="img" aria-label="{escape(label or 'OneSpace app screen')}" data-i18n-attr="aria-label:{lk}">
<div class="scr"><div class="bar-top"><span>9:41</span><span>●●● ▮</span></div>{inner}</div></div>'''


def app_head(sub='Two of Us. One Space.', sub_ar='نحن الاثنان. مساحة واحدة.', bell=True):
    b = '<span class="bell">🔔<i></i></span>' if bell else ''
    return f'''<div class="app-head"><img src="assets/mark.svg" alt=""><div><b>OneSpace</b>{T(sub, sub_ar, 'small')}</div>{b}</div>'''


def nav_bar(on='today'):
    items = [('today', '📅', 'Today', 'اليوم'), ('remember', '🔖', 'Remember', 'تذكّر'), ('coordinate', '🧭', 'Coordinate', 'نسّق'),
             ('connect', '♡', 'Connect', 'تواصل'), ('smart-details', '⌕', 'Search & Notifications', 'البحث والإشعارات'), ('me', '👤', 'Me', 'أنا')]
    return '<div class="nav-b">' + ''.join(
        f'<span class="{"on" if k == on else ""}"><i>{i}</i>{T(e, a)}</span>' for k, i, e, a in items) + '</div>'


def row(icon, title, title_ar, sub='', sub_ar='', value='', value_ar='', small='', small_ar='', extra=''):
    v = f'<span class="rv">{T(value, value_ar or value)}{T(small, small_ar or small, "small") if small else ""}</span>' if value else ''
    s = T(sub, sub_ar or sub) if sub else ''
    return f'<div class="row"><span class="ri">{icon}</span><span class="rt">{T(title, title_ar, "b")}{s}{extra}</span>{v}</div>'


def scr_today(apart=True):
    if apart:
        place = f'''<div class="pc"><h4>✈️ {T('Living apart', 'متباعدان')}</h4>
  <div class="clocks"><div>{T('Omar · Toronto', 'عمر · تورونتو')}<b>12:14 PM</b><em>☀️ 18° · {T('clear', 'صافٍ')}</em></div>
  <div>{T('Lina · London', 'لينا · لندن')}<b>5:14 PM</b><em>🌧 9° · {T('good time to talk', 'وقت مناسب للحديث')}</em></div></div></div>'''
    else:
        place = f'''<div class="pc"><h4>🏡 {T('Together under one roof', 'معًا تحت سقف واحد')}</h4>
  {row('💗', 'One home, one shared space.', 'بيت واحد ومساحة مشتركة واحدة.', 'Your day together, at a glance', 'يومكما معًا في لمحة')}</div>'''
    return f'''{app_head()}<div class="body">
  {T('Good evening, Omar', 'مساء الخير، عمر', 'div', 'greet')}{T('Your space with Lina', 'مساحتك مع لينا', 'div', 'sub')}
  {place}
  <div class="pc"><h4>💌 {T('Since you were away', 'منذ غيابك')}</h4>
    {row('🤍', 'Lina sent you a hug', 'أرسلت لك لينا حضنًا', '“Sending you a big, warm hug.”', '«أرسل لك حضنًا كبيرًا ودافئًا.»', '2m', 'دقيقتان')}</div>
  <div class="pc"><h4>☑️ {T('Needs your attention', 'يحتاج انتباهك')} <span class="n">2</span></h4>
    {row('🧭', 'Choose our weekend plan', 'اختر خطة عطلتنا', 'Activity · 2 options', 'نشاط · خياران')}
    {row('🎁', 'Order the anniversary gift', 'اطلب هدية الذكرى', 'Occasion · due Thu', 'مناسبة · الخميس')}</div>
  <div class="pc"><h4>📅 {T('Today and the next 7 days', 'اليوم والأيام السبعة القادمة')}</h4>
    {row('🎬', 'Movie night', 'سهرة فيلم', 'Fri · 9:00 PM', 'الجمعة · 9:00 م')}
    {row('✈️', 'Flight to Istanbul', 'رحلة إلى إسطنبول', 'Sat · 7:40 AM', 'السبت · 7:40 ص')}</div>
</div><span class="fab">＋ {T('Quick add', 'إضافة سريعة')}</span>{nav_bar('today')}'''


def scr_ourspace():
    def tiles(items):
        return '<div class="tiles">' + ''.join(f'<div><i>{i}</i>{T(e, a)}</div>' for i, e, a in items) + '</div>'
    return f'''{app_head()}<div class="body">
  {T('Our space', 'مساحتنا', 'div', 'greet')}
  {T('Plan together', 'خططا معًا', 'div', 'grp')}
  {tiles([('📅', 'Calendar', 'التقويم'), ('☑️', 'To-do lists', 'قوائم المهام'), ('⏰', 'Reminders', 'التذكيرات'), ('🧭', 'Activities', 'الأنشطة'), ('✈️', 'Trips', 'الرحلات'), ('🎁', 'Occasions', 'المناسبات')])}
  {T('Stay close', 'ابقيا قريبين', 'div', 'grp')}
  {tiles([('💌', 'Letters', 'الرسائل'), ('🤍', 'A little love', 'لمسة حب'), ('🌤', 'Daily connection', 'التواصل اليومي'), ('🎬', 'Experiences', 'التجارب'), ('📸', 'Memories', 'الذكريات'), ('📍', 'Our places', 'أماكننا')])}
  {T('Remember', 'تذكّر', 'div', 'grp')}
  {tiles([('📝', 'Notes', 'الملاحظات'), ('👤', 'Contact cards', 'بطاقات التواصل'), ('⏳', 'Counters', 'العدّادات')])}
</div>{nav_bar('today')}'''


def scr_quickadd():
    items = [('⏰', 'Reminder', 'تذكير'), ('☑️', 'To-do', 'مهمة'), ('📅', 'Event', 'موعد'), ('📝', 'Note', 'ملاحظة'),
             ('🔎', 'Research', 'بحث'), ('🎁', 'Gift idea', 'فكرة هدية'), ('✈️', 'Trip', 'رحلة'), ('📸', 'Story', 'قصة'),
             ('🌤', 'Daily feeling', 'شعور اليوم'), ('💌', 'Letter', 'رسالة'), ('🤍', 'A little love', 'لمسة حب'), ('📍', 'Place', 'مكان')]
    qa = ''.join(f'<div><i>{i}</i>{T(e, a)}</div>' for i, e, a in items)
    return f'''{app_head()}<div class="body" style="opacity:.35">
  {T('Good evening, Omar', 'مساء الخير، عمر', 'div', 'greet')}
  <div class="pc" style="height:90px"></div><div class="pc" style="height:120px"></div></div>
  <div class="sheet">{T('Quick add', 'إضافة سريعة', 'div', 'greet')}<div style="height:8px"></div><div class="qa">{qa}</div></div>'''


def scr_counters():
    return f'''<div class="app-head"><b style="font-size:15px">← {T('Counters', 'العدّادات')}</b></div><div class="body">
  <div class="pc" style="text-align:center;background:color-mix(in srgb,var(--p) 14%,var(--pcard))">
    <div>📌 {T('Our 6th anniversary', 'ذكرانا السادسة')}</div>
    <b style="font-size:30px;display:block;color:var(--p)">{T('5 months', '5 أشهر')}</b>{T('15 days to go', 'و15 يومًا متبقية')}
    <div class="prog"><i style="width:58%"></i></div></div>
  <div class="pc">{row('✈️', 'Trip to Istanbul', 'رحلة إلى إسطنبول', 'Sat 22 Nov · next trip', 'السبت 22 نوفمبر · الرحلة القادمة', '6 days', '6 أيام', 'to go', 'متبقية')}<div class="prog"><i style="width:82%"></i></div></div>
  <div class="today-line">{T('Today', 'اليوم')}</div>
  <div class="pc agebar" style="--w:30%">{row('💍', 'Wedding day', 'يوم الزفاف', '1 May 2021 · the day itself', '1 مايو 2021 · اليوم نفسه', '5 years', '5 سنوات', '6 months since', 'و6 أشهر مضت')}</div>
  <div class="pc agebar" style="--w:62%">{row('☕', 'Our first date', 'موعدنا الأول', '2 Mar 2019', '2 مارس 2019', '7 years', '7 سنوات', 'since', 'مضت')}</div>
  <div class="pc agebar" style="--w:100%">{row('💞', 'The day we met', 'يوم التقينا', '14 Sep 2018', '14 سبتمبر 2018', '8 years', '8 سنوات', 'since', 'مضت')}</div>
</div>{nav_bar('remember')}'''


def scr_places():
    return f'''<div class="app-head"><b style="font-size:15px">← {T('Our places', 'أماكننا')}</b><span class="bell">🗺️</span></div><div class="body">
  <div class="map"><span class="pin" style="left:30%;top:45%">❤️</span><span class="pin" style="left:62%;top:38%">❤️</span>
    <span class="pin" style="left:48%;top:78%">🧭</span><span class="pin" style="left:80%;top:70%">🧭</span></div>
  <div style="display:flex;gap:6px"><span class="chip">❤️ {T('Been there', 'زرناه')}</span><span class="chip">🧭 {T('Bucket list', 'قائمة الأحلام')}</span></div>
  <div class="pc">{row('☕', 'Our café', 'مقهانا', 'Toronto · 12 visits · ★★★★★', 'تورونتو · 12 زيارة · ★★★★★')}
    {row('🏖', 'Cascais', 'كاشكايش', 'Portugal · first time 2023', 'البرتغال · أول مرة 2023')}
    {row('🗼', 'Santorini', 'سانتوريني', 'Bucket list · tick to plan a trip', 'قائمة الأحلام · اختر لتخطط لرحلة', '☐')}</div>
</div>{nav_bar('remember')}'''


def scr_trip():
    return f'''<div class="app-head"><b style="font-size:15px">← {T('Trip', 'الرحلة')}</b></div><div class="body">
  {T('Istanbul for our anniversary', 'إسطنبول في ذكرانا', 'div', 'greet')}
  <div style="display:flex;gap:6px;flex-wrap:wrap"><span class="chip">YYZ → IST</span><span class="chip">{T('Booked', 'محجوزة')}</span><span class="chip">👥 2</span></div>
  <div class="pc"><h4>✈️ {T('Flights', 'الطيران')}</h4>
    {row('🛫', 'YYZ → IST · Sat 07:40', 'تورونتو ← إسطنبول · السبت 07:40', '1 stop · 2 cabin bags', 'توقف واحد · حقيبتا مقصورة', '$1,180', '1,180 دولار')}
    {row('🛬', 'IST → YYZ · Thu 18:05', 'إسطنبول ← تورونتو · الخميس 18:05', 'Direct · seat 14A', 'مباشر · مقعد 14A')}</div>
  <div class="pc"><h4>🧳 {T('Packing', 'التجهيز')} <span class="n">7/12</span></h4><div class="prog"><i style="width:58%"></i></div>
    {row('🛂', 'Passports and visas', 'الجوازات والتأشيرات', 'Lina · done', 'لينا · تم')}
    {row('🔌', 'Travel adapter', 'محوّل الكهرباء', 'Omar', 'عمر')}</div>
  <div class="pc"><h4>📄 {T('Travel documents', 'مستندات السفر')}</h4>{row('🏨', 'Hotel booking.pdf', 'حجز الفندق.pdf', 'Only us two can open it', 'لا يفتحه سوانا')}</div>
</div>{nav_bar('coordinate')}'''


def scr_love():
    g = [('🤗', 'Hug', 'حضن'), ('💋', 'Kiss', 'قبلة'), ('😊', 'Smile', 'ابتسامة'), ('☀️', 'Good morning', 'صباح الخير'),
         ('🌙', 'Goodnight', 'تصبح على خير'), ('🏅', 'Proud of you', 'فخور بك'), ('🫶', 'Thank you', 'شكرًا'), ('📞', 'Call me', 'اتصل بي'), ('🍀', 'Lucky to have you', 'محظوظ بك')]
    tiles = ''.join(f'<div><i>{i}</i>{T(e, a)}</div>' for i, e, a in g)
    return f'''<div class="app-head"><b style="font-size:15px">← {T('A little love', 'لمسة حب')}</b></div><div class="body">
  <div class="pc" style="background:color-mix(in srgb,var(--p) 12%,var(--pcard))">{row('🤍', 'Lina sent you a hug', 'أرسلت لك لينا حضنًا', '“Sending you a big, warm hug.”', '«أرسل لك حضنًا كبيرًا ودافئًا.»')}</div>
  {T('Send a little love', 'أرسل لمسة حب', 'div', 'grp')}
  <div class="tiles">{tiles}</div>
  <div class="pc"><h4>✍️ {T('Your words', 'كلماتك')}</h4>
    {row('🤗', 'Hug', 'حضن', '“Can’t wait to see you tonight.”', '«لا أطيق الانتظار لرؤيتك الليلة.»', 'Send', 'أرسل')}</div>
  <div class="pc"><h4>⏰ {T('Private nudge', 'تذكير خاص')}</h4>
    {row('🔔', 'Remind me to send a little love', 'ذكّرني بإرسال لمسة حب', 'Only me · weekdays 6:00 PM', 'أنا فقط · أيام العمل 6:00 م')}</div>
</div>{nav_bar('connect')}'''


def scr_letter():
    return f'''<div class="app-head"><b style="font-size:15px">← {T('Letters', 'الرسائل')}</b></div><div class="body">
  <div class="pc" style="text-align:center;padding:18px 12px"><div style="font-size:40px">💌</div>
    {T('A letter from Lina', 'رسالة من لينا', 'b')}<div class="sub">{T('Sealed until our anniversary · 1 May', 'مغلقة حتى ذكرانا · 1 مايو')}</div>
    <div class="prog"><i style="width:64%"></i></div></div>
  <div class="pc"><h4>✍️ {T('Your letters', 'رسائلك')}</h4>{row('📮', 'For the day you land', 'ليوم وصولك', 'Opens on Sat 22 Nov', 'تُفتح السبت 22 نوفمبر')}{row('📖', 'Just because', 'بلا مناسبة', 'Read by Lina · 3 Nov', 'قرأتها لينا · 3 نوفمبر')}</div>
  <div class="pc"><h4>🌤 {T('Daily connection', 'التواصل اليومي')}</h4>{row('😊', 'Lina felt great today', 'شعرت لينا اليوم بأنها رائعة', '“Finished the big project!”', '«أنهيت المشروع الكبير!»')}</div>
</div>{nav_bar('connect')}'''


def scr_occasion():
    return f'''<div class="app-head"><b style="font-size:15px">← {T('Occasion', 'المناسبة')}</b></div><div class="body">
  {T("Lina's birthday", 'عيد ميلاد لينا', 'div', 'greet')}<div class="sub">🔒 {T('Only me · a surprise', 'أنا فقط · مفاجأة')}</div>
  <div class="pc"><h4>💰 {T('Occasion budget', 'ميزانية المناسبة')}</h4><b style="font-size:20px">$370</b> <span class="sub">{T('left of $600', 'متبقٍ من 600 دولار')}</span><div class="prog"><i style="width:38%"></i></div></div>
  <div class="pc"><h4>🎁 {T('Gift ideas', 'أفكار الهدايا')} <span class="n">4</span></h4>{row('💐', 'Flowers + dinner', 'ورود وعشاء', 'Reserved', 'محجوز', '$160', '160 دولار')}{row('📷', 'Instant camera', 'كاميرا فورية', 'Considering · ★★★★', 'قيد الدراسة · ★★★★', '$120', '120 دولار')}</div>
  <div class="pc"><h4>🗓 {T('Plan', 'الخطة')}</h4>{row('⏰', 'Start preparing', 'ابدأ التحضير', '3 weeks before', 'قبل 3 أسابيع')}</div>
</div>{nav_bar('remember')}'''


def scr_activity():
    return f'''<div class="app-head"><b style="font-size:15px">← {T('Activity', 'النشاط')}</b></div><div class="body">
  {T('A new sofa', 'أريكة جديدة', 'div', 'greet')}<div class="sub">{T('Exploring · compare 2 options', 'قيد البحث · مقارنة خيارين')}</div>
  <div class="pc"><h4>⚖️ {T('Options', 'الخيارات')}</h4>{row('🛋', 'Grey corner sofa', 'أريكة زاوية رمادية', 'Omar ♥ · Lina ?', 'عمر ♥ · لينا ؟', '$1,400', '1,400 دولار')}{row('🛋', 'Velvet 3-seater', 'أريكة مخمل لثلاثة', 'Omar ? · Lina ♥', 'عمر ؟ · لينا ♥', '$1,150', '1,150 دولار')}</div>
  <div class="pc"><h4>💬 {T('Conversation', 'المحادثة')}</h4>{row('🎙', 'Voice note · 0:12', 'رسالة صوتية · 0:12', 'Lina')}{row('💬', '“The velvet one fits the window”', '«المخمل يناسب النافذة»', 'Omar')}</div>
  <div class="pc"><h4>✅ {T('Decision', 'القرار')}</h4>{row('🛋', 'Velvet 3-seater', 'أريكة مخمل لثلاثة', 'Decided together', 'قررناها معًا')}</div>
</div>{nav_bar('coordinate')}'''


def scr_arabic():
    return f'''<div dir="rtl" style="display:flex;flex-direction:column;height:100%;font-family:var(--font-ar)">
  <div class="app-head"><img src="assets/mark.svg" alt=""><div><b>OneSpace</b><small>نحن الاثنان، مساحة واحدة</small></div><span class="bell">🔔<i></i></span></div>
  <div class="body"><div class="greet">صباح الخير، لينا</div><div class="sub">مساحتك مع عمر</div>
  <div class="pc"><h4>✈️ متباعدان</h4><div class="clocks"><div><span>لينا · لندن</span><b>8:02 ص</b><em>🌧 9°</em></div><div><span>عمر · تورونتو</span><b>3:02 ص</b><em>🌙 12°</em></div></div></div>
  <div class="pc"><h4>💌 منذ غيابك</h4><div class="row"><span class="ri">☀️</span><span class="rt"><b>عمر يقول صباح الخير</b><span>«يومك جميل يا حبيبتي»</span></span></div></div>
  <div class="pc"><h4>📅 اليوم والأيام السبعة القادمة</h4><div class="row"><span class="ri">✈️</span><span class="rt"><b>رحلة إلى إسطنبول</b><span>السبت · 7:40 ص</span></span></div></div>
  </div><div class="nav-b"><span class="on"><i>📅</i>اليوم</span><span><i>🔖</i>تذكّر</span><span><i>🧭</i>نسّق</span><span><i>♡</i>تواصل</span><span><i>👤</i>أنا</span></div></div>'''


def scr_memories():
    return f'''<div class="app-head"><b style="font-size:15px">← {T('Memories', 'الذكريات')}</b></div><div class="body">
  <div class="pc" style="padding:0;overflow:hidden"><div style="height:120px;background:linear-gradient(135deg,#F6C9B8,#BFD9DC);display:grid;place-items:center;font-size:42px">🌅</div>
    <div style="padding:10px 12px">{T('Sunset in Alexandria', 'غروب في الإسكندرية', 'b')}<div class="sub">{T('Story · 3 photos · 12 Aug', 'قصة · 3 صور · 12 أغسطس')}</div></div></div>
  <div class="pc"><h4>🤳 {T('Daily selfie · both of you', 'سيلفي اليوم · كلاكما')}</h4><div style="display:grid;grid-template-columns:1fr 1fr;gap:6px"><div style="height:62px;border-radius:10px;background:#F7D8C9;display:grid;place-items:center;font-size:24px">🙂</div><div style="height:62px;border-radius:10px;background:#D3E6E7;display:grid;place-items:center;font-size:24px">😄</div></div></div>
  <div class="pc">{row('📒', 'Our year · scrapbook', 'سنتنا · ألبوم قصاصات', '12 pages · save as PDF', '12 صفحة · احفظ كـ PDF')}</div>
</div>{nav_bar('remember')}'''


def scr_share():
    sug = [('🎬', 'Shared experience', 'تجربة مشتركة', 'Watchlist · Movies', 'قائمة المشاهدة · أفلام'), ('🧭', 'New Activity', 'نشاط جديد', '', ''), ('📝', 'Note', 'ملاحظة', '', '')]
    rows = ''.join(row(i, e, a, se, sa) for i, e, a, se, sa in sug)
    return f"""<div class="body" style="opacity:.35;padding-top:30px"><div class="pc" style="height:140px"></div><div class="pc" style="height:120px"></div></div>
  <div class="sheet">{T('Save to OneSpace', 'احفظ في OneSpace', 'div', 'greet')}
    <div class="pc" style="margin:8px 0">{row('▶️', 'Before Sunrise (1995)', 'قبل الشروق (1995)', 'netflix.com/title/…', 'netflix.com/title/…')}</div>
    {T('Suggested for this link', 'مقترح لهذا الرابط', 'div', 'grp')}<div class="pc">{rows}</div>
    <div style="margin-top:8px;background:var(--p);color:#fff;border-radius:12px;padding:9px;text-align:center;font-weight:800">{T('Save as Shared experience', 'احفظ كتجربة مشتركة')}</div></div>"""


def scr_watch():
    return f"""<div class="app-head"><b style="font-size:15px">← {T('Shared experiences', 'التجارب المشتركة')}</b></div><div class="body">
  <div style="display:flex;gap:5px;flex-wrap:wrap">{''.join(f'<span class="chip" style="font-size:9px;padding:3px 8px">{T(e, a)}</span>' for e, a in [('Movies', 'أفلام'), ('TV', 'مسلسلات'), ('Music', 'موسيقى'), ('Books', 'كتب'), ('Games', 'ألعاب')])}</div>
  <div class="pc" style="background:color-mix(in srgb,var(--p) 13%,var(--pcard))"><h4>✨ {T('What shall we do together?', 'ماذا نفعل معًا؟')}</h4>{row('🎬', 'Before Sunrise', 'قبل الشروق', 'A mutual pick · Prime Video', 'اختيار مشترك · برايم فيديو')}</div>
  <div class="pc"><h4>💞 {T('Mutual picks', 'اختيارات مشتركة')} <span class="n">3</span></h4>
    {row('📺', 'The Great British Bake Off', 'مسابقة الخَبز البريطانية', 'Planned · Fri 9 PM', 'مخطط · الجمعة 9 م')}
    {row('🎵', 'Our wedding playlist', 'قائمة أغاني زفافنا', 'Music · Spotify', 'موسيقى · سبوتيفاي')}
    {row('📖', 'The Little Prince', 'الأمير الصغير', 'Book · a chapter each', 'كتاب · فصل لكل منا')}</div>
  <div class="pc"><h4>⭐ {T('Our ratings', 'تقييماتنا')}</h4>{row('🎞', 'Before Sunrise', 'قبل الشروق', 'Omar ★★★★ · Lina ★★★★★', 'عمر ★★★★ · لينا ★★★★★')}</div>
</div>{nav_bar('connect')}"""


def scr_contacts():
    return f"""<div class="app-head"><b style="font-size:15px">← {T('Contact cards', 'بطاقات التواصل')}</b></div><div class="body">
  <div class="pc" style="color:var(--pmuted)">🔎 {T('Search contact cards', 'ابحث في بطاقات التواصل')}</div>
  <div class="pc">{row('🦷', 'Dr. Sara — dentist', 'د. سارة — طبيبة الأسنان', 'Smile Clinic · Sun–Thu 9–21', 'عيادة الابتسامة · الأحد–الخميس 9–21')}
    {row('🔧', 'Building maintenance', 'صيانة المبنى', 'Faisal · WhatsApp is fastest', 'فيصل · الواتساب أسرع')}
    {row('🏊', 'Kids’ swim club', 'نادي السباحة للأطفال', 'From the Activity “Summer plans”', 'من نشاط «خطط الصيف»')}</div>
  <div class="pc"><h4>📇 {T('Dr. Sara — dentist', 'د. سارة — طبيبة الأسنان')}</h4>
    <div style="display:flex;gap:6px;flex-wrap:wrap">{''.join(f'<span class="chip" style="font-size:9px;padding:3px 8px">{i} {T(e, a)}</span>' for i, e, a in [('📞', 'Call', 'اتصال'), ('💬', 'WhatsApp', 'واتساب'), ('🗺', 'Directions', 'الاتجاهات'), ('📲', 'Save to phone', 'احفظ في الهاتف')])}</div></div>
  <div class="pc" style="background:color-mix(in srgb,var(--p) 12%,var(--pcard))">{row('📥', 'Import from phone', 'استيراد من الهاتف', 'Duplicates are spotted for you', 'يكتشف التكرار تلقائيًا')}</div>
</div>{nav_bar('remember')}"""


SCREENS = {'today': scr_today, 'ourspace': scr_ourspace, 'quickadd': scr_quickadd, 'counters': scr_counters,
           'places': scr_places, 'trip': scr_trip, 'love': scr_love, 'letter': scr_letter, 'occasion': scr_occasion,
           'activity': scr_activity, 'arabic': scr_arabic, 'memories': scr_memories}


def _bar(title, title_ar):
    return f'<div class="app-head"><b style="font-size:15px">← {T(title, title_ar)}</b></div>'


def bubble(text, text_ar, mine=False, who=''):
    side = 'margin-inline-start:auto;background:var(--p);color:#fff' if mine else 'background:var(--pcard)'
    w = f'<div style="font-size:9px;opacity:.75">{who}</div>' if who else ''
    return f'<div style="max-width:78%;border-radius:14px;padding:7px 10px;{side};box-shadow:0 4px 10px -8px rgba(0,0,0,.4)">{w}{T(text, text_ar)}</div>'


def scr_demo_note():
    return f"""{_bar('Note', 'ملاحظة')}<div class="body">
  {T('Weekend away ideas', 'أفكار لعطلة نهاية الأسبوع', 'div', 'greet')}<div class="sub">📌 {T('Pinned · shared with Lina', 'مثبتة · مشتركة مع لينا')}</div>
  <div class="pc" style="line-height:1.6">{T('<b>Somewhere quiet, 2 nights</b><br>• Banff — stars and the mountains<br>• Muskoka — a lake cabin, canoe at sunrise<br>• Budget around $800', '<b>مكان هادئ، ليلتان</b><br>• بانف — النجوم والجبال<br>• موسكوكا — كوخ على البحيرة وتجديف عند الشروق<br>• الميزانية نحو 800 دولار')}</div>
  <div class="pc">{row('🔗', 'Banff stargazing tour', 'جولة مراقبة النجوم في بانف', 'link · added by Lina', 'رابط · أضافته لينا')}</div>
  <div class="pc" style="background:color-mix(in srgb,var(--p) 12%,var(--pcard))">{row('🧭', 'Create from this → Activity', 'أنشئ من هذه ← نشاط', 'Turn the ideas into options to compare', 'حوّل الأفكار إلى خيارات للمقارنة')}</div>
</div>{nav_bar('remember')}"""


def scr_demo_activity():
    return f"""{_bar('Activity', 'النشاط')}<div class="body">
  {T('Weekend away', 'عطلة نهاية الأسبوع', 'div', 'greet')}<div class="sub">{T('Exploring · Fri 28 Nov · 2 options', 'قيد البحث · الجمعة 28 نوفمبر · خياران')}</div>
  <div class="pc"><h4>⚖️ {T('Options', 'الخيارات')}</h4>
    {row('🏔', 'Banff, 2 nights', 'بانف، ليلتان', 'Omar ♥ · Lina ?', 'عمر ♥ · لينا ؟', '$760', '760 دولار')}
    {row('🛶', 'Muskoka, 2 nights', 'موسكوكا، ليلتان', 'Omar ? · Lina ?', 'عمر ؟ · لينا ؟', '$540', '540 دولار')}</div>
  <div class="pc"><h4>📎 {T('Linked', 'مرتبط')}</h4>{row('📝', 'Weekend away ideas', 'أفكار لعطلة نهاية الأسبوع', 'Note', 'ملاحظة')}</div>
  <div class="pc" style="background:color-mix(in srgb,var(--p) 12%,var(--pcard))">{row('🔔', 'Lina was asked to pick', 'طُلب من لينا الاختيار', 'Shows in her Needs your attention', 'يظهر في «يحتاج انتباهك» لديها')}</div>
</div>{nav_bar('coordinate')}"""


def scr_demo_chat():
    return f"""{_bar('Our conversation', 'محادثتنا')}<div class="body" style="gap:7px">
  {bubble('Banff looks magical — @Lina what do you think?', 'بانف تبدو ساحرة — @لينا ما رأيك؟', True)}
  {bubble('🎙 Voice note · 0:14', '🎙 رسالة صوتية · 0:14', False, 'Lina')}
  {bubble('Yes! But can we do Muskoka for your birthday?', 'نعم! لكن هل نجعل موسكوكا لعيد ميلادك؟', False, 'Lina')}
  {bubble('Deal 🤝 Banff now, Muskoka in March', 'اتفقنا 🤝 بانف الآن وموسكوكا في مارس', True)}
  <div class="pc">{row('♥', 'Lina picked Banff', 'اختارت لينا بانف', 'Both of you agree', 'كلاكما متفقان')}</div>
  <div class="pc" style="display:flex;gap:6px;align-items:center;margin-top:auto"><span style="flex:1;color:var(--pmuted)">{T('Write a message… type @ to mention', 'اكتب رسالة… اكتب @ للإشارة')}</span>🎙</div>
</div>{nav_bar('coordinate')}"""


def scr_demo_decision():
    return f"""{_bar('Activity', 'النشاط')}<div class="body">
  {T('Weekend away', 'عطلة نهاية الأسبوع', 'div', 'greet')}<div class="sub">✅ {T('Decided together', 'قررناها معًا')}</div>
  <div class="pc" style="background:color-mix(in srgb,var(--p) 12%,var(--pcard))"><h4>✅ {T('Decision', 'القرار')}</h4>{row('🏔', 'Banff, 2 nights', 'بانف، ليلتان', 'Fri 28 – Sun 30 Nov', 'الجمعة 28 – الأحد 30 نوفمبر', '$760', '760 دولار')}</div>
  <div class="pc"><h4>📎 {T('Linked items', 'العناصر المرتبطة')}</h4>
    {row('📅', 'Calendar · Banff weekend', 'التقويم · عطلة بانف', 'Fri 28 Nov, all weekend', 'الجمعة 28 نوفمبر، طوال العطلة')}
    {row('⏰', 'Reminder · book the hotel', 'تذكير · احجز الفندق', 'Omar · tomorrow 9:00 AM', 'عمر · غدًا 9:00 ص')}
    {row('📝', 'Weekend away ideas', 'أفكار لعطلة نهاية الأسبوع', 'Note', 'ملاحظة')}</div>
</div>{nav_bar('coordinate')}"""


def scr_demo_connect():
    return f"""{_bar('A little love', 'لمسة حب')}<div class="body">
  <div class="pc" style="text-align:center;padding:16px 12px"><div style="font-size:38px">🤗</div>{T('Send Lina a hug', 'أرسل لينا حضنًا', 'b')}
    <div class="pc" style="margin-top:8px;text-align:start;background:var(--pbg)">{T('“Can’t wait for our stars weekend.”', '«لا أطيق الانتظار لعطلة النجوم.»')}</div>
    <div style="margin-top:8px;background:var(--p);color:#fff;border-radius:12px;padding:8px;font-weight:800">{T('Send', 'أرسل')}</div></div>
  <div class="pc"><h4>📸 {T('Afterwards: keep the memory', 'بعدها: احفظا الذكرى')}</h4>{row('🌌', 'Under the Banff stars', 'تحت نجوم بانف', 'Story · 8 photos · Sun 30 Nov', 'قصة · 8 صور · الأحد 30 نوفمبر')}{row('📍', 'Banff moved to “Been there”', 'انتقلت بانف إلى «زرناه»', 'Our places', 'أماكننا')}</div>
</div>{nav_bar('connect')}"""


SCREENS.update({'share': scr_share, 'watch': scr_watch, 'contacts': scr_contacts})
SCREENS.update({'demo_note': scr_demo_note, 'demo_activity': scr_demo_activity, 'demo_chat': scr_demo_chat,
                'demo_decision': scr_demo_decision, 'demo_connect': scr_demo_connect})


# ------------------------------------------------------------------ real app screenshots (v7)
APP = ROOT / 'assets' / 'app'


def has_shot(name, lang='en'):
    return (APP / lang / (name if name.endswith('.png') else f'{name}.webp')).exists()


def device(name, alt, alt_ar, cls='', fallback='', themed=False):
    """A real app screenshot (made by the demo-couple robot) in a phone frame.
    Switches to the Arabic screenshot when the page is in Arabic. Falls back to
    the HTML illustration while the robot hasn't produced that screen yet."""
    if not has_shot(name):
        return fallback
    file_name = name if name.endswith('.png') else f'{name}.webp'
    en = f'assets/app/en/{file_name}'
    ar = f'assets/app/ar/{file_name}' if has_shot(name, 'ar') else en
    k = K(alt, alt_ar)
    t = ' data-theme-img' if themed else ''
    return (f'<div class="device {cls}"><img src="{en}" data-en-src="{en}" data-ar-src="{ar}"{t} alt="{escape(alt)}" '
            f'data-i18n-attr="alt:{k}" width="720" height="1600" loading="lazy" decoding="async"></div>')


REAL = {  # illustration key -> robot screenshot name
    'today': 'today', 'ourspace': 'connect', 'quickadd': 'quickadd', 'counters': 'counters', 'places': 'places_map',
    'trip': 'trip', 'love': 'love', 'letter': 'letters', 'occasion': 'occasion', 'activity': 'decision',
    'memories': 'memories', 'demo_note': 'notes', 'demo_activity': 'activity', 'demo_chat': 'activity_chat',
    'demo_decision': 'decision', 'demo_connect': 'love'}


def screen(key, theme, alt, alt_ar, cls='', real=None):
    """Real screenshot when the robot has made it, else the HTML illustration."""
    name = real or REAL.get(key, key)
    return device(name, alt, alt_ar, cls, fallback=phone(SCREENS[key](), theme, cls, alt, alt_ar))


def clip(name, alt, alt_ar, cls=''):
    """A short tutorial clip recorded from the real app (muted, looping)."""
    if not (APP / 'video' / f'en_{name}.mp4').exists():
        return ''
    en, ar = f'assets/app/video/en_{name}', f'assets/app/video/ar_{name}'
    if not (APP / 'video' / f'ar_{name}.mp4').exists():
        ar = en
    k = K(alt, alt_ar)
    return (f'<div class="device {cls}"><video src="{en}.mp4" poster="{en}.jpg" data-en-src="{en}.mp4" data-ar-src="{ar}.mp4" '
            f'data-en-poster="{en}.jpg" data-ar-poster="{ar}.jpg" muted loop playsinline data-autoplay preload="none" '
            f'aria-label="{escape(alt)}" data-i18n-attr="aria-label:{k}"></video></div>')


# ------------------------------------------------------------------ pages
def snip(name, alt, alt_ar):
    if not has_shot(f'snip/{name}'):
        return ''
    en = f'assets/app/en/snip/{name}.webp'
    ar = f'assets/app/ar/snip/{name}.webp' if has_shot(f'snip/{name}', 'ar') else en
    k = K(alt, alt_ar)
    return (f'<div class="snip"><img src="{en}" data-en-src="{en}" data-ar-src="{ar}" alt="{escape(alt)}" '
            f'data-i18n-attr="alt:{k}" loading="lazy" decoding="async"></div>')


def pain(them, them_ar, me, me_ar, ans, ans_ar, who='Lina', who_ar='لينا', shot=''):
    return f"""<div class="pain reveal"><div class="msg them">{T(them, them_ar)}<small>{T(who, who_ar)}</small></div>
  <div class="msg me">{T(me, me_ar)}</div>
  <div class="answer"><b>OneSpace</b>{T(ans, ans_ar)}</div>{snip(shot, ans, ans_ar) if shot else ''}</div>"""


def slot(time, text, text_ar):
    return f'<div class="slot reveal"><time>{time}</time><div class="bubble">{T(text, text_ar)}</div></div>'


def cities_panel():
    return f"""<div class="cities">
    <div class="split" style="gap:40px;align-items:start">
      <div>{T('A day in two cities', 'يوم في مدينتين', 'span', 'eyebrow')}{T('5,700 km, one shared day.', '5,700 كم، ويوم مشترك واحد.', 'h3', '', 'style="font-size:30px;margin:10px 0 0"')}
        <svg class="route" viewBox="0 0 400 120" aria-hidden="true"><path class="arc" d="M30 95 Q200 -20 370 95" fill="none" stroke="#F3A27E" stroke-width="2.5"/><circle cx="30" cy="95" r="7" fill="#F3A27E"/><circle cx="370" cy="95" r="7" fill="#7FC4CC"/><text x="200" y="40" text-anchor="middle" font-size="22">✈️</text></svg>
        <div class="city-row"><div class="city">{T('Toronto · Omar', 'تورونتو · عمر')}<b>12:14 PM</b><span>☀️ 18° · {T('lunchtime', 'وقت الغداء')}</span></div><div class="city">{T('London · Lina', 'لندن · لينا')}<b>5:14 PM</b><span>🌧 9° · {T('good time to talk', 'وقت مناسب للحديث')}</span></div></div>
        <a class="btn btn-primary" style="margin-top:24px" href="long-distance.html">{T('OneSpace for long distance →', 'OneSpace للعلاقات عن بُعد ←')}</a></div>
      <div class="day">
        {slot('07:40', '<b>Lina</b> wakes up to “Good morning ☀️” Omar sent before bed.', '<b>لينا</b> تستيقظ على «صباح الخير ☀️» أرسلها عمر قبل نومه.')}
        {slot('12:10', '<b>Omar</b> adds the flight to Istanbul — YYZ → IST, Saturday 07:40.', '<b>عمر</b> يضيف رحلة إسطنبول — تورونتو ← إسطنبول، السبت 07:40.')}
        {slot('17:14', 'Today says it is <b>a good time to talk</b> in London. They call.', '«اليوم» يقول إنه <b>وقت مناسب للحديث</b> في لندن. يتصلان.')}
        {slot('21:30', '<b>Lina</b> ticks “Passports” on the packing list. 7 of 12 done.', '<b>لينا</b> تضع علامة على «الجوازات» في قائمة التجهيز. 7 من 12.')}
        {slot('23:55', 'The reunion counter flips to <b>5 days</b>. ✈️', 'عدّاد اللقاء يصبح <b>5 أيام</b>. ✈️')}
      </div></div></div>"""


def home_panel():
    return f"""<div class="split">
    <div class="stage">{device('together/today', 'Today for a couple living together', 'اليوم لزوجين يعيشان معًا', fallback=phone(scr_today(False), 'coral', label='Today for a couple living together', label_ar='اليوم لزوجين يعيشان معًا', themable=False))}</div>
    <div>{T('One home, shared load', 'بيت واحد وعبء مشترك', 'span', 'eyebrow')}{T('Nobody has to be the household’s memory.', 'لا أحد مضطر لأن يكون ذاكرة البيت.', 'h3', '', 'style="font-size:30px;margin:10px 0 18px"')}
      <div class="day" style="margin-top:0">
        <div class="slot"><time style="color:var(--coral)">08:00</time><div class="card" style="padding:12px 16px">{T('Shared grocery list — Omar grabs milk on the way to work.', 'قائمة المشتريات المشتركة — عمر يشتري الحليب في طريقه للعمل.')}</div></div>
        <div class="slot"><time style="color:var(--coral)">13:00</time><div class="card" style="padding:12px 16px">{T('Internet bill reminder, assigned to Lina. Paid ✓', 'تذكير فاتورة الإنترنت، مُسند إلى لينا. تم الدفع ✓')}</div></div>
        <div class="slot"><time style="color:var(--coral)">19:30</time><div class="card" style="padding:12px 16px">{T('They finally decide on the sofa — both picked the velvet one.', 'قرّرا أخيرًا الأريكة — كلاهما اختار المخملية.')}</div></div>
        <div class="slot"><time style="color:var(--coral)">22:00</time><div class="card" style="padding:12px 16px">{T('Movie night saved to Experiences, rated ★★★★ and ★★★★★.', 'سهرة الفيلم محفوظة في التجارب، بتقييم ★★★★ و★★★★★.')}</div></div>
      </div><a class="btn btn-primary" style="margin-top:22px" href="living-together.html">{T('OneSpace for living together →', 'OneSpace للحياة المشتركة ←')}</a></div>
  </div>"""


def solo_panel():
    def s(t, text):
        return f'<div class="slot"><time style="color:var(--teal)">{t}</time><div class="card" style="padding:12px 16px">{N(text)}</div></div>'
    return f"""<div class="split">
    <div class="stage">{screen('share', 'clean', 'Saving a link from another app', _nov_ar('Saving a link from another app'))}</div>
    <div>{N('A day on your own', 'span', 'eyebrow')}{N('Everything in one place — and nothing to remember.', 'h3', '', 'style="font-size:30px;margin:10px 0 18px"')}
      <div class="day" style="margin-top:0">
        {s('08:30', 'Sara shares a sofa from IKEA straight into her “New flat” activity.')}
        {s('12:00', 'A reminder pops up: renew the gym pass before Friday. Done ✓')}
        {s('18:45', 'Gift ideas for her sister’s birthday, with a budget — 2 shortlisted.')}
        {s('21:30', 'A series from Netflix lands in her watchlist for the weekend.')}
      </div><a class="btn btn-primary" style="margin-top:22px" href="on-my-own.html">{N('OneSpace for life on your own →')}</a></div>
  </div>"""


def solo_section():
    """Solo positioning: no backend vocabulary, just what a person can do alone."""
    cards = ''.join(trust_card(i, c, h, _nov_ar(h), p, _nov_ar(p)) for i, c, h, p in [
        ('📲', 'i-blue', 'Everything from every app', 'Links, places, films and products land in one organised space.'),
        ('🧭', 'i-teal', 'Your plans, your pace', 'Compare options, set reminders and plan trips on your own.'),
        ('💞', 'i-coral', 'Invite someone when you’re ready', 'Start sharing with a partner later — your private things stay yours.')])
    return f"""<section id="on-your-own"><div class="wrap">
  <div class="sec-head center">{N('ON YOUR OWN OR TOGETHER', 'span', 'eyebrow')}<h2>{N('No partner in the app yet?')} <span class="serif accent">{N('No problem.')}</span></h2>
  {N('OneSpace works as your own personal assistant from day one. Share links from Netflix, Amazon, Google Maps or any app, keep your lists, reminders, trips and memories together, and decide in your own time. When someone special comes along, invite them — what you keep as Only me stays yours.', 'p', 'lead')}</div>
  <div class="grid g3">{cards}</div>
  <p class="center" style="margin-top:24px"><a class="btn btn-ghost" href="on-my-own.html">{N('OneSpace on your own →')}</a></p>
</div></section>"""


PALETTES = [('clean', 'cleanLight'), ('coral', 'oneSpace'), ('rose', 'softRose'), ('teal', 'oceanTeal'), ('sage', 'sageGarden'),
            ('lavender', 'lavenderDusk'), ('sand', 'desertSand'), ('midnight', 'midnightBlue'), ('mono', 'monochrome')]


def hero_devices():
    if not has_shot('today'):
        return phone(scr_today(True), 'clean', label='OneSpace Today screen for a couple living apart',
                     label_ar='شاشة اليوم في OneSpace لزوجين متباعدين', themable=False)
    return ('<div class="fan">'
            + device('counters', 'Counters', 'العدّادات', 'd2')
            + device('places_map', 'Our places on a map', 'أماكننا على الخريطة', 'd3')
            + device('today', 'OneSpace Today screen for a couple living apart', 'شاشة اليوم في OneSpace لزوجين متباعدين', 'd1 lg')
            + '</div>')


def theme_wall():
    if not has_shot('themes/today_cleanLight'):
        return ''
    figs = ''.join(f'<figure>{device("themes/today_" + p, "Today in " + n, "اليوم بسمة " + na, "")}<figcaption>{T(n, na)}</figcaption></figure>'
                   for (k, p), (n, na) in zip(PALETTES, [('Clean Light', 'فاتح نقي'), ('Coral & Teal', 'مرجاني وفيروزي'), ('Soft Rose', 'وردي ناعم'),
                                                       ('Ocean Teal', 'فيروزي المحيط'), ('Sage Garden', 'حديقة المريمية'), ('Lavender Dusk', 'غسق الخزامى'),
                                                       ('Desert Sand', 'رمال الصحراء'), ('Midnight Blue', 'أزرق منتصف الليل'), ('Monochrome', 'أحادي اللون')]))
    return f'''<section class="tint"><div class="wrap"><div class="sec-head center">{T('Nine themes, the real app', 'تسع سمات من التطبيق الحقيقي', 'span', 'eyebrow')}{T('Which one feels like you two?', 'أيها يشبهكما؟', 'h2')}</div>
  <div class="wall theme-wall-grid reveal">{figs}</div><p class="center" style="margin-top:22px"><a class="btn btn-ghost" href="how-it-works.html">{T('Try the demo', 'جرّب العرض')}</a></p></div></section>'''


ONE_LIST = [  # (icon, kind, kind_ar, [(app, its list)], onespace, onespace_ar, link)
    ('🎬', 'Movies & shows', 'الأفلام والمسلسلات', [('Netflix', 'My List'), ('Prime Video', 'Watchlist'), ('Disney+', 'Watchlist'), ('YouTube', 'Watch later'), ('Apple TV+', 'Up Next')],
     'One shared watchlist — with what you both want on top', 'قائمة مشاهدة مشتركة واحدة — وما يريده كلاكما في الأعلى', 'watchlists.html'),
    ('🎵', 'Music, books & games', 'الموسيقى والكتب والألعاب', [('Spotify', 'Liked songs'), ('Apple Music', 'Library'), ('Goodreads', 'Want to read'), ('Steam', 'Wishlist')],
     'One list per kind, rated by both of you', 'قائمة واحدة لكل نوع، بتقييم كل منكما', 'watchlists.html'),
    ('🛒', 'Things to buy', 'المشتريات', [('Amazon', 'Wish list'), ('IKEA', 'Favourites'), ('Etsy', 'Favourites'), ('eBay', 'Watchlist')],
     'Options from every shop side by side — or one gift list per occasion', 'خيارات كل المتاجر جنبًا إلى جنب — أو قائمة هدايا واحدة لكل مناسبة', 'decide-together.html'),
    ('✈️', 'Flights & stays', 'الطيران والإقامة', [('Google Flights', 'Tracked'), ('Skyscanner', 'Saved'), ('Kayak', 'Trips'), ('Booking.com', 'Saved')],
     'One trip: every flight option compared, hotel, plan and documents', 'رحلة واحدة: كل خيارات الطيران مقارنة، والفندق والخطة والمستندات', 'trips.html'),
    ('📍', 'Places', 'الأماكن', [('Google Maps', 'Saved'), ('Apple Maps', 'Guides'), ('Waze', 'Favorites')],
     'One map of where you have been — and where you dream of going', 'خريطة واحدة لما زرتماه — ولما تحلمان بزيارته', 'memories.html'),
]


def one_list_section(cls='tint', head=True, cta=True):
    rows = ''
    for icon, k, ka, apps, o, oa, link in ONE_LIST:
        chips = ''.join(f'<span class="ol-app"><b>{a}</b> {l}</span>' for a, l in apps)
        rows += f"""<div class="ol-row reveal"><div class="ol-kind"><span class="ol-ico">{icon}</span>{T(k, ka, 'b')}</div>
  <div class="ol-apps">{chips}<span class="ol-x">{T('×2 — you each have your own', '×2 — لكلٍّ منكما حسابه')}</span></div>
  <span class="ol-arrow" aria-hidden="true">→</span>
  <a class="ol-one" href="{link}"><span class="ol-badge">{T('1 in OneSpace', '1 في OneSpace')}</span>{T(o, oa)}</a></div>"""
    top = f"""<div class="sec-head center">{T('One list per kind', 'قائمة واحدة لكل نوع', 'span', 'eyebrow')}{T('Every app keeps its own list. OneSpace keeps one for both of you.', 'كل تطبيق يحتفظ بقائمته. OneSpace يحتفظ بقائمة واحدة لكليكما.', 'h2')}
  {T('Five streaming services, four shops, three flight sites — each with its own list, and each of you with your own account. That is easily 20 lists between two people. Tap Share in any of them and OneSpace puts it in the one list where it belongs.', 'خمس منصات بث وأربعة متاجر وثلاثة مواقع طيران — لكل منها قائمته، ولكل منكما حسابه. هذا يعني بسهولة 20 قائمة بينكما. انقر «مشاركة» في أي منها وسيضعه OneSpace في القائمة الوحيدة التي ينتمي إليها.', 'p', 'lead')}</div>""" if head else ''
    return f"""<section class="{cls}" id="one-list"><div class="wrap">{top}<div class="ol">{rows}</div>
  {f'<p class="center" style="margin-top:22px"><a class="btn btn-ghost" href="smart-sharing.html">' + T('See how sharing works →', 'شاهد كيف تعمل المشاركة ←') + '</a></p>' if cta else ''}</div></section>"""


def watch_section():
    tour = clip('tour', 'A short tour of the OneSpace app', 'جولة قصيرة في تطبيق OneSpace', 'lg')
    if not tour:
        return ''
    small = ''.join(f'<figure>{clip(n, e, a, "sm")}<figcaption>{T(e, a)}</figcaption></figure>' for n, e, a in [
        ('plan', 'Decide together', 'قررا معًا'), ('counters', 'Count the days', 'عدّا الأيام'), ('themes', 'Change the mood', 'غيّرا المزاج')] if clip(n, e, a))
    return f'''<section class="warm"><div class="wrap split watch-real-layout">
  <div class="stage">{tour}</div>
  <div>{T('See it move', 'شاهده يتحرك', 'span', 'eyebrow')}{T('This is the real app — not a mock-up.', 'هذا هو التطبيق الحقيقي — وليس تصميمًا تخيليًا.', 'h2')}
  {T('Recorded on a phone with our fictional couple, Omar and Lina. What you see is exactly what you get.', 'سُجّل على هاتف مع زوجينا الافتراضيين عمر ولينا. ما تراه هو ما ستحصل عليه تمامًا.', 'p', 'lead')}
  <div class="wall watch-clips" style="margin-top:20px">{small}</div></div>
</div></section>'''


def compare_rows(limit=None):
    rows = COMPARE[:limit] if limit else COMPARE
    lo, ln = K('The usual mix', 'الخليط المعتاد'), K('OneSpace', 'OneSpace')
    return ''.join(f'<tr><th scope="row">{T(n, na)}</th><td class="old" data-label="The usual mix" data-i18n-attr="data-label:{lo}">{T(u, ua)}</td>'
                   f'<td class="new" data-label="OneSpace" data-i18n-attr="data-label:{ln}">✓ {T(o, oa)}</td></tr>' for n, na, u, ua, o, oa in rows)


def compare_table(limit=None):
    return f"""<div class="cmp-wrap"><table class="cmp"><thead><tr><th></th><th>{T('The usual mix', 'الخليط المعتاد')}<small>{T('chat, notes, two calendars, spreadsheets, photos', 'محادثة وملاحظات وتقويمان وجداول وصور')}</small></th><th class="new">OneSpace<small>{T('one private app for two', 'تطبيق خاص واحد لشخصين')}</small></th></tr></thead>
<tbody>{compare_rows(limit)}</tbody></table></div>"""


def value_grid():
    cards = ''.join(f"""<a class="card link value reveal" href="{d['slug']}"><span class="vi">{d['icon']}</span>{T(d['nav'][0], d['nav'][1], 'h3')}{T(d['navd'][0], d['navd'][1], 'p')}<span class="more">{T('See how →', 'شاهد كيف ←')}</span></a>""" for d in DEEP)
    extra = [('long-distance.html', '🌍', 'Made for distance', 'مصمم للمسافة', 'Two clocks, reunion countdowns, sealed letters', 'ساعتان وعدّ للقاء ورسائل مغلقة'),
             ('features.html#remember', '⏳', 'Counters that understand dates', 'عدّادات تفهم التواريخ', 'The day itself and its anniversary, with progress', 'اليوم نفسه وذكراه، مع التقدم'),
             ('connect-care.html', '♡', 'Connect & care', 'التواصل والاهتمام', 'Letters, gestures, daily check-ins and a feelings journal', 'رسائل ولفتات وتواصل يومي ويوميات المشاعر')]
    cards += ''.join(f"""<a class="card link value reveal" href="{h}"><span class="vi">{i}</span>{T(e, a, 'h3')}{T(de, da, 'p')}<span class="more">{T('See how →', 'شاهد كيف ←')}</span></a>""" for h, i, e, a, de, da in extra)
    return f"""<section id="why"><div class="wrap">
  <div class="sec-head center">{T('Why couples choose OneSpace', 'لماذا يختار الأزواج OneSpace', 'span', 'eyebrow')}<h2>{T('More than the basics.', 'أكثر من الأساسيات.')} <span class="serif accent">{T('Thought through for two.', 'مدروسة لكليكما.')}</span></h2>
  {T('Every OneSpace feature adds thoughtful details to a familiar idea. Open one to see the workflow behind it.', 'تضيف كل ميزة في OneSpace تفاصيل مدروسة لفكرة مألوفة. افتحا أي ميزة لتكتشفا طريقة عملها.', 'p', 'lead')}</div>
  <div class="values">{cards}</div>
</div></section>"""


def deep_page(d):
    slug = d['slug']
    t_en, t_ar = d['title']
    h = head(slug, f"{d['nav'][0]} — OneSpace couples app", f"{d['nav'][1]} — تطبيق OneSpace للأزواج", d['seo'][0], d['seo'][1])
    shot = d.get('shot')
    main_dev = device(shot, d['nav'][0], d['nav'][1], 'lg', fallback=phone(SCREENS[d['illus']](), d['theme'], label=d['nav'][0], label_ar=d['nav'][1])) if shot else phone(SCREENS[d['illus']](), d['theme'], label=d['nav'][0], label_ar=d['nav'][1])
    second = d.get('shot2')
    pains = ''.join(pain(a, b, c, e, f, g) for a, b, c, e, f, g in d['pains'])
    steps = ''.join(f'<li class="reveal"><span class="sn">{i}</span><div>{T(a, b, "h3")}{T(c, e, "p")}</div></li>' for i, (a, b, c, e) in enumerate(d['steps'], 1))
    details = ''.join(trust_card(i, 'i-teal', a, b, c, e) for i, a, b, c, e in d['details'])
    vs = ''.join(f'<tr><th scope="row">{T(n, na)}</th><td class="old">{T(u, ua)}</td><td class="new">✓ {T(o, oa)}</td></tr>' for n, na, u, ua, o, oa in d['vs'])
    faq = ''.join(f'<details>{T(q, qa, "summary")}{T(a, aa, "p")}</details>' for q, qa, a, aa in d['faq'])
    side = device(second, 'Shared list in OneSpace', 'قائمة مشتركة في OneSpace', 'sm', fallback='') if slug == 'smart-sharing.html' and second else (device(second, d['nav'][0], d['nav'][1], 'sm', fallback='') if second else '')
    if slug == 'smart-sharing.html':
        main_dev = '<div class="sharing-preview-wrap">' + main_dev + '<span class="sharing-preview-label">' + T('Illustration of the share flow', 'تصور توضيحي لعملية المشاركة') + '</span></div>'
    illus = phone(SCREENS[d['illus']](), d['theme'], label=d['nav'][0], label_ar=d['nav'][1])
    hero_headline = (
        '<h1 class="editorial-hero-title">' + T('Share anything from any app', 'شارك أي شيء من أي تطبيق') +
        ' <span class="serif accent">' + T('OneSpace knows where it goes', 'وOneSpace يعرف أين يضعه') + '</span></h1>'
        if slug == 'smart-sharing.html' else T(t_en, t_ar, 'h1')
    )
    others = ''.join(f'<a class="chip" href="{o["slug"]}">{o["icon"]} {T(o["nav"][0], o["nav"][1])}</a>' for o in DEEP if o is not d)
    ld = {'@context': 'https://schema.org', '@type': 'WebPage', 'name': t_en, 'description': d['seo'][0], 'url': BASE + slug,
          'about': {'@type': 'MobileApplication', 'name': 'OneSpace'}}
    return h + f"""
<section class="page-hero deep-hero"><div class="wrap split">
  <div><div class="crumbs"><a href="./">{T('Home', 'الرئيسية')}</a> › <a href="features.html">{T('Features', 'المزايا')}</a> › {T(d['nav'][0], d['nav'][1])}</div>
    <div style="font-size:44px;margin-top:14px">{d['icon']}</div>{hero_headline}{T(d['lead'][0], d['lead'][1], 'p', 'lead')}
    <div class="cta-row"><a class="btn btn-primary" href="join.html">{T('Join the Founding 500', 'انضم إلى المؤسسين الـ500')}</a><a class="btn btn-ghost" href="#how">{T('How it works', 'كيف يعمل')}</a></div></div>
  <div class="stage"><div class="phones">{main_dev}{side}</div></div>
</div></section>
<section class="tint"><div class="wrap"><div class="sec-head center">{T('The problem', 'المشكلة', 'span', 'eyebrow')}{T('Sound familiar?', 'هل يبدو هذا مألوفًا؟', 'h2')}</div><div class="pains">{pains}</div></div></section>
{one_list_section('', cta=slug != 'smart-sharing.html') if slug in ('smart-sharing.html', 'watchlists.html', 'trips.html') else ''}
<section id="how"><div class="wrap split" style="align-items:start">
  <div>{T('How OneSpace solves it', 'كيف يحلها OneSpace', 'span', 'eyebrow')}{T('Three simple steps.' if len(d['steps']) == 3 else 'Four simple steps.', 'ثلاث خطوات بسيطة.' if len(d['steps']) == 3 else 'أربع خطوات بسيطة.', 'h2', '', 'style="margin:10px 0 26px"')}<ol class="how">{steps}</ol></div>
  <div class="stage" style="position:sticky;top:100px">{illus}</div>
</div></section>
<section class="tint"><div class="wrap"><div class="sec-head">{T('In detail', 'بالتفصيل', 'span', 'eyebrow')}{T('Everything it can do.', 'كل ما يستطيع فعله.', 'h2')}</div><div class="grid g3">{details}</div></div></section>
<section><div class="narrow"><div class="sec-head center">{T('The difference', 'الفرق', 'span', 'eyebrow')}{T('Before and after OneSpace', 'قبل OneSpace وبعده', 'h2')}</div>
  <div class="cmp-wrap"><table class="cmp"><thead><tr><th></th><th>{T('Without', 'بدونه')}</th><th class="new">{T('With OneSpace', 'مع OneSpace')}</th></tr></thead><tbody>{vs}</tbody></table></div>
  {('<div style="margin-top:36px">' + faq + '</div>') if faq else ''}
  <p class="center" style="margin-top:30px"><a href="compare.html">{T('See the full comparison →', 'شاهد المقارنة الكاملة ←')}</a></p></div></section>
<section class="tint"><div class="wrap center">{T('More of what OneSpace does', 'المزيد مما يفعله OneSpace', 'h2', '', 'style="font-size:28px;margin-bottom:18px"')}<div style="display:flex;flex-wrap:wrap;gap:10px;justify-content:center">{others}</div></div></section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
""" + cta_band() + foot()




# Preview is deliberately visible for design sign-off; switch off after review.
# No ratings, testimonials or customer names here are verified customer feedback.
SHOW_AI_REVIEW_PREVIEW = True


def connect_care_preview():
    return f'''<section class="connection-showcase" id="connect-care-showcase">
      <div class="wrap connection-layout" id="connect">
        <div class="connection-copy">
          {T('CONNECT & CARE', 'التواصل والاهتمام', 'span', 'eyebrow')}
          {T('Stay close. Plan life together.', 'ابقيا قريبين، وخططا لحياتكما معًا.', 'h2')}
          {T('Love letters, personal gestures, daily check-ins and a feelings journal help you connect. OneSpace goes further — share ideas, discuss options and make plans together.', 'رسائل الحب ولمسات الاهتمام والتواصل اليومي ويوميات المشاعر تبقيكما على تواصل. ويذهب OneSpace أبعد من ذلك لتتشاركا الأفكار وتناقشا الخيارات وتخططا معًا.', 'p', 'lead')}
          <div class="connection-links">
            <a href="connect-care.html#letters">{T('Letters', 'الرسائل')}</a>
            <a href="connect-care.html#gestures">{T('Love gestures', 'لمسات الحب')}</a>
            <a href="connect-care.html#checkins">{T('Daily check-ins', 'التواصل اليومي')}</a>
            <a href="connect-care.html#journal">{T('Feelings journal', 'يوميات المشاعر')}</a>
          </div>
          <a class="btn btn-ghost" href="connect-care.html">{T('Explore Connect & Care', 'اكتشفا التواصل والاهتمام')}</a>
        </div>
        <div class="connection-devices">
          {device('letters','OneSpace love letters — real app screenshot','رسائل الحب — لقطة حقيقية من التطبيق','sm')}
          {device('love','OneSpace love gestures — real app screenshot','لمسات الحب — لقطة حقيقية من التطبيق','sm')}
        </div>
      </div>
    </section>'''



def gesture_extra():
    """Honest, feature-specific popup and history diagrams pending real robot screenshots."""
    return f'''<section class="gesture-extra"><div class="wrap gesture-extra-layout">
      <div>{T('THE COMPLETE GESTURE JOURNEY', 'تجربة اللمسة كاملة', 'span','eyebrow')}
      {T('A gesture, its moment and its history.', 'لفتة ولحظتها وسجلّها.', 'h3')}
      {T('The gesture picker is shown above from the real app. Dedicated captures of the sending popup and sent/received history are still being prepared.', 'تظهر شاشة اختيار اللفتة أعلاه من التطبيق الحقيقي. ما زلنا نجهز لقطتي نافذة الإرسال وسجل اللفتات المرسلة والمستلمة.', 'p')}</div>
      <div class="gesture-capture-slots">
        <figure class="gesture-mockup"><figcaption>{T('Gesture popup','نافذة اللمسة')}</figcaption><div class="gesture-ui">
          <small>{T('Illustrative layout · real screenshot pending','تصور توضيحي · اللقطة الحقيقية قيد الانتظار')}</small>
          <b>{T('A little love','لمسة حب')}</b><span class="gesture-illustration-icon" aria-hidden="true">🤗</span>
          <strong>{T('Send Lina a hug','أرسل لينا حضنًا')}</strong>
          <p>{T('“Can’t wait for our stars weekend.”','«لا أطيق الانتظار لعطلة النجوم.»')}</p>
          <span class="gesture-illustration-action">{T('Send','أرسل')}</span></div></figure>
        <figure class="gesture-mockup"><figcaption>{T('Sent & received history','سجل المرسلة والمستلمة')}</figcaption><div class="gesture-ui gesture-history-ui">
          <small>{T('Illustrative layout · real screenshot pending','تصور توضيحي · اللقطة الحقيقية قيد الانتظار')}</small>
          <b>{T('Sent & received history','سجل المرسلة والمستلمة')}</b>
          <div class="gesture-history-switch" aria-hidden="true"><span>↗</span><span>↙</span></div>
          <div class="gesture-history-row"><span aria-hidden="true">🤗</span><span class="gesture-history-placeholder"></span></div>
          <div class="gesture-history-row"><span aria-hidden="true">💌</span><span class="gesture-history-placeholder"></span></div>
          <div class="gesture-history-row"><span aria-hidden="true">💖</span><span class="gesture-history-placeholder"></span></div>
        </div></figure>
      </div>
    </div></section>'''


def page_connect_care():
    h = head('connect-care.html', 'Connect & Care | OneSpace letters, gestures and feelings',
             'التواصل والاهتمام | رسائل OneSpace ومشاعره',
             'Love letters, personal gestures, daily check-ins and feelings journal in one couples app, alongside shared planning and decisions.',
             'رسائل الحب ولمسات الاهتمام والتواصل اليومي ويوميات المشاعر إلى جانب التخطيط والقرارات المشتركة في تطبيق للأزواج.')
    return h + page_hero('Connect & Care','التواصل والاهتمام',
      'The heart of your relationship, with room for everything else.',
      'مساحة لمشاعركما، ولكل تفاصيل حياتكما.',
      'Emotional connection is important. OneSpace combines it with planning, conversations, comparisons and decisions — so it supports the whole life you share.',
      'التواصل العاطفي مهم. ويجمعه OneSpace مع التخطيط والمحادثات والمقارنات والقرارات، ليدعم حياتكما المشتركة بكل تفاصيلها.') + \
      feature_block('letters', 'LOVE LETTERS','رسائل الحب',
        'Words worth waiting for.','كلمات تستحق الانتظار.',
        'Write a letter today and choose when your partner can open it, with a countdown until that moment.',
        'اكتب رسالة اليوم، واختر موعد فتحها لشريكك مع عد تنازلي حتى تلك اللحظة.',
        [('Timed opening','for birthdays, anniversaries and special days.','موعد الفتح','لأعياد الميلاد والذكريات والمناسبات الخاصة.'),
         ('Private message','the letter stays for its intended recipient.','رسالة خاصة','تبقى الرسالة لمن أرسلت إليه.')],
        'letter','rose',tint=True,label='OneSpace letters screenshot') + \
      feature_block('gestures','A LITTLE LOVE','لمسة حب',
        'A small gesture can change a day.','لفتة صغيرة قد تغيّر اليوم.',
        'Send a hug, a kiss, encouragement or your own words. A personal moment, not an automated ritual.',
        'أرسل حضنًا أو قبلة أو تشجيعًا أو كلماتك الخاصة. لفتة شخصية وليست رسالة آلية.',
        [('Your words','add a personal message to a gesture.','كلماتك','أضف رسالة شخصية إلى اللفتة.'),
         ('Shared history','look back at the gestures you have sent and received.','سجل اللفتات','ارجع إلى ما أرسلتماه وتلقيتماه.')],
        'love','lavender',rev=True,label='OneSpace A little love screenshot') + \
      gesture_extra() + \
      feature_block('checkins','DAILY CHECK-INS','التواصل اليومي',
        'A little space to say how you really are.','مساحة صغيرة لتعبّر عما تشعر به.',
        'Share how you are feeling and what is on your mind, even when you are busy or apart.',
        'عبّر عن شعورك وما يشغل بالك حتى مع الانشغال أو البعد.',
        [('Daily reflection','take a moment to name how your day feels.','تأمل يومي','توقف قليلًا لتصف شعورك اليوم.'),
         ('Share what matters','give your partner context beyond a quick reply.','مشاركة مهمة','امنح شريكك صورة أوضح من مجرد رد سريع.')],
        'ourspace','teal',tint=True,label='Real daily check-in screenshot from the demo couple',real='checkins.png') + \
      feature_block('journal','FEELINGS JOURNAL','يوميات المشاعر',
        'Give your feelings somewhere to live.','امنح مشاعرك مكانًا تحتفظ به.',
        'Record thoughts and moods over time, and revisit them when you want to reflect on your day.',
        'دوّن أفكارك ومشاعرك، وعُد إليها حين ترغب في التأمل في يومك.',
        [('Reflect over time','revisit your earlier notes and feelings.','تأمل مع الوقت','عد إلى ملاحظاتك ومشاعرك السابقة.'),
         ('Your context','keep what you want to remember without losing it in chat.','احتفظ بالسياق','احفظ ما يهمك دون أن يضيع في المحادثة.')],
        'ourspace','sage',rev=True,visual=f'''<div class="journal-illustration" role="img" aria-label="Illustrative feelings journal layout, not a real screenshot">
          <small>{T('Illustrative layout · real screenshot pending', 'تصور توضيحي · اللقطة الحقيقية قيد الانتظار')}</small>
          <div class="journal-illustration-head"><span aria-hidden="true">✎</span><strong>{T('Feelings journal','يوميات المشاعر')}</strong></div>
          <div class="journal-illustration-moods" aria-hidden="true"><span>😞</span><span>😐</span><span class="selected">🙂</span><span>😊</span><span>🤩</span></div>
          <p>{T('Record thoughts and moods over time, and revisit them when you want to reflect on your day.', 'دوّن أفكارك ومشاعرك، وعُد إليها حين ترغب في التأمل في يومك.')}</p>
          <div class="journal-illustration-lines" aria-hidden="true"><i></i><i></i><i></i></div>
        </div>''') + \
      f'''<section class="connection-followup"><div class="wrap center">
        {T('Emotional connection is only the beginning.', 'التواصل العاطفي ليس إلا البداية.', 'h2')}
        {T('OneSpace also brings two-way editing, comparison, discussion and shared planning into the same space.', 'يجمع OneSpace أيضًا التعديل المتبادل والمقارنة والنقاش والتخطيط المشترك في المساحة نفسها.', 'p','lead')}
        <a class="btn btn-primary" href="decide-together.html">{T('See how we decide together', 'اكتشفا كيف تقرران معًا')}</a>
      </div></section>''' + value_grid() + cta_band() + foot()



def smart_utilities():
    """Verified capabilities: global search plus schedule-aware notifications."""
    notification = device('notifications', 'Real OneSpace notifications screen',
      'لقطة حقيقية من شاشة إشعارات OneSpace', 'sm')
    return f'''<section class="smart-utilities" id="smart-details">
      <div class="wrap">
        <div class="sec-head center">
          {T('SMART DETAILS', 'تفاصيل ذكية', 'span','eyebrow')}
          {T('Find it fast. Know what matters.', 'اعثر على ما تريد. واعرف ما يهم.', 'h2')}
          {T('Your shared life needs more than another list of alerts. OneSpace keeps information and daily rhythms in context.',
             'حياتكما المشتركة تحتاج إلى أكثر من قائمة تنبيهات. يحفظ OneSpace المعلومات وينظمها وفق سياق يومكما.', 'p','lead')}
        </div>
        <div class="smart-utility-grid">
          <article class="smart-utility-panel">
            <div class="smart-utility-copy">
              <span class="eyebrow">{T('GLOBAL SEARCH','البحث الشامل')}</span>
              {T('One search across your shared space.','بحث واحد في مساحتكما المشتركة.','h3')}
              {T('Forgot where you saved that link, note, place, trip or decision? Search across the information you can access, then open the original item. Private content stays protected by your account permissions.',
                 'هل نسيت أين حفظت رابطًا أو ملاحظة أو مكانًا أو رحلة أو قرارًا؟ ابحث في المعلومات المتاحة لحسابك وافتح العنصر الأصلي مباشرة. وتبقى العناصر الخاصة محمية بصلاحيات حسابك.', 'p')}
              <ul class="ticks">
                <li>{T('Find information without opening every list','اعثر على المعلومات دون فتح كل قائمة')}</li>
                <li>{T('Searchable categories and filtered results','فئات بحث ونتائج يمكن تصفيتها')}</li>
                <li>{T('Respect private and shared visibility','احترام خصوصية العناصر المشتركة والخاصة')}</li>
              </ul>
            </div>
            <div class="smart-search-preview" role="img" aria-label="Illustrative global search layout, not a screenshot from the app">
              <span class="smart-preview-label">{T('Illustrative layout · real screenshot pending', 'تصور توضيحي · اللقطة الحقيقية قيد الانتظار')}</span>
              <div class="smart-search-box"><span aria-hidden="true">⌕</span>{T('Search our space', 'ابحث في مساحتنا')}</div>
              <div class="smart-search-sample">
                <span>{T('Example categories', 'أمثلة للفئات')}</span>
                <span class="smart-search-tags">{T('Notes · Trips · Places · Activities', 'ملاحظات · رحلات · أماكن · أنشطة')}</span>
              </div>
            </div>
          </article>
          <article class="smart-utility-panel smart-notifications">
            <div class="smart-utility-copy">
              <span class="eyebrow">{T('THOUGHTFUL NOTIFICATIONS','إشعارات تراعي وقتك')}</span>
              {T('Notifications that know your rhythm.', 'إشعارات تفهم إيقاع يومك.', 'h3')}
              {T('OneSpace uses the work and sleep schedule you set, including days off. Non-urgent partner pushes can wait while you sleep and arrive as a morning summary; urgent reminders can still alert you. Your usual working hours also help the app understand your daily routine.',
                 'يعتمد OneSpace على مواعيد عملك ونومك التي تحددها، بما فيها أيام الإجازة. يمكن أن تنتظر إشعارات الشريك غير العاجلة أثناء نومك ثم تصلك مجمّعة صباحًا، بينما تظل التذكيرات العاجلة قادرة على تنبيهك. وتساعد ساعات العمل المعتادة التطبيق على مراعاة روتين يومك.', 'p')}
              <ul class="ticks">
                <li>{T('Sleep-aware quiet hours and morning summary','هدوء أثناء النوم وملخص عند الاستيقاظ')}</li>
                <li>{T('Work schedule and days-off awareness','مراعاة أوقات العمل وأيام الإجازة')}</li>
                <li>{T('Grouped updates with context and direct links','تحديثات مجمعة مع سياق وروابط مباشرة')}</li>
              </ul>
            </div>
            <div class="smart-notification-visual">{notification}</div>
          </article>
        </div>
      </div>
    </section>'''



def ai_review_preview():
    """AI-generated fictional examples: review layouts, never social-proof claims."""
    if not SHOW_AI_REVIEW_PREVIEW:
        return ''
    samples = [
      ('We kept sending each other links. Now our shortlist lives in one place.',
       'كنا نتبادل الروابط باستمرار، والآن نجمع خياراتنا في قائمة واحدة.', 'Long-distance', 'عن بُعد'),
      ('We can discuss different options and actually remember what we decided.',
       'نتناقش في الخيارات المختلفة ونتذكّر فعلًا ما قررناه.', 'Living together', 'نعيش معًا'),
      ('Our trip ideas, packing list and decisions finally have a place together.',
       'أفكار رحلتنا وقائمة تجهيزنا وقراراتنا أصبحت في مكان واحد.', 'Planning a trip', 'نخطط لرحلة'),
      ('The sweet messages are still there, alongside everything we need to plan.',
       'رسائلنا الجميلة موجودة، ومعها كل ما نحتاج إلى التخطيط له.', 'Living apart', 'نعيش متباعدين'),
    ]
    cards = ''.join(
      f'<article class="testi-card" data-testimonial-card tabindex="0">'
      f'<span class="testi-label">{T("AI-generated test example","مثال تجريبي مولّد بالذكاء الاصطناعي")}</span>'
      f'{T("“"+quote+"”","«"+quote_ar+"»","p","testi-quote")}'
      f'{T(kind,kind_ar,"span","testi-type")}'
      f'</article>'
      for quote,quote_ar,kind,kind_ar in samples)
    dots = ''.join(f'<button type="button" data-slide-dot="{i}" aria-current="{"true" if i == 0 else "false"}" aria-label="Example testimonial {i+1}"></button>' for i in range(len(samples)))
    def store_panel(name, label, label_ar):
      brand = ('''<span class="review-brand-icon" aria-hidden="true"><svg viewBox="0 0 48 48" focusable="false"><path d="M8 4.5v39l21-19.5z" fill="#34A853"/><path d="M8 4.5 32 17 29 24z" fill="#4285F4"/><path d="m29 24 3-7 11 5.8a3.5 3.5 0 0 1 0 6.2L32 31z" fill="#FBBC04"/><path d="m8 43.5 24-12.5-3-7z" fill="#EA4335"/></svg></span>''' if name == 'Google Play' else '''<span class="review-brand-icon" aria-hidden="true"><svg viewBox="0 0 48 48" focusable="false"><rect x="2" y="2" width="44" height="44" rx="10" fill="#1677ED"/><path d="M18.2 11.5 34 37.6M31.4 11.5 15.2 37.6M10.6 29.3h26.9" stroke="#fff" stroke-width="4.7" stroke-linecap="round"/><path d="m18.2 11.5 2.3 3.9" stroke="#fff" stroke-width="4.7" stroke-linecap="round"/></svg></span>''')
      bars = ''.join(
         f'<div class="store-rating-row"><span>{star} ★</span><span class="store-rating-bar" aria-hidden="true"><i></i></span>'
         f'<span class="store-rating-pending">—</span></div>'
         for star in (5,4,3,2,1))
      return f'''<article class="review-preview-store">
        <div class="review-store-head"><h4 class="review-brand">{brand}<span>{name}</span></h4><span class="review-test-tag">{T('TEST PREVIEW','معاينة تجريبية')}</span></div>
        <div class="review-store-metrics">
          <div><strong>— / 5</strong>{T('Average rating','متوسط التقييم','span')}</div>
          <div><strong>—</strong>{T('Ratings & reviews','التقييمات والمراجعات','span')}</div>
          <div><strong>—</strong>{T('Downloads','التنزيلات','span')}</div>
        </div>
        <h5>{T('Rating breakdown', 'توزيع التقييمات')}</h5>
        <div class="review-rating-breakdown">{bars}</div>
        <p class="review-unrated">{T('Awaiting verified store data', 'بانتظار بيانات موثّقة من المتجر')}</p>
        <div class="review-fake-review">
          <span>{T('Review layout placeholder', 'موضع تجريبي لعرض مراجعة')}</span>
          <p>{T('A real review will appear here after public release and permission to display it.',
             'ستظهر هنا مراجعة حقيقية بعد الإطلاق العام والحصول على إذن عرضها.')}</p>
        </div>
        <p class="review-store-disclaimer">{T('AI-generated testing layout. Not a real app rating or review.',
             'تنسيق تجريبي مولّد بالذكاء الاصطناعي. ليس تقييمًا أو مراجعة حقيقية.')}</p>
      </article>'''
    return f'''<section class="review-preview" id="reviews-preview" data-review-preview="test-only" data-nosnippet>
    <div class="wrap">
      <p class="review-preview-warning">{T('TEST ONLY · AI-GENERATED PLACEHOLDERS · NOT REAL CUSTOMER REVIEWS OR RATINGS',
        'للاختبار فقط · نماذج مولّدة بالذكاء الاصطناعي · ليست مراجعات أو تقييمات حقيقية')}</p>
      <div class="review-preview-head">
        <div>{T('DESIGN PREVIEW', 'معاينة التصميم', 'span','eyebrow')}
          {T('A glimpse of what couples might say.', 'لمحة عمّا قد يقوله الأزواج.', 'h2')}
          {T('Fictional example testimonials for layout testing only. These quotes are not from actual users.',
            'شهادات افتراضية لاختبار التصميم فقط. هذه الاقتباسات ليست من مستخدمين حقيقيين.', 'p','lead')}</div>
        <div class="review-slider-actions">
          <button data-slide-prev type="button" aria-label="Previous testimonial" disabled>‹</button>
          <button data-slide-next type="button" aria-label="Next testimonial">›</button>
        </div>
      </div>
      <div class="testimonials-carousel" data-testimonial-carousel>
        <div class="testi-track" data-slide-track tabindex="0" aria-label="AI-generated example testimonial carousel">{cards}</div>
        <div class="testi-dots">{dots}</div>
      </div>
      <div class="review-stores-header">
        {T('App ratings & reviews — design preview','تقييمات ومراجعات التطبيق — معاينة التصميم','h3')}
        {T('We will display verified store metrics when they are available. No ratings or download counts have been invented.',
           'سنعرض بيانات المتاجر الموثّقة عندما تتوفر. لم نخترع أي تقييمات أو أرقام تنزيلات.', 'p')}
      </div>
      <div class="review-preview-grid">{store_panel('Google Play','','')}{store_panel('App Store','','')}</div>
      <p class="review-preview-note">{T('All examples are AI-generated for testing and must not be presented as real social proof.',
         'جميع الأمثلة مولّدة بالذكاء الاصطناعي لأغراض الاختبار ولا يجوز عرضها على أنها آراء حقيقية.')}</p>
    </div>
    </section>'''



def differentiation_section():
    """Editorial value story: connected workflows, not generic feature tiles."""
    pillars = [
      ('01', 'Share anywhere. Keep one list together.', 'شاركا من أي مكان، واجمعا كل شيء.',
       'Share from another app and OneSpace suggests where the item belongs — a shared watchlist, a place, an option or a gift idea. Both of you know where to find it.',
       'شاركا من أي تطبيق، وسيقترح OneSpace مكان العنصر المناسب: قائمة مشاهدة مشتركة أو مكان أو خيار أو فكرة هدية. ليعرف كل منكما أين يجده.',
       'smart-sharing.html', 'Explore smart sharing', 'اكتشفا المشاركة الذكية'),
      ('02', 'Two people. One evolving decision.', 'رأيان وقرار واحد يتطور معكما.',
       'Both partners can contribute to shared activities: add or edit details, discuss options, see changes and keep the final choice beside the conversation.',
       'يمكن لكليكما المشاركة في الأنشطة المشتركة: إضافة التفاصيل وتعديلها ومناقشة الخيارات ومراجعة التغييرات، مع حفظ القرار بجانب النقاش.',
       'decide-together.html', 'Explore shared decisions', 'اكتشفا القرارات المشتركة'),
      ('03', 'Plan the whole journey, not just the date.', 'خططا للتفاصيل، لا للموعد وحده.',
       'Compare prices and specifications, organise flights and packing, and prepare occasions with gift ideas and budgets — all connected to the plan.',
       'قارنا الأسعار والمواصفات، ونظّما الرحلات والتجهيز، وخططا للمناسبات بأفكار الهدايا والميزانيات، مع بقاء التفاصيل مرتبطة بالخطة.',
       'trips.html', 'Explore trip planning', 'اكتشفا تخطيط الرحلات'),
      ('04', 'Emotional connection — and a life beyond it.', 'تواصل عاطفي وحياة مشتركة تتجاوز ذلك.',
       'Letters, love gestures, check-ins and a feelings journal keep you close. OneSpace goes further: planning, discussion, comparisons and decisions happen in the same space.',
       'تبقيكما الرسائل ولمسات الحب والتواصل اليومي ويوميات المشاعر قريبين. ويذهب OneSpace أبعد من ذلك: تخططان وتتناقشان وتقارنان الخيارات وتتخذان القرارات في مساحة واحدة.',
       'connect-care.html', 'Explore Connect & Care', 'اكتشفا التواصل والاهتمام'),
    ]
    lines = ''.join(
      f'<article class="difference-row">'
      f'<span class="difference-no" aria-hidden="true">{n}</span>'
      f'<div class="difference-copy">{T(title, title_ar, "h3")}'
      f'{T(desc, desc_ar, "p")}'
      f'<a href="{href}" class="difference-link">{T(link, link_ar)} <span aria-hidden="true">↗</span></a>'
      f'</div></article>'
      for n,title,title_ar,desc,desc_ar,href,link,link_ar in pillars)
    return f'''<section class="difference" id="the-difference"><div class="wrap">
      <div class="difference-lead">
        <div>
          {T('WHAT MAKES ONESPACE DIFFERENT', 'ما الذي يميّز OneSpace', 'span', 'eyebrow')}
          {T('More than emotional connection. A life you build together.', 'أكثر من تواصل عاطفي... حياة تبنيانها معًا.', 'h2')}
        </div>
        {T('Love letters and daily gestures matter. What makes OneSpace different is what happens beyond them: share ideas from other apps, edit together, compare options, discuss decisions and put your plans into action.', 'رسائل الحب واللفتات اليومية مهمة، لكن ما يميز OneSpace هو ما بعدها: تشاركا الأفكار من تطبيقات أخرى، وعدّلاها معًا، وقارنا الخيارات، وتناقشا في القرارات، وحوّلا خططكما إلى واقع.', 'p', 'lead')}
      </div>
      <div class="difference-grid">{lines}</div>
      <div class="difference-outro"><a href="compare.html" class="btn btn-ghost">{T('Discover why OneSpace is different', 'اكتشفا الفرق مع OneSpace')}</a></div>
    </div></section>'''



def page_compare():
    h = head('compare.html', 'Why OneSpace is different — connected sharing, planning and decisions', 'لماذا يختلف OneSpace — مشاركة وتخطيط وقرارات مترابطة',
             'Discover the difference: smart sharing into unified lists, two-way collaboration, side-by-side choices, trips and occasion budgets in one private couples app.',
             'اكتشف الفرق: مشاركة ذكية إلى قوائم موحدة، وتعاون بين الشريكين، ومقارنة الخيارات، وتخطيط الرحلات وميزانيات المناسبات في تطبيق خاص للأزواج.')
    return h + page_hero('Why OneSpace', 'لماذا OneSpace',
                         'Beyond connection: plan and decide together.', 'أكثر من التواصل: خططا وقررا معًا.',
                         'Emotional connection is only part of a shared life. OneSpace brings your ideas, comparisons, two-way discussions, decisions and plans together in one private space for two.',
                         'التواصل العاطفي جزء من حياتكما المشتركة، وليس كل شيء. يجمع OneSpace الأفكار والمقارنات والنقاشات المتبادلة والقرارات والخطط في مساحة واحدة خاصة بكما.') + \
       differentiation_section() + f"""
<section class="difference-compare" aria-labelledby="compare-tools-title"><div class="wrap">
  <div class="sec-head center">
    {T('The real comparison', 'المقارنة الفعلية', 'span', 'eyebrow')}
    {T('Separate tools or one connected space?', 'أدوات متفرقة أم مساحة مترابطة؟', 'h2', '', 'id="compare-tools-title"')}
    {T('Chats, notes and calendars are useful on their own. OneSpace is designed to keep a couple’s decisions and follow-up alongside the details.', 'المحادثات والملاحظات والتقويمات مفيدة كلٌّ على حدة. أما OneSpace فيربط قراراتكما ومتابعتها بالتفاصيل التي تخصها.', 'p', 'lead')}
  </div>
  {compare_table()}
  <p class="muted center" style="margin-top:18px">{T('This compares everyday workflows, not an exhaustive audit of other apps. Features and integrations can vary by product.', 'هذه مقارنة لطرق الاستخدام اليومية، وليست مراجعة شاملة للتطبيقات الأخرى. قد تختلف المزايا والتكاملات من تطبيق لآخر.')}</p>
</div></section>
""" + story_case_cards(['sofa-that-both-of-us-chose', 'course-together-across-time-zones']) + value_grid() + cta_band() + foot()


def page_index():
    h = head('index.html', 'OneSpace — the private couples app for plans, love and memories', 'OneSpace — تطبيق الأزواج الخاص للخطط والحب والذكريات',
             'OneSpace is a private couples app: shared calendar, lists, trips, little gestures, letters, counters and memories — for couples living together or long distance.',
             'OneSpace تطبيق خاص للأزواج: تقويم وقوائم ورحلات ولمسات صغيرة ورسائل وعدّادات وذكريات مشتركة — للأزواج معًا أو عن بُعد.')
    tabs = [
        ('today', '📅', 'Today', 'اليوم', 'Open the app, know what matters.', 'افتح التطبيق واعرف ما يهم.',
         [('What your partner sent while you were away', 'ما أرسله شريكك أثناء غيابك'), ('What needs your answer', 'ما يحتاج ردّك'), ('Two clocks and weathers when you live apart', 'ساعتان وطقسان حين تكونان متباعدين')], 'today', 'features.html#today'),
        ('remember', '🔖', 'Remember', 'تذكّر', 'Your story, counted and kept.', 'قصتكما، محسوبة ومحفوظة.',
         [('Counters for the day itself and its anniversary', 'عدّادات لليوم نفسه ولذكراه'), ('Your places on a map — been there and bucket list', 'أماكنكما على خريطة — ما زرتماه وقائمة الأحلام'), ('Notes, contact cards, memories and scrapbooks', 'ملاحظات وبطاقات تواصل وذكريات وألبومات')], 'counters', 'features.html#remember'),
        ('coordinate', '🧭', 'Coordinate', 'نسّق', 'Decide together, without the back-and-forth.', 'قررا معًا دون أخذ ورد.',
         [('One shared calendar, lists and reminders', 'تقويم وقوائم وتذكيرات مشتركة'), ('Compare options, talk it through, decide', 'قارنا الخيارات وتناقشا وقررا'), ('Trips with flights, packing and documents', 'رحلات بالطيران والتجهيز والمستندات')], 'activity', 'features.html#coordinate'),
        ('connect', '♡', 'Connect', 'تواصل', 'Small, daily ways to feel close.', 'طرق يومية صغيرة للشعور بالقرب.',
         [('A hug or “proud of you” in one tap, in your words', 'حضن أو «فخور بك» بنقرة وبكلماتك'), ('Letters sealed until the right day', 'رسائل مغلقة حتى اليوم المناسب'), ('A one-minute daily check-in', 'تواصل يومي في دقيقة')], 'love', 'features.html#connect'),
        ('me', '👤', 'Me', 'أنا', 'Set it up your way.', 'اضبطه على طريقتك.',
         [('Nine themes — try them on the phone', 'تسع سمات — جرّبها على الهاتف'), ('English and Arabic, right to left', 'العربية والإنجليزية من اليمين لليسار'), ('Private items, download your data, delete any time', _nov_ar('Private items, download your data, delete any time'))], 'ourspace', 'features.html#me'),
    ]
    btns = ''.join(f'<button class="step" type="button" role="tab" data-view="{k}" aria-selected="{"true" if i == 0 else "false"}"><b>{ic} {T(e, ar)}</b>{T(t, tar)}</button>'
                   for i, (k, ic, e, ar, t, tar, _, _, _) in enumerate(tabs))
    views = ''.join(f'<div data-view-of="tabs" data-view-name="{k}"{" hidden" if i else ""}>{(device("themes/today_cleanLight", "Today tab", ar, themed=True) if k == "today" and has_shot("themes/today_cleanLight") else device(k, e + " tab", ar, fallback=phone(SCREENS[sc](), "clean", label=e + " tab", label_ar=ar)))}'
                    f'<ul class="ticks" style="max-width:320px">{"".join(f"<li>{T(x, y)}</li>" for x, y in pts)}</ul><a class="more" href="{href}" style="font-weight:700">{T("More about " + e + " →", "المزيد عن " + ar + " ←")}</a></div>'
                    for i, (k, ic, e, ar, t, tar, pts, sc, href) in enumerate(tabs))
    marquee_items = [('🛒', 'Groceries for Friday · 4 left', 'مشتريات الجمعة · بقي 4'), ('💍', 'Anniversary in 12 days', 'الذكرى بعد 12 يومًا'), ('💌', 'A letter opens on Saturday', 'رسالة تُفتح يوم السبت'),
                     ('🏔', 'Lina picked Banff', 'اختارت لينا بانف'), ('🤗', 'Omar sent a hug', 'أرسل عمر حضنًا'), ('✈️', 'YYZ → IST · packing 7/12', 'تورونتو ← إسطنبول · التجهيز 7/12'),
                     ('🧾', 'Internet bill due Thursday', 'فاتورة الإنترنت الخميس'), ('📍', 'Santorini added to the bucket list', 'أُضيفت سانتوريني إلى قائمة الأحلام'), ('🎂', 'Gift ideas: 3 shortlisted', 'أفكار هدايا: 3 في القائمة'),
                     ('😊', 'Lina felt great today', 'شعرت لينا اليوم بأنها رائعة'), ('🎬', 'Movie night · Friday 9 PM', 'سهرة فيلم · الجمعة 9 م'), ('☕', 'Our café · 12 visits', 'مقهانا · 12 زيارة')]
    chips = ''.join(f'<span class="chip">{i} {T(e, a)}</span>' for i, e, a in marquee_items)
    app_ld = {'@context': 'https://schema.org', '@type': 'MobileApplication', 'name': 'OneSpace', 'operatingSystem': 'Android',
              'applicationCategory': 'LifestyleApplication', 'description': 'A private app for couples: shared calendar, lists, trips, gestures, letters, counters and memories.',
              'inLanguage': 'en', 'url': BASE}
    rot = ''.join(f'<span class="{"on" if i == 0 else ""}">{T(e, a)}</span>' for i, (e, a) in enumerate([
        (x, _nov_ar(x)) for x in ('couples living together', 'couples 5,700 km apart', 'people on their own', 'couples planning a wedding', 'busy weeks')]))
    toasts = [('🤍', 'Lina sent you a hug', 'أرسلت لك لينا حضنًا', 'just now', 'الآن'), ('💌', 'A letter is waiting for you', 'رسالة تنتظرك', 'opens Saturday', 'تُفتح السبت'),
              ('✅', 'Lina ticked “Buy flowers”', 'أنهت لينا «شراء الورد»', '2 min ago', 'قبل دقيقتين'), ('🏔', 'You both picked Banff', 'اخترتما بانف كلاكما', 'decision saved', 'حُفظ القرار')]
    toast_data = ''.join(f'<template data-toast><span class="e">{i}</span><div>{T(a, b, "b")}{T(c, d)}</div></template>' for i, a, b, c, d in toasts)
    return h + f"""
<section class="hero-xl"><div class="wrap hero-grid">
  <span class="floaty" style="left:4%;top:12%">♥</span><span class="floaty" style="left:44%;top:78%;animation-delay:-3s">✦</span><span class="floaty" style="right:4%;top:70%;animation-delay:-6s;color:var(--coral)">♥</span>
  <div>
    {N('Two of Us. One Space.', 'span', 'eyebrow')}
    <h1>{T('The private home for the life', 'مساحتكما الخاصة')} <span class="serif accent">{T('you share.', 'لكل تفاصيل حياتكما.')}</span></h1>
    <p class="lead">{N('Save what matters from every app, then plan, decide and remember — in one private space. In a relationship or not, OneSpace is your own assistant, and when you’re ready it becomes a space for two. Made for')} <b class="rotator" style="color:var(--teal)">{rot}</b></p>
    <div class="cta-row">
      <a class="btn btn-primary" href="#founding" data-track="hero_join">{T('Join the Founding 500 — free', 'انضم إلى المؤسسين الـ500 — مجانًا')}</a>
      <a class="btn btn-ghost" href="how-it-works.html" data-track="hero_demo">▶ {T('Try the demo', 'جرّب العرض')}</a>
    </div>
    <div class="avatars" style="max-width:360px;margin-top:30px"><span class="av o">O</span><span class="av-line"></span><span class="av l">L</span></div>
    <div class="trust">{N('Private by design')}{T('No ads, no data selling', 'بلا إعلانات ولا بيع للبيانات')}{T('English & العربية', 'العربية والإنجليزية')}</div>
  </div>
  <div class="stage">
    {hero_devices()}
    <div class="toast t1 live" data-toast-slot></div>{toast_data}
    <div class="toast t2"><span class="e">✈️</span><div>{T('Istanbul in 6 days', 'إسطنبول بعد 6 أيام', 'b')}{T('Packing 7 of 12', 'التجهيز 7 من 12')}</div></div>
  </div>
</div></section>
<div class="marquee" aria-hidden="true"><div class="marquee-track">{chips}{chips}</div></div>
{solo_section()}
{differentiation_section()}
{watch_section()}
{connect_care_preview()}

<section><div class="wrap">
  <div class="sec-head center">{T('Sound familiar?', 'هل يبدو هذا مألوفًا؟', 'span', 'eyebrow')}<h2>{T('Love is easy.', 'الحب جميل…')} <span class="serif accent">{T('Logistics aren’t.', 'لكن التفاصيل محتاجة تنظيم.')}</span></h2>
  {T('Every couple has these conversations. OneSpace quietly takes care of them, so your chats can be about you again.', 'كل زوجين يمرّان بهذه المحادثات. يتولاها OneSpace بهدوء، لتعود محادثاتكما عنكما من جديد.', 'p', 'lead')}</div>
  <div class="pains">
    {pain('Did you book the dentist? 🦷', 'هل حجزت موعد طبيب الأسنان؟ 🦷', 'I thought YOU were doing it 😅', 'ظننت أنكِ ستحجزينه 😅', 'Reminders that belong to someone — and show up in their Today.', 'تذكيرات لها صاحب — وتظهر في «اليوم» لديه.', shot='lists')}
    {pain('What was that restaurant we loved in Lisbon?', 'ما اسم المطعم الذي أحببناه في لشبونة؟', 'No idea… it had blue chairs?', 'لا أذكر… كانت كراسيه زرقاء؟', 'Our places: every spot you loved, pinned on your own map.', 'أماكننا: كل مكان أحببتماه، على خريطتكما الخاصة.', shot='places')}
    {pain('Sorry, did I wake you? 🙈', 'آسفة، هل أيقظتك؟ 🙈', 'It’s 3 a.m. here…', 'الساعة 3 فجرًا هنا…', 'Two clocks and two weathers on Today — know before you call.', 'ساعتان وطقسان في «اليوم» — اعرف قبل أن تتصل.', shot='clocks')}
    {pain('Which sofa did we say? The grey one?', 'أي أريكة اتفقنا عليها؟ الرمادية؟', 'I sent you 14 links last week…', 'أرسلت لكِ 14 رابطًا الأسبوع الماضي…', 'Activities: options side by side, both your picks, one decision.', 'الأنشطة: خيارات جنبًا إلى جنب، واختيار كل منكما، وقرار واحد.', shot='options')}
    {pain('Is it our anniversary this month?!', 'هل ذكرانا هذا الشهر؟!', '…it was last Tuesday 💔', '…كانت الثلاثاء الماضي 💔', 'Counters and occasions that remind you weeks before — with gift ideas.', 'عدّادات ومناسبات تذكّرك قبلها بأسابيع — مع أفكار هدايا.', shot='counter')}
    {pain('Who has the passports?', 'من معه الجوازات؟', 'Me? I thought they were in your bag', 'أنا؟ ظننتها في حقيبتك', 'Trips with a shared packing list — who brings what, ticked off.', 'رحلات بقائمة تجهيز مشتركة — من يحضر ماذا، مع علامة الإنجاز.', shot='trip')}
  </div>
</div></section>

{value_grid()}

<section class="tint"><div class="wrap">
  <div class="sec-head center">{T('Everything for two', 'كل شيء لاثنين', 'span', 'eyebrow')}<h2>{T('One app instead of', 'تطبيق واحد بدل')} <span class="serif accent">{T('ten chats, three lists and a lost calendar.', 'عشر محادثات وثلاث قوائم وتقويم ضائع.')}</span></h2></div>
  <div class="bento">
    <div class="bx b-2 b-tall peach reveal"><div class="ico i-coral">⏳</div>{T('Counters that understand dates', 'عدّادات تفهم التواريخ', 'h3')}{T('The day itself and its anniversary — with progress all the way there.', 'اليوم نفسه وذكراه — مع تقدّم حتى الوصول.', 'p')}
      <div class="viz"><div class="big-count">164 <small>{T('days', 'يومًا')}</small></div>{T('until our 6th anniversary', 'حتى ذكرانا السادسة', 'p')}<div class="bar"><i style="--w:58%"></i></div>
      <div style="height:16px"></div><div class="big-count" style="font-size:38px">8 <small>{T('years since we met', 'سنوات منذ التقينا')}</small></div></div></div>
    <div class="bx b-2 reveal"><div class="ico i-rose">💌</div>{T('Letters that wait', 'رسائل تنتظر', 'h3')}{T('Write today, sealed until a birthday, a landing or a hard day.', 'اكتب اليوم، مغلقة حتى عيد ميلاد أو يوم وصول أو يوم صعب.', 'p')}<div class="viz"><div class="envelope"><span class="seal">♥</span></div></div></div>
    <div class="bx b-2 mint reveal"><div class="ico i-teal">📍</div>{T('Our places, on a map', 'أماكننا على خريطة', 'h3')}{T('Been there and bucket list. Share straight from Google Maps.', 'ما زرتماه وقائمة الأحلام. شارك مباشرة من خرائط Google.', 'p')}
      <div class="viz"><div class="mini-map"><span class="pin" style="left:28%;top:50%">❤️</span><span class="pin" style="left:58%;top:40%;animation-delay:.3s">❤️</span><span class="pin" style="left:78%;top:78%;animation-delay:.6s">🧭</span><span class="pin" style="left:42%;top:86%;animation-delay:.9s">🧭</span></div></div></div>
    <div class="bx b-2 sun reveal"><div class="ico i-gold">🧳</div>{T('Trips, packed together', 'رحلات نجهّزها معًا', 'h3')}<div class="viz"><ul class="check-list">
      <li class="d">{T('Passports — Lina', 'الجوازات — لينا')}</li><li class="d">{T('Hotel booking — Omar', 'حجز الفندق — عمر')}</li><li>{T('Travel adapter — Omar', 'محوّل الكهرباء — عمر')}</li></ul></div></div>
    <div class="bx b-2 lilac reveal"><div class="ico i-violet">🌤</div>{T('A one-minute check-in', 'تواصل يومي في دقيقة', 'h3')}{T('How was today, really? Pick a face, add one honest line.', 'كيف كان يومك حقًا؟ اختر وجهًا وأضف سطرًا صادقًا.', 'p')}<div class="viz"><div class="faces"><span>😞</span><span>😕</span><span>🙂</span><span class="on">😊</span><span>🤩</span></div></div></div>
    <div class="bx b-4 ink reveal"><div class="ico" style="background:rgba(255,255,255,.1)">🌙</div>{T('Arabic and English, side by side', 'العربية والإنجليزية جنبًا إلى جنب', 'h3')}{T('Each of you picks your language. Every screen works right to left.', 'يختار كل منكما لغته. وكل شاشة تعمل من اليمين لليسار.', 'p')}
      <div class="viz lang-pair"><div>🤗 <b style="color:#fff">Lina sent you a hug</b><br><span style="color:#B9C3D8">“Sending you a big, warm hug.”</span></div><div dir="rtl" style="font-family:var(--font-ar)">🤗 <b style="color:#fff">أرسل لكِ عمر حضنًا</b><br><span style="color:#B9C3D8">«أرسل لكِ حضنًا كبيرًا ودافئًا.»</span></div></div></div>
    <div class="bx b-2 reveal"><div class="ico i-green">🎁</div>{T('Surprises stay secret', 'المفاجآت تبقى سرًا', 'h3')}{T('Mark a gift or an occasion “Only me”. Your partner never sees it.', 'اجعل الهدية أو المناسبة «أنا فقط». لن يراها شريكك أبدًا.', 'p')}<div class="viz"><span class="chip">🔒 {T('Only me', 'أنا فقط')}</span> <span class="chip">💰 $370 {T('left', 'متبقٍ')}</span></div></div>
  </div>
  <p class="center" style="margin-top:28px"><a class="btn btn-ghost" href="features.html">{T('See every feature →', 'شاهد كل المزايا ←')}</a></p>
</div></section>

<section><div class="wrap">
  <div class="sec-head center">{N('However you live', 'span', 'eyebrow')}<h2>{N('Together, apart or on your own,')} <span class="serif accent">{N('it fits your life.')}</span></h2>
  <div class="seg" role="tablist" data-views="live" style="margin-top:18px"><button type="button" role="tab" data-view="apart" aria-selected="true">🌍 {T('Living apart', 'متباعدان')}</button><button type="button" role="tab" data-view="together" aria-selected="false">🏡 {T('Living together', 'معًا')}</button><button type="button" role="tab" data-view="solo" aria-selected="false">🙋 {N('On my own')}</button></div></div>
  <div data-view-of="live" data-view-name="apart">{cities_panel()}</div>
  <div data-view-of="live" data-view-name="together" hidden>{home_panel()}</div>
  <div data-view-of="live" data-view-name="solo" hidden>{solo_panel()}</div>
</div></section>

<section id="tour" data-theme-scope><div class="wrap"><div class="playground" data-pg="clean">
  <div class="sec-head center">{T('Try it right here', 'جرّبه هنا', 'span', 'eyebrow')}<h2>{T('Five tabs.', 'خمسة تبويبات.')} <span class="serif accent">{T('Nine moods.', 'تسعة أمزجة.')}</span></h2>
  {T('Tap a tab, then pick a theme — the phone and this whole section change, just like the real app.', 'انقر على تبويب ثم اختر سمة — يتغير الهاتف وهذا القسم كله، تمامًا كما في التطبيق.', 'p', 'lead')}</div>
  <div class="tour tour3">
    <div class="steps" role="tablist" data-views="tabs">{btns}</div>
    <div class="stage" style="padding-top:0">{views}</div>
    <div><h3 style="margin-bottom:12px">{T('Pick a theme', 'اختر سمة')}</h3><div class="swatches">{swatches()}</div>
    {('<div style="margin-top:20px">' + device('themes/love_cleanLight', 'A little love in the chosen theme', 'لمسة حب بالسمة المختارة', 'sm', themed=True) + '</div>') if has_shot('themes/love_cleanLight') else ''}</div>
  </div>
</div></div></section>

{theme_wall()}
{smart_utilities()}
<section class="warm"><div class="wrap">
  <p class="promise reveal">{T('“Your relationship isn’t content. Nothing you put in OneSpace is shown to anyone but the two of you — no feed, no followers, no ads, and never sold.”', '«علاقتكما ليست محتوى. لا يُعرض شيء تضعانه في OneSpace إلا لكما — بلا منشورات ولا متابعين ولا إعلانات، ولا يُباع أبدًا.»')}</p>
  <p class="center muted" style="margin-top:14px">— {T('Our promise', 'وعدنا')}</p>
  <div class="numbers">
    <div class="reveal"><b>2</b>{T('people per space', 'شخصان لكل مساحة')}</div><div class="reveal"><b>5</b>{T('simple tabs', 'تبويبات بسيطة')}</div>
    <div class="reveal"><b>9</b>{T('themes', 'سمات')}</div><div class="reveal"><b>2</b>{T('languages', 'لغتان')}</div><div class="reveal"><b>0</b>{T('ads, ever', 'إعلانات، أبدًا')}</div>
  </div>
</div></section>

<section><div class="wrap">
  <div class="sec-head" style="display:flex;justify-content:space-between;align-items:end;max-width:none;gap:20px;flex-wrap:wrap"><div>{N('Guides', 'span', 'eyebrow')}{T('Ideas worth stealing.', 'أفكار تستحق التجربة.', 'h2', '', 'style="margin-top:10px"')}</div><a class="btn btn-ghost" href="guides.html">{T('All guides →', 'كل الأدلة ←')}</a></div>
  <div class="grid g3">{guide_cards()}</div>
</div></section>

{ai_review_preview() if False else ''}
{store_section()}

<section id="founding"><div class="wrap"><div class="band"><div class="cta-band" style="align-items:start">
  <div>
    {T('The Founding 500', 'المؤسسون الـ500', 'span', 'eyebrow')}
    <h2>{N('Be one of the')} <span class="serif" style="color:#F3A27E">{N('first 500 people.')}</span></h2>
    {N('Registration is open now for Android and iPhone. The first 500 people to confirm — on their own or as a couple — become Founder Members, with free early access when their version is ready and a say in what we build. Founder benefits will be announced before any pricing.', 'p', 'lead')}
    <ul class="ticks"><li>{T('<b>Free</b> during early access', '<b>مجاني</b> خلال الوصول المبكر')}</li><li>{T('<b>Registration now:</b> Android and iPhone', '<b>التسجيل مفتوح الآن:</b> أندرويد وآيفون')}</li><li>{T('<b>Your email only</b> for the invite and launch updates', '<b>بريدك فقط</b> للدعوة وتحديثات الإطلاق')}</li></ul>
  </div>
  {founding_entry()}
</div></div></div></section>
<script type="application/ld+json">{json.dumps(app_ld)}</script>
""" + foot()



def founding_entry():
    """One conversion destination: the full Founder form lives on join.html."""
    return f'''<div class="panel"><div class="join-entry" data-founder-entry>
      <span class="join-entry-icon" aria-hidden="true">♡</span>
      {T('Reserve your Founder spot', 'احجز مكانك كمؤسس', 'h3')}
      <a class="btn btn-primary" href="join.html" data-track="founder_join_canonical">{T('Join the Founding 500', 'انضم إلى المؤسسين الـ500')}</a>
      {T('We never share your email. <a href="privacy.html">Privacy</a>', 'لا نشارك بريدك أبدًا. <a href="privacy.html">الخصوصية</a>', 'p')}
    </div></div>'''



def founding_form(prefix, full=False):
    ek = K('you@example.com', 'you@example.com')
    extra = ''
    if full:
        extra = f"""<label>{N('How do you live?')}</label>
      {radio('living', [('apart', 'Living apart', 'متباعدان'), ('together', 'Living together', 'معًا'), ('solo', 'On my own', _nov_ar('On my own')), ('both', 'A bit of both', 'بين هذا وذاك'), ('soon', 'Moving in soon', 'سننتقل للعيش معًا قريبًا')])}
      <div class="f2"><div><label for="{prefix}-name">{T('Your first name', 'اسمك الأول')}</label><input id="{prefix}-name" name="name" autocomplete="given-name" maxlength="60"></div>
      <div><label for="{prefix}-l">{T('Language', 'اللغة')}</label><select id="{prefix}-l" name="language"><option value="en">English</option><option value="ar">العربية</option>{T('Both', 'كلاهما', 'option', attrs='value="both"')}</select></div></div>
      <label for="{prefix}-s">{T('How did you hear about us?', 'كيف عرفت عنا؟')}</label><select id="{prefix}-s" name="source">{T('A friend', 'صديق', 'option', attrs='value="friend"')}{T('My partner', 'شريكي', 'option', attrs='value="partner"')}{T('Social media', 'وسائل التواصل', 'option', attrs='value="social"')}{T('Search', 'البحث', 'option', attrs='value="search"')}{T('Other', 'أخرى', 'option', attrs='value="other"')}</select>
      <label for="{prefix}-m">{T('Anything you hope OneSpace helps with? (optional)', 'ما الذي تأمل أن يساعدكما فيه OneSpace؟ (اختياري)')}</label><textarea id="{prefix}-m" name="message" maxlength="1500" style="min-height:80px"></textarea>"""
    return f"""<div class="panel">
    <form data-form="join" data-done="{prefix}-done" novalidate>
      {T('Reserve a Founder spot — Android or iPhone', 'احجز مكانك بين المؤسسين — أندرويد أو آيفون', 'h3')}
      <div class="invite-note" hidden>💞 {N('Your partner invited you — you’ll join the Founding 500 together.')}</div>
      <input type="hidden" name="invite" value="">
      <label for="{prefix}-email">{T('Email *', 'البريد الإلكتروني *')}</label><input id="{prefix}-email" name="email" type="email" required autocomplete="email" placeholder="you@example.com" data-i18n-attr="placeholder:{ek}">
      <label>{T('Your phone — both platforms can register now', 'نوع هاتفك — التسجيل مفتوح للمنصتين الآن')}</label>
      {radio('platform', [('android', 'Android', 'أندرويد'), ('iphone', 'iPhone', 'iPhone'), ('both', 'We use both', 'نستخدم الاثنين'), ('unsure', 'Not sure yet', 'لست متأكدًا')])}
      {extra}
      <input class="hp" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">
      <label class="check"><input type="checkbox" name="consent" required> {T('I agree to receive OneSpace product and launch updates by email.', 'أوافق على تلقي تحديثات منتج OneSpace وإطلاقه بالبريد.')}</label>
      <div class="cta-row" style="margin-top:16px"><button class="btn btn-primary" type="submit" data-track="join_submit">{T('Join the Founding 500', 'انضم إلى المؤسسين الـ500')}</button></div>
      <p class="status" role="status" aria-live="polite"></p>
      <p class="muted" style="font-size:13px;margin:6px 0 0">{T('We never share your email. <a href="privacy.html">Privacy</a>', 'لا نشارك بريدك أبدًا. <a href="privacy.html">الخصوصية</a>')}</p>
    </form>
    <div id="{prefix}-done" class="done" tabindex="-1">
      <div style="font-size:46px">📬</div>
      {T('Check your inbox', 'تفقّد بريدك', 'h3', '', 'style="font-size:24px"')}
      {N('We sent you a link from <b>founders@onespace.live</b>. Confirm your email to become a Founder Member — then you can invite your partner if you like.', 'p', 'muted')}
      {T('Nothing after a few minutes? Check spam or Promotions, then try again.', 'لم يصل شيء بعد دقائق؟ تفقّد البريد العشوائي أو العروض ثم حاول مجددًا.', 'p', 'muted', 'style="font-size:14px"')}
      <p style="margin-top:16px"><a href="how-it-works.html">{T('While you wait: try the demo →', 'أثناء الانتظار: جرّب العرض ←')}</a></p>
    </div>
  </div>"""


def swatches():
    themes = [('clean', '#3768BA', 'Clean Light', 'فاتح نقي'), ('coral', '#E8745A', 'Coral & Teal', 'مرجاني وفيروزي'), ('rose', '#BA688B', 'Soft Rose', 'وردي ناعم'),
              ('teal', '#1F6E78', 'Ocean Teal', 'فيروزي المحيط'), ('sage', '#5E8C61', 'Sage Garden', 'حديقة المريمية'), ('lavender', '#8A6FC2', 'Lavender Dusk', 'غسق الخزامى'),
              ('sand', '#B98348', 'Desert Sand', 'رمال الصحراء'), ('midnight', '#4A80D8', 'Midnight Blue', 'أزرق منتصف الليل'), ('mono', '#62646B', 'Monochrome', 'أحادي اللون')]
    pal = dict(PALETTES)
    return ''.join(f'<button class="swatch" type="button" data-theme-pick="{k}" data-palette="{pal[k]}" aria-pressed="{"true" if k == "clean" else "false"}"><i style="background:{c}"></i>{T(e, a)}</button>' for k, c, e, a in themes)


def trust_card(i, c, h, har, p, par):
    return f'<div class="card reveal"><div class="ico {c}">{i}</div>{T(h, har, "h3")}{T(p, par, "p")}</div>'


def feature_block(anchor, eyebrow, eyebrow_ar, h2, h2_ar, lead, lead_ar, items, screen_key, theme, rev=False, tint=False, label='', real=None, visual=None):
    lis = ''.join(f'<li>{T(f"<b>{a}</b> — {b}", f"<b>{c}</b> — {d}")}</li>' for a, b, c, d in items)
    cls = ' class="tint"' if tint else ''
    return f'''<section id="{anchor}"{cls}><div class="wrap split{' rev' if rev else ''}">
  <div class="stage">{visual if visual is not None else screen(screen_key, theme, label or h2, h2_ar, real=real)}</div>
  <div>{T(eyebrow, eyebrow_ar, 'span', 'eyebrow')}{T(h2, h2_ar, 'h2')}{T(lead, lead_ar, 'p', 'lead')}<ul class="ticks">{lis}</ul></div>
</div></section>'''


def page_features():
    h = head('features.html', 'Features — OneSpace', 'المزايا — OneSpace',
             'Every OneSpace feature by tab: Today, Remember, Coordinate, Connect and Me — calendar, lists, trips, occasions, letters, counters, places and more.',
             'كل مزايا OneSpace حسب التبويب: اليوم وتذكّر ونسّق وتواصل وأنا — التقويم والقوائم والرحلات والمناسبات والرسائل والعدّادات والأماكن وغيرها.')
    jump = ''.join(f'<a class="chip" href="#{a}">{i} {T(e, ar)}</a>' for a, i, e, ar in [
        ('today', '📅', 'Today', 'اليوم'), ('remember', '🔖', 'Remember', 'تذكّر'), ('coordinate', '🧭', 'Coordinate', 'نسّق'),
        ('trips', '✈️', 'Trips', 'الرحلات'), ('occasions', '🎁', 'Occasions', 'المناسبات'), ('connect', '♡', 'Connect', 'تواصل'), ('me', '👤', 'Me', 'أنا')])
    return h + page_hero('Features', 'المزايا', 'Everything you need, nothing you don’t.', _nov_ar('Everything you need, nothing you don’t.'),
                         'OneSpace is organised the way life actually works: what is happening today, what you want to remember, what you need to coordinate, how you stay close, and how you like things set up. Use it on your own or with your partner.',
                         _nov_ar('OneSpace is organised the way life actually works: what is happening today, what you want to remember, what you need to coordinate, how you stay close, and how you like things set up. Use it on your own or with your partner.'),
                         extra=f'<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:22px">{jump}</div>',
                         headline_html=N('Everything you need,') + ' <span class="serif accent">' + T('nothing you don’t.', 'ولا شيء زائد.') + '</span>') + \
        feature_block('today', 'Today', 'اليوم', 'Open the app, know what matters.', 'افتح التطبيق واعرف ما يهم.',
                      'Today brings together what needs your answer, what your partner sent and the next seven days — shaped by whether you live on your own, together or apart.',
                      _nov_ar('Today brings together what needs your answer, what your partner sent and the next seven days — shaped by whether you live on your own, together or apart.'),
                      [('Your day, side by side', 'your plans, your partner’s and what you do together, in one day view.', _nov_ar('Your day, side by side'), _nov_ar('your plans, your partner’s and what you do together, in one day view.')),
                       ('Since you were away', 'gestures, letters and updates you missed.', 'منذ غيابك', 'اللمسات والرسائل والتحديثات التي فاتتك.'),
                       ('Needs your attention', 'votes, decisions and items assigned to you.', 'يحتاج انتباهك', 'التصويتات والقرارات والعناصر المسندة إليك.'),
                       ('Two clocks & weather', 'when you live apart, see both cities at once.', 'ساعتان وطقس', 'حين تكونان متباعدين، شاهد المدينتين معًا.'),
                       ('Quick add', 'a reminder, to-do, note, place or trip in two taps.', 'إضافة سريعة', 'تذكير أو مهمة أو ملاحظة أو مكان أو رحلة بنقرتين.'),
                       ('Your shortcuts', 'pin the screens you use most.', 'اختصاراتك', 'ثبّت الشاشات التي تستخدمها كثيرًا.')], 'today', 'clean') + \
        feature_block('remember', 'Remember', 'تذكّر', 'Your shared memory, organised.', 'ذاكرتكما المشتركة، منظمة.',
                      'Counters for every special date, your places on a map, notes, contact cards and memories that become scrapbooks.',
                      'عدّادات لكل تاريخ خاص، وأماكنكما على خريطة، وملاحظات، وبطاقات تواصل، وذكريات تصبح ألبومات.',
                      [('Counters', 'days, weeks, months and years — the date itself and its anniversary, with progress bars.', 'العدّادات', 'أيام وأسابيع وأشهر وسنوات — التاريخ نفسه وذكراه، مع أشرطة تقدّم.'),
                       ('Linked dates', 'see the time between two moments, like first date → wedding.', 'تواريخ مرتبطة', 'شاهد المدة بين لحظتين، مثل الموعد الأول ← الزفاف.'),
                       ('Our places', 'been there and bucket list, pinned on a map, shared from Maps.', 'أماكننا', 'ما زرتماه وقائمة الأحلام، على خريطة، ومشاركة من الخرائط.'),
                       ('Memories & scrapbooks', 'stories, a daily selfie calendar, scrapbooks you can both edit, save as PDF.', 'الذكريات والألبومات', _nov_ar('stories, a daily selfie calendar, scrapbooks you can both edit, save as PDF.')),
                       ('Notes & contact cards', 'rich notes and the details you always need — sizes, the doctor, the plumber.', 'الملاحظات وبطاقات التواصل', 'ملاحظات منسقة والتفاصيل التي تحتاجها دائمًا — المقاسات والطبيب والسبّاك.')],
                      'places', 'teal', rev=True, tint=True) + \
        feature_block('coordinate', 'Coordinate', 'نسّق', 'Decide together, without the back-and-forth.', 'قررا معًا دون أخذ ورد.',
                      'A shared calendar, lists and reminders — plus activities where you each mark the options you like and decide together.',
                      'تقويم وقوائم وتذكيرات مشتركة — وأنشطة يحدد فيها كل منكما الخيارات التي تعجبه وتقرران معًا.',
                      [('Calendar', 'one calendar with work days, days off and public holidays for your country — sent one way to your phone calendar if you like.', 'التقويم', _nov_ar('one calendar with work days, days off and public holidays for your country — sent one way to your phone calendar if you like.')),
                       ('Who’s taking part', 'mark each event for you, your partner or both, in its own time zone.', _nov_ar('Who’s taking part'), _nov_ar('mark each event for you, your partner or both, in its own time zone.')),
                       ('To-do lists & reminders', 'assign to one of you or both, with due dates and repeats.', 'المهام والتذكيرات', 'أسندها لأحدكما أو لكليكما، بمواعيد وتكرار.'),
                       ('Activities', 'compare options, vote, talk it through with voice notes and @mentions, then decide.', 'الأنشطة', 'قارنا الخيارات وصوّتا وتحدثا بالرسائل الصوتية والإشارات ثم قررا.'),
                       ('Nudge partner', 'a gentle reminder to your partner, without nagging.', _nov_ar('Nudge partner'), _nov_ar('a gentle reminder to your partner, without nagging.'))],
                      'activity', 'sage') + \
        feature_block('trips', 'Trips', 'الرحلات', 'Every trip in one place — flights to packing.', 'كل رحلة في مكان واحد — من الطيران إلى التجهيز.',
                      'Flights, stays, a shared packing list and private travel documents only the two of you can open.',
                      'الطيران والإقامة وقائمة تجهيز مشتركة ومستندات سفر خاصة لا يفتحها سواكما.',
                      [('Flights', 'routes, stops, baggage and prices for both directions.', 'الطيران', 'المسارات والتوقفات والأمتعة والأسعار للذهاب والعودة.'),
                       ('Packing', 'who brings what, with progress.', 'التجهيز', 'من يحضر ماذا، مع التقدّم.'),
                       ('Documents', 'bookings and tickets stored privately.', 'المستندات', 'الحجوزات والتذاكر محفوظة بخصوصية.')],
                      'trip', 'coral', rev=True, tint=True) + \
        feature_block('occasions', 'Occasions', 'المناسبات', 'Birthdays and anniversaries, planned in time.', 'أعياد الميلاد والذكريات، مُخطط لها في وقتها.',
                      'Gift ideas with prices and ratings, a budget that tracks what is left, and a reminder to start early. Keep it private for a surprise.',
                      'أفكار هدايا بالأسعار والتقييمات، وميزانية تتابع ما تبقى، وتذكير للبدء مبكرًا. واجعلها خاصة للمفاجأة.',
                      [('Gift ideas', 'considering, reserved, bought — never the same gift twice.', 'أفكار الهدايا', 'قيد الدراسة ومحجوزة ومشتراة — لن تتكرر الهدية.'),
                       ('Occasion budget', 'see what is spent and what is left.', 'ميزانية المناسبة', 'شاهد ما صُرف وما تبقى.'),
                       ('Only me', 'surprises stay hidden from your partner.', 'أنا فقط', 'المفاجآت تبقى مخفية عن شريكك.')],
                      'occasion', 'rose') + \
        connect_care_preview() + \
        smart_utilities() + \
        f'''<section id="me" class="dark" data-theme-scope><div class="wrap split">
  <div>{T('Me', 'أنا', 'span', 'eyebrow')}{T('Set it up your way.', 'اضبطه على طريقتك.', 'h2')}
  {N('Nine themes, Arabic or English, notifications grouped by day, privacy controls and a download of your data.', 'p', 'lead')}
  <div class="swatches" style="margin-top:24px">{swatches()}</div>
  <ul class="ticks"><li>{T('<b>Notifications that explain themselves</b> — who, what and when, grouped by day.', '<b>إشعارات واضحة</b> — من وماذا ومتى، مجمعة حسب اليوم.')}</li>
  <li>{T('<b>Help without signing in</b> — contact us even if you are locked out.', '<b>مساعدة دون تسجيل الدخول</b> — تواصل معنا حتى لو لم تستطع الدخول.')}</li></ul></div>
  <div class="phones">{screen('quickadd', 'clean', 'Appearance and themes', 'المظهر والسمات', 'sm', real='appearance')}{screen('memories', 'clean', 'Me tab', 'تبويب أنا', 'sm', real='me')}</div>
</div></section>''' + cta_band() + foot()



# ------------------------------------------- rich, practical couple journeys
def journey_text(translations, tag='span', cls=''):
    """The localized website is built from shared English/Arabic DOM."""
    return T(translations[0], translations[1], tag, cls)


def journey_preview_card(journey, index):
    return ('<a class="story-preview journey-preview reveal" href="scenarios.html#story-' + journey['slug'] + '">'
            + '<span class="journey-preview-number" aria-hidden="true">' + f'{index:02d}' + '</span>'
            + journey_text(journey['title'], 'h3')
            + journey_text(journey['teaser'], 'p')
            + '<span class="story-preview-more">' + journey_text(JOURNEY_UI['read'])
            + ' <span aria-hidden="true">↗</span></span></a>')


def story_case_cards(slugs):
    """Small curated taste only; never add long content to the homepage."""
    selected = [next(j for j in JOURNEYS if j['slug'] == slug) for slug in slugs]
    tiles = ''.join(journey_preview_card(j, i) for i, j in enumerate(selected, 1))
    return ('<section class="story-case-strip"><div class="wrap">'
            + '<div class="sec-head center">' + journey_text(JOURNEY_UI['previewHeading'], 'h2') + '</div>'
            + '<div class="story-preview-grid story-cases">' + tiles + '</div>'
            + '<p class="story-disclaimer">' + journey_text(JOURNEY_UI['fiction'])
            + '</p></div></section>')


def story_previews(apart):
    mode = apart if isinstance(apart, str) else ('apart' if apart else 'together')
    journeys = [j for j in JOURNEYS if j['mode'] == mode]
    intro = {'apart': JOURNEY_UI['apartDescription'], 'together': JOURNEY_UI['togetherDescription'],
             'solo': JOURNEY_UI['soloDescription']}[mode]
    heading = JOURNEY_UI['previewHeading'] if mode != 'solo' else ROWS_BY_EN['Real-life stories']
    more = JOURNEY_UI['soloMore'] if mode == 'solo' else JOURNEY_UI['more']
    fiction = JOURNEY_UI['soloFiction'] if mode == 'solo' else JOURNEY_UI['fiction']
    first = ''.join(journey_preview_card(j, i + 1) for i, j in enumerate(journeys[:3]))
    hidden = ''.join(journey_preview_card(j, i + 4) for i, j in enumerate(journeys[3:]))
    return ('<section class="story-preview-section journey-previews"><div class="wrap">'
            + '<div class="sec-head center">' + journey_text(heading, 'h2')
            + journey_text(intro, 'p', 'muted') + '</div>'
            + '<div class="story-preview-grid">' + first + '</div>'
            + '<details class="journey-show-more"><summary>' + journey_text(more)
            + '</summary>'
            + '<div class="story-preview-grid journey-additional">' + hidden + '</div></details>'
            + '<p class="journey-view-all"><a href="scenarios.html#story-season-' + mode + '">'
            + journey_text(JOURNEY_UI['navOpen']) + ' <span aria-hidden="true">↗</span></a></p>'
            + '<p class="story-disclaimer">' + journey_text(fiction)
            + '</p></div></section>')


def page_scenarios():
    h = head('scenarios.html', *JOURNEY_UI['pageTitle'][:2], *JOURNEY_UI['description'][:2])
    nav = ('<nav class="journey-switch" aria-label="' + JOURNEY_UI['jumpHint'][0] + '">'
           + '<a href="#story-season-apart">' + journey_text(JOURNEY_UI['apart']) + '</a>'
           + '<a href="#story-season-together">' + journey_text(JOURNEY_UI['together']) + '</a>'
           + '<a href="#story-season-solo">' + journey_text(JOURNEY_UI['solo']) + '</a>'
           + '</nav>')
    seasons = []
    for mode in ('apart', 'together', 'solo'):
        sequence = [j for j in JOURNEYS if j['mode'] == mode]
        label = JOURNEY_UI[mode]
        intro = JOURNEY_UI[mode + 'Description']
        episodes = []
        for index, journey in enumerate(sequence, 1):
            narrative = ''.join(
                '<div class="journey-beat"><span class="journey-beat-no" aria-hidden="true">'
                + f'{i:02d}' + '</span>' + journey_text(paragraph, 'p') + '</div>'
                for i, paragraph in enumerate(journey['stages'], 1))
            linked = ''.join(
                '<a class="journey-feature-chip" href="' + JOURNEY_FEATURES[key][5] + '">'
                + journey_text(JOURNEY_FEATURES[key]) + '</a>'
                for key in journey['features'])
            episodes.append(
                '<details class="story-episode journey-episode" id="story-' + journey['slug'] + '">'
                + '<summary><span class="journey-number" aria-hidden="true">' + f'{index:02d}'
                + '</span><span class="story-summary-copy">' + journey_text(journey['title'], 'strong')
                + journey_text(journey['teaser'], 'span')
                + '</span></summary>'
                + '<div class="journey-full"><div class="journey-intro-label">'
                + journey_text(JOURNEY_UI['followSolo' if mode == 'solo' else 'follow']) + '</div>'
                + '<div class="journey-beats">' + narrative + '</div>'
                + '<div class="journey-connections"><h3>' + journey_text(JOURNEY_UI['features'])
                + '</h3><div class="journey-feature-links">' + linked + '</div></div></div></details>')
        seasons.append(
            '<section class="story-season journey-season" id="story-season-' + mode + '"><div class="narrow">'
            + '<div class="story-season-head">' + journey_text(label, 'h2') + journey_text(intro, 'p', 'muted')
            + '</div><div class="journey-episodes">' + ''.join(episodes)
            + '</div></div></section>')
    return (h + page_hero(*JOURNEY_UI['eyebrow'][:2], *JOURNEY_UI['headline'][:2], *JOURNEY_UI['subhead'][:2])
            + '<div class="wrap">' + nav + '</div>'
            + '<div class="narrow"><p class="story-disclaimer">' + journey_text(JOURNEY_UI['fiction'])
            + ' ' + journey_text(JOURNEY_UI['soloFiction'])
            + '</p></div>' + ''.join(seasons) + cta_band() + foot())


def page_solo():
    page = 'on-my-own.html'
    h = head(page, 'OneSpace for people on their own', _nov_ar('OneSpace for people on their own'),
             'In a relationship or not, OneSpace is your own assistant: save links from any app, plan trips, never miss a birthday and keep your memories — then invite someone when you’re ready.',
             _nov_ar('In a relationship or not, OneSpace is your own assistant: save links from any app, plan trips, never miss a birthday and keep your memories — then invite someone when you’re ready.'))
    hero = page_hero('On my own', _nov_ar('On my own'), 'Your life, in one place.', _nov_ar('Your life, in one place.'),
                     'You don’t need a partner to use OneSpace. It gathers what you save in a dozen apps — links, places, films, gifts, plans — into one calm, private space. When someone special comes along, you can invite them. Until then, it’s all yours.',
                     _nov_ar('You don’t need a partner to use OneSpace. It gathers what you save in a dozen apps — links, places, films, gifts, plans — into one calm, private space. When someone special comes along, you can invite them. Until then, it’s all yours.'))
    points = [('📲', 'i-blue', 'One list per kind', 'Films, books, products and places from every app — sorted for you.'),
              ('🧭', 'i-teal', 'Decisions without 40 tabs', 'Compare flats, phones or courses side by side, with prices and notes.'),
              ('✈️', 'i-coral', 'Trips, sorted', 'Flight options, packing and documents in one trip.'),
              ('🎁', 'i-rose', 'Birthdays, never missed', 'Family and friends’ occasions with gift ideas and a budget.'),
              ('📸', 'i-violet', 'Your memories, kept', 'A daily selfie calendar, a feelings journal and scrapbooks you can save as PDF.'),
              ('💞', 'i-gold', 'Share later, on your terms', 'Invite a partner any time. Only me items stay private, always.')]
    cards = ''.join(trust_card(i, c, t, _nov_ar(t), d, _nov_ar(d)) for i, c, t, d in points)
    you = ('You', _nov_ar('You'))
    pains_html = ''.join(pain(q, _nov_ar(q), a, _nov_ar(a), r, _nov_ar(r), who=you[0], who_ar=you[1]) for q, a, r in [
        ('Where did I save that flat?', 'Somewhere between WhatsApp, three browsers and a screenshot…', 'Activities: every option you shared, side by side, with your notes.'),
        ('Is Mum’s birthday this week?!', '…it was yesterday 💔', 'Occasions that remind you weeks ahead, with gift ideas and a budget.'),
        ('What was that series everyone recommended?', 'No idea. It was in a chat… last month?', 'Shared from any app into one watchlist, waiting for the weekend.')])
    g = next(x for x in GUIDES if x['slug'] == SOLO_GUIDE['slug'])
    return h + hero + f'''
<section style="padding-top:20px"><div class="wrap">{solo_panel()}</div></section>
<section class="tint"><div class="wrap"><div class="sec-head center">{T('Sound familiar?', 'هل يبدو هذا مألوفًا؟', 'span', 'eyebrow')}{N('The conversations you have with yourself.', 'h2')}</div>
<div class="pains">{pains_html}</div></div></section>
<section><div class="wrap split">
  <div class="stage">{screen('watch', 'clean', 'One list per kind', _nov_ar('One list per kind'))}</div>
  <div><div class="grid g2">{cards}</div></div>
</div></section>
{story_previews('solo')}
<section class="tint"><div class="narrow center">
  {T('A real week with OneSpace', 'أسبوع حقيقي مع OneSpace', 'span', 'eyebrow')}
  {N('Set up once. It works quietly in the background.', 'h2')}
  {N('Create your space with your email, share things in from your other apps — and invite someone whenever you’re ready.', 'p', 'lead')}
  <div class="cta-row" style="justify-content:center"><a class="btn btn-primary" href="join.html">{T('Join the Founding 500', 'انضم إلى المؤسسين الـ500')}</a><a class="btn btn-ghost" href="living-together.html">{N('Living with a partner?')}</a></div>
</div></section>
<section><div class="narrow"><a class="card link art-card" href="{g['slug']}" style="flex-direction:row;align-items:center;gap:20px"><div class="cover" style="background:{g['bg']};width:120px;height:120px;flex:none;margin:0">{g['emoji']}</div><div>{T('Guide', 'دليل', 'span', 'eyebrow')}{T(g['title'][0], g['title'][1], 'h3')}{T(g['desc'][0], g['desc'][1], 'p')}</div></a></div></section>
''' + cta_band() + foot()


def persona_page(page, apart):
    if apart:
        h = head(page, 'OneSpace for long-distance couples', 'OneSpace للأزواج عن بُعد',
                 'Two cities, two clocks, one shared life: OneSpace helps long-distance couples with time zones, reunions, trips, letters and daily gestures.',
                 'مدينتان وساعتان وحياة مشتركة واحدة: يساعد OneSpace الأزواج عن بُعد في فروق التوقيت واللقاءات والرحلات والرسائل واللمسات اليومية.')
        hero = page_hero('Living apart', 'متباعدان', 'Far apart, still living one life.', 'بعيدان، ونعيش حياة واحدة.',
                         'Distance is hard enough. OneSpace takes care of the time-zone maths, counts down to the next visit and keeps the small signs of love flowing every day.',
                         'المسافة صعبة بما يكفي. يتولى OneSpace حساب فروق التوقيت، ويعد تنازليًا حتى الزيارة القادمة، ويحافظ على تدفق إشارات الحب الصغيرة كل يوم.')
        points = [('🕰', 'i-blue', 'Two clocks, two weathers', 'ساعتان وطقسان', 'Know if it is a good time to call before you call.', 'اعرف إن كان الوقت مناسبًا للاتصال قبل أن تتصل.'),
                  ('⏳', 'i-violet', 'Countdown to the reunion', 'عد تنازلي للقاء', 'A counter with progress from today to the day you land.', 'عدّاد بتقدّم من اليوم حتى يوم وصولك.'),
                  ('✈️', 'i-coral', 'Trips that plan themselves', 'رحلات منظمة', 'Flights, packing and documents shared by both of you.', 'الطيران والتجهيز والمستندات مشتركة بينكما.'),
                  ('🤍', 'i-gold', 'A little love, any time', 'لمسة حب في أي وقت', 'One tap sends a hug or “thinking of you”, in your own words.', 'نقرة واحدة ترسل حضنًا أو «أفكر فيك» بكلماتك.'),
                  ('💌', 'i-rose', 'Letters for the hard days', 'رسائل للأيام الصعبة', 'Write today, sealed until the day they need it.', 'اكتب اليوم، مغلقة حتى اليوم الذي يحتاجها فيه.'),
                  ('🤳', 'i-teal', 'Daily selfie, side by side', 'سيلفي يومي جنبًا إلى جنب', 'Two photos, one day — a diary of the distance.', 'صورتان ويوم واحد — يوميات المسافة.')]
        scr, theme = scr_today(True), 'teal'
    else:
        h = head(page, 'OneSpace for couples living together', 'OneSpace للأزواج تحت سقف واحد',
                 'Share the mental load at home: OneSpace keeps groceries, chores, bills, decisions, occasions and date nights organised for couples who live together.',
                 'تشاركا العبء الذهني في البيت: ينظّم OneSpace المشتريات والأعمال المنزلية والفواتير والقرارات والمناسبات وليالي المواعيد للأزواج الذين يعيشون معًا.')
        hero = page_hero('Living together', 'تحت سقف واحد', 'Same home. Shared load. More time for each other.', 'بيت واحد. عبء مشترك. وقت أكثر لبعضكما.',
                         'Living together means a hundred small things to remember. OneSpace puts them in one place both of you can see, so nobody has to be the household’s memory.',
                         'العيش معًا يعني مئة شيء صغير يجب تذكّره. يضعها OneSpace في مكان واحد يراه كلاكما، فلا يضطر أحد لأن يكون ذاكرة البيت.')
        points = [('🛒', 'i-green', 'Shared lists', 'قوائم مشتركة', 'Groceries and chores, assigned to one of you or both.', 'المشتريات والأعمال المنزلية، لأحدكما أو لكليكما.'),
                  ('🧾', 'i-gold', 'Bills and renewals', 'الفواتير والتجديدات', 'Repeating reminders so nothing is paid late.', 'تذكيرات متكررة حتى لا يتأخر الدفع.'),
                  ('⚖️', 'i-teal', 'Decide together', 'قررا معًا', 'Compare sofas, schools or holidays and vote.', 'قارنا الأرائك أو المدارس أو العطلات وصوّتا.'),
                  ('🎬', 'i-violet', 'Date nights', 'ليالي المواعيد', 'Plan them, then keep the memory.', 'خططا لها ثم احفظا ذكراها.'),
                  ('🎁', 'i-rose', 'Occasions on time', 'المناسبات في وقتها', 'Gift ideas and budget, private for surprises.', 'أفكار الهدايا والميزانية، خاصة للمفاجآت.'),
                  ('💗', 'i-coral', 'Love without the cliché', 'حب دون مبالغة', 'Gestures written for couples at home — no “miles away” messages.', 'لمسات مكتوبة لمن يعيشان معًا — بلا رسائل «من بعيد».')]
        scr, theme = scr_today(False), 'coral'
    cards = ''.join(trust_card(*p) for p in points)
    other = ('living-together.html', 'Living together instead?', 'تعيشان معًا؟') if apart else ('long-distance.html', 'Living apart instead?', 'متباعدان؟')
    if apart:
        pains_html = (pain('Can you call now?', 'هل يمكنك الاتصال الآن؟', 'In a meeting till 6 — your 9 PM 😕', 'في اجتماع حتى 6 — أي 9 مساءً عندك 😕', 'Two clocks on Today show the best time to talk.', 'ساعتان في «اليوم» تُظهران أفضل وقت للحديث.')
                      + pain('When do we see each other again?', 'متى نلتقي مرة أخرى؟', 'Let me check… March? April?', 'دعيني أتحقق… مارس؟ أبريل؟', 'A reunion counter with progress, on both your phones.', 'عدّاد للقاء بتقدّم، على هاتفيكما.')
                      + pain('I miss you today 🥺', 'أفتقدك اليوم 🥺', '(at 3 a.m., asleep)', '(في الثالثة فجرًا، نائم)', 'A letter you wrote weeks ago, sealed for exactly this kind of day.', 'رسالة كتبتها قبل أسابيع، مغلقة لمثل هذا اليوم تمامًا.'))
        panel, gslug = cities_panel(), 'guide-long-distance-ideas.html'
    else:
        pains_html = (pain('Did you pay the internet?', 'هل دفعت فاتورة الإنترنت؟', 'Wasn’t that your turn?', 'أليس دورك؟', 'Bills with an owner and a monthly repeat.', 'فواتير لها صاحب وتكرار شهري.')
                      + pain('What do we need from the store?', 'ماذا نحتاج من المتجر؟', 'I’ll just buy everything twice', 'سأشتري كل شيء مرتين', 'One live grocery list — ticked as you shop.', 'قائمة مشتريات حيّة — تُعلَّم أثناء التسوق.')
                      + pain('Are we doing anything for my mum’s birthday?', 'هل سنفعل شيئًا لعيد ميلاد أمي؟', 'Wait — that’s this week?!', 'لحظة — هذا الأسبوع؟!', 'Occasions that remind you weeks ahead, with gift ideas and a budget.', 'مناسبات تذكّرك قبلها بأسابيع، مع أفكار هدايا وميزانية.'))
        panel, gslug = home_panel(), 'guide-mental-load.html'
    g = next(x for x in GUIDES if x['slug'] == gslug)
    return h + hero + f'''
<section style="padding-top:20px"><div class="wrap">{panel}</div></section>
<section class="tint"><div class="wrap"><div class="sec-head center">{T('Sound familiar?', 'هل يبدو هذا مألوفًا؟', 'span', 'eyebrow')}{T('The conversations OneSpace quietly handles.', 'المحادثات التي يتولاها OneSpace بهدوء.', 'h2')}</div>
<div class="pains">{pains_html}</div></div></section>
<section><div class="wrap split">
  <div class="stage">{device('trip' if apart else 'together/lists', 'The trip to Istanbul' if apart else 'Shared to-do lists', 'رحلة إسطنبول' if apart else 'قوائم المهام المشتركة', fallback=phone(scr, theme, label='Today screen', label_ar='شاشة اليوم'))}</div>
  <div><div class="grid g2">{cards}</div></div>
</div></section>
{story_previews(apart)}
<section class="tint"><div class="narrow center">
  {T('A real week with OneSpace', 'أسبوع حقيقي مع OneSpace', 'span', 'eyebrow')}
  {T('Set up once. It works quietly in the background.', 'اضبطه مرة واحدة. ويعمل بهدوء في الخلفية.', 'h2')}
  {N('Create your space, invite your partner by email, choose how you live — and Today does the rest.', 'p', 'lead')}
  <div class="cta-row" style="justify-content:center"><a class="btn btn-primary" href="join.html">{T('Join the Founding 500', 'انضم إلى المؤسسين الـ500')}</a><a class="btn btn-ghost" href="{other[0]}">{T(other[1], other[2])}</a></div>
</div></section>
<section><div class="narrow"><a class="card link art-card" href="{g['slug']}" style="flex-direction:row;align-items:center;gap:20px"><div class="cover" style="background:{g['bg']};width:120px;height:120px;flex:none;margin:0">{g['emoji']}</div><div>{T('Guide', 'دليل', 'span', 'eyebrow')}{T(g['title'][0], g['title'][1], 'h3')}{T(g['desc'][0], g['desc'][1], 'p')}</div></a></div></section>
''' + cta_band() + foot()


def page_how():
    """Six-step guided product tour, preserving real app captures and all themes."""
    h = head('how-it-works.html', 'Try OneSpace — guided demo in six steps', 'جرّب OneSpace — عرض تفاعلي في ست خطوات',
             'Experience shared planning, discussion and decisions in a guided six-step OneSpace product demo.',
             'جرّب التخطيط والنقاش والقرارات المشتركة في عرض تفاعلي من ست خطوات داخل OneSpace.')
    steps = [
        ('Notice what matters', 'لاحظ ما يهمكما', 'See what needs your attention in Today.', 'اطّلع على ما يحتاج انتباهك في «اليوم».', 'today', 'clean'),
        ('Save the idea', 'احفظ الفكرة', 'Capture an idea in a shared note so it does not get lost.', 'دوّن الفكرة في ملاحظة مشتركة حتى لا تضيع.', 'demo_note', 'clean'),
        ('Compare options', 'قارن الخيارات', 'Collect links, prices and possibilities in Coordinate.', 'اجمع الروابط والأسعار والخيارات في «نسّق».', 'demo_activity', 'clean'),
        ('Talk it through', 'تناقشا معًا', 'Discuss the options together, right next to their details.', 'ناقشا الخيارات معًا بجانب تفاصيلها مباشرة.', 'demo_chat', 'clean'),
        ('Decide & follow up', 'قرّرا وتابعا', 'Keep your decision, reminders and dates connected.', 'احتفظا بالقرار والتذكيرات والمواعيد مترابطة.', 'demo_decision', 'clean'),
        ('Stay close', 'ابقيا قريبين', 'Finish with a thoughtful gesture — planning is not all you share.', 'اختتما بلفتة لطيفة؛ فالتخطيط ليس كل ما تتشاركانه.', 'demo_connect', 'clean'),
    ]
    tabs = ''.join(
      f'<button class="demo-step" id="demo-tab-{i}" type="button" role="tab" '
      f'data-view="s{i}" aria-controls="demo-panel-{i}" aria-selected="{"true" if i == 0 else "false"}" tabindex="{"0" if i == 0 else "-1"}">'
      f'<span class="demo-step-number">{i+1:02d}</span>{T(en,ar,"span","demo-step-label")}</button>'
      for i,(en,ar,detail,detail_ar,screen_key,theme) in enumerate(steps))
    panels = ''.join(
      f'<div id="demo-panel-{i}" role="tabpanel" aria-labelledby="demo-tab-{i}" '
      f'data-view-of="tour" data-view-name="s{i}" {"hidden" if i else ""}>'
      f'<div class="demo-panel-context">{T(en,ar,"h3")}{T(detail,detail_ar,"p")}</div>'
      f'<div class="demo-panel-device">{device("themes/today_cleanLight",en,ar,themed=True) if i == 0 else (device("themes/love_cleanLight",en,ar,themed=True) if i == 5 else screen(screen_key,theme,en,ar))}</div></div>'
      for i,(en,ar,detail,detail_ar,screen_key,theme) in enumerate(steps))
    faqs = ''.join(f'<details>{T(q,qa,"summary")}{T(answer,answer_ar,"p")}</details>'
      for q,qa,answer,answer_ar in [
        ('Does my partner need the app too?', 'هل يحتاج شريكي إلى التطبيق أيضًا؟', 'Yes. Each of you has an account in the same shared space.', 'نعم. لكل منكما حساب في المساحة المشتركة نفسها.'),
        ('Can we use different languages?', 'هل يمكننا استخدام لغتين مختلفتين؟', 'Yes. Each partner chooses their own app language.', 'نعم. يختار كل شريك لغة التطبيق الخاصة به.'),
        ('Can iPhone users sign up now?', 'هل يستطيع مستخدمو آيفون التسجيل الآن؟', 'Absolutely. Founder registration is open to Android and iPhone users now. The iOS app comes later.', _nov_ar('Absolutely. Founder registration is open to Android and iPhone users now. The iOS app comes later.'))
      ])
    return h + page_hero('Demo', 'العرض',
        'One idea. Two perspectives. One shared plan.', 'فكرة واحدة، ورأيان، وخطة مشتركة.',
        'Follow six real app screens, from spotting something important to planning together and sending a little love. Choose a step or use Previous and Next.',
        'استكشف ست شاشات حقيقية من التطبيق، من ملاحظة ما يهمكما إلى التخطيط معًا وإرسال لمسة حب. اختر أي خطوة أو استخدم السابق والتالي.') + f'''
<section class="demo-wizard-section" data-theme-scope data-demo-wizard>
  <div class="wrap">
    <div class="demo-wizard-shell">
      <div class="demo-wizard-sidebar">
        <span class="eyebrow">{T('GUIDED EXPERIENCE', 'تجربة إرشادية')}</span>
        <h2>{T('Explore at your pace.', 'استكشف على راحتك.')}</h2>
        <div class="demo-progress-row" aria-live="polite">
          <span>{T('Step', 'الخطوة')} <strong data-demo-current>1</strong> {T('of', 'من')} 6</span>
          <span>{T('Your journey', 'رحلتكما')}</span>
        </div>
        <div class="demo-progress-track" role="progressbar" aria-label="Demo progress" aria-valuenow="1" aria-valuemin="1" aria-valuemax="6">
          <span data-demo-progress style="width:16.667%"></span>
        </div>
        <div class="demo-step-grid" role="tablist" aria-label="Demo steps" data-views="tour">{tabs}</div>
        <div class="demo-wizard-actions">
          <button class="btn btn-ghost" type="button" data-demo-prev disabled>{T('← Previous', 'السابق ←')}</button>
          <button class="btn btn-dark" type="button" data-next="tour">{T('Next →', 'التالي ←')}</button>
        </div>
      </div>
      <div class="demo-wizard-stage"><div class="demo-wizard-panels">{panels}</div>
        <aside class="demo-theme-inline">
          <span class="eyebrow">{T('MAKE IT YOURS', 'اجعله على ذوقك')}</span>
          <h3>{T('Pick a theme', 'اختر سمة')}</h3>
          <div class="swatches demo-theme-grid" aria-label="App theme examples">{swatches()}</div>
          <p class="demo-theme-note">{T('The same app, nine looks. Switch any time.', 'التطبيق نفسه بتسع سمات. غيّرها متى شئت.')}</p>
          {device('themes/today_cleanLight','App theme preview','معاينة سمة التطبيق','demo-theme-device',themed=True)}
        </aside>
      </div>
    </div>
  </div>
</section>
<section class="tint"><div class="narrow">{T('Quick questions','أسئلة سريعة','h2')}<div style="height:20px"></div>{faqs}
  <p><a href="faq.html">{T('All questions →','كل الأسئلة ←')}</a></p></div></section>
''' + cta_band() + foot()


TUTORIALS = [
    ('start', '🚀', 'Getting started', 'البدء', [
        ('Create your space and invite your partner', 'أنشئ مساحتكما وادعُ شريكك', [
            ('Sign up with your email and accept the short terms.', 'سجّل ببريدك واقبل الشروط المختصرة.'),
            ('Create your space and give it a name.', 'أنشئ مساحتكما وسمّها.'),
            ('Tap Invite and enter your partner’s email — or share your invite code.', _nov_ar('Tap Invite and enter your partner’s email — or share your invite code.')),
            ('Your partner accepts the invitation in the app. Invitations expire after 48 hours, and a space holds exactly two people.', _nov_ar('Your partner accepts the invitation in the app. Invitations expire after 48 hours, and a space holds exactly two people.'))]),
        ('Use OneSpace on your own', _nov_ar('Use OneSpace on your own'), [
            (x, _nov_ar(x)) for x in ('Sign up with your email and create your space — no partner needed.',
                                      'Share links from other apps, and add reminders, lists, trips and memories as usual.',
                                      'When you’re ready, invite someone from Me. Anything you keep as Only me stays private.')]),
        ('Tell OneSpace how you live', 'أخبر OneSpace كيف تعيشان', [
            ('Tap “Tell OneSpace how you live” in your space.', 'انقر «أخبر OneSpace كيف تعيشان» في مساحتكما.'),
            ('Choose living apart or together. Apart adds both cities’ clocks and weather to Today.', 'اختر متباعدين أو معًا. خيار التباعد يضيف ساعتي المدينتين وطقسهما إلى «اليوم».'),
            ('Built-in gesture messages follow your choice — no “miles away” lines for couples at home.', 'رسائل اللمسات الجاهزة تتبع اختيارك — بلا عبارات «من بعيد» لمن يعيشان معًا.')]),
        ('Choose your language and theme', 'اختر لغتك وسمتك', [
            ('Open Me and pick English or العربية — each of you chooses separately.', 'افتح «أنا» واختر العربية أو English — يختار كل منكما على حدة.'),
            ('Pick one of nine themes and a background you like.', 'اختر واحدة من تسع سمات وخلفية تعجبك.')]),
    ]),
    ('everyday', '☑️', 'Every day', 'كل يوم', [
        ('Add anything in two taps', 'أضف أي شيء بنقرتين', [
            ('Tap Quick add on Today.', 'انقر «إضافة سريعة» في «اليوم».'),
            ('Choose reminder, to-do, event, note, trip, place, letter…', 'اختر تذكيرًا أو مهمة أو موعدًا أو ملاحظة أو رحلة أو مكانًا أو رسالة…'),
            ('Choose who it belongs to — you, your partner or both — and whether it is Shared or Only me.', 'اختر لمن هو — لك أو لشريكك أو لكليكما — وهل هو مشترك أو «أنا فقط».')]),
        ('See OneSpace events in your phone calendar', 'شاهد مواعيد OneSpace في تقويم هاتفك', [
            ('Turn on “Show in my phone calendar” and allow calendar access.', 'فعّل «اعرض في تقويم هاتفي» واسمح بالوصول إلى التقويم.'),
            ('Shared events, trips, occasions and special dates appear in a separate “OneSpace” calendar in Google, Samsung or iPhone calendar.', 'تظهر المواعيد والرحلات والمناسبات والتواريخ الخاصة المشتركة في تقويم منفصل باسم «OneSpace» في تقويم Google أو Samsung أو iPhone.'),
            ('It is one way: change things in OneSpace, and OneSpace never reads your other calendars.', 'الاتجاه واحد: غيّر الأشياء في OneSpace، ولا يقرأ OneSpace تقاويمك الأخرى أبدًا.')]),
        ('Send a little love', 'أرسل لمسة حب', [
            ('Open A little love from Our space or Connect.', 'افتح «لمسة حب» من «مساحتنا» أو «تواصل».'),
            ('Pick a gesture — hug, kiss, proud of you, call me…', 'اختر لمسة — حضن أو قبلة أو فخور بك أو اتصل بي…'),
            ('Keep the built-in message or write your own, then send.', 'أبقِ الرسالة الجاهزة أو اكتب رسالتك ثم أرسل.')]),
    ]),
    ('plan', '🧭', 'Plan together', 'خططا معًا', [
        ('Decide together with an activity', 'قررا معًا بنشاط', [
            ('In Coordinate, create an activity — a sofa, a restaurant, a weekend away.', 'في «نسّق»، أنشئ نشاطًا — أريكة أو مطعمًا أو عطلة.'),
            ('Add options with links and prices; each of you marks what you like.', 'أضف خيارات بروابط وأسعار؛ ويحدد كل منكما ما يعجبه.'),
            ('Talk in the conversation (type @ to mention, or record a voice note), then record the decision.', 'تحدثا في المحادثة (اكتب @ للإشارة أو سجّل رسالة صوتية) ثم سجّلا القرار.'),
            ('Use “Remind us” or add to the calendar — the items stay linked.', 'استخدم «ذكّرنا» أو أضف إلى التقويم — وتبقى العناصر مرتبطة.')]),
        ('Plan a trip', 'خطط لرحلة', [
            ('Create a trip in Coordinate → Trips.', 'أنشئ رحلة في «نسّق» ← «الرحلات».'),
            ('Found a flight? In Google Flights tap Share › OneSpace, or copy the link and paste it.', 'وجدت رحلة طيران؟ في Google Flights انقر مشاركة › OneSpace، أو انسخ الرابط والصقه.'),
            ('Split the packing list and attach travel documents — only the two of you can open them.', 'قسّما قائمة التجهيز وأرفقا مستندات السفر — لا يفتحها سواكما.')]),
        ('Prepare a surprise occasion', 'جهّز مناسبة مفاجئة', [
            ('Create an occasion and set it to Only me.', 'أنشئ مناسبة واجعلها «أنا فقط».'),
            ('Add gift ideas with prices and a budget.', 'أضف أفكار هدايا بأسعار وميزانية.'),
            ('Choose when to start preparing — OneSpace reminds you in time.', 'اختر متى تبدأ التحضير — وسيذكّرك OneSpace في الوقت المناسب.')]),
    ]),
    ('remember', '🔖', 'Remember', 'تذكّر', [
        ('Count down (or up) to a special date', 'عدّ تنازليًا (أو تصاعديًا) لتاريخ خاص', [
            ('Open Counters in Remember and add a date.', 'افتح «العدّادات» في «تذكّر» وأضف تاريخًا.'),
            ('For a past date, see both the time since the day itself and the next anniversary.', 'للتاريخ الماضي، شاهد المدة منذ اليوم نفسه والذكرى القادمة.'),
            ('Use “Link to another counter” to see the time between two moments.', 'استخدم «اربط بعدّاد آخر» لترى المدة بين لحظتين.')]),
        ('Save a place from Google Maps', 'احفظ مكانًا من خرائط Google', [
            ('In Google Maps tap Share › OneSpace (or copy the link into the place).', 'في خرائط Google انقر مشاركة › OneSpace (أو انسخ الرابط إلى المكان).'),
            ('Choose “Been there” or “Bucket list”, add photos, a date and a note.', 'اختر «زرناه» أو «قائمة الأحلام» وأضف صورًا وتاريخًا وملاحظة.'),
            ('Open the map to see all your pins; tick bucket-list places to plan a trip.', 'افتح الخريطة لترى كل الدبابيس؛ واختر أماكن من قائمة الأحلام لتخطط لرحلة.')]),
        ('Make a scrapbook', 'اصنع ألبومًا', [
            ('Pick a template and add memories and photos.', 'اختر قالبًا وأضف ذكريات وصورًا.'),
            ('In a shared scrapbook, both of you can add and edit pages. Use Nudge partner to ask for their part.', _nov_ar('In a shared scrapbook, both of you can add and edit pages. Use Nudge partner to ask for their part.')),
            ('Use “Save or share as PDF” to keep or print it.', 'استخدم «احفظ أو شارك كـ PDF» للاحتفاظ به أو طباعته.')]),
    ]),
    ('privacy', '🔒', 'Privacy & help', 'الخصوصية والمساعدة', [
        ('Keep something private', 'أبقِ شيئًا خاصًا', [
            ('When creating or editing an item, choose Only me instead of Shared.', 'عند إنشاء عنصر أو تعديله، اختر «أنا فقط» بدل «مشترك».'),
            ('Only-me items never show on your partner’s phone.', 'العناصر الخاصة لا تظهر أبدًا على هاتف شريكك.')]),
        ('Download or delete your data', _nov_ar('Download or delete your data'), [
            ('Open Me → Your data and account.', 'افتح «أنا» ← «بياناتك وحسابك».'),
            ('Tap Download my data if you want a copy (photos and files are not included), then tap Delete my account.', _nov_ar('Tap Download my data if you want a copy (photos and files are not included), then tap Delete my account.')),
            ('Nothing is deleted for 7 days, and you can cancel at any time in that period.', _nov_ar('Nothing is deleted for 7 days, and you can cancel at any time in that period.')),
            ('Locked out? Use the <a href="delete-account.html">deletion request form</a>.', 'لا تستطيع الدخول؟ استخدم <a href="delete-account.html">نموذج طلب الحذف</a>.')]),
        ('Get help when you can’t sign in', 'احصل على مساعدة إن لم تستطع الدخول', [
            ('The sign-in screen has Help, Contact us and Report a problem — no account needed.', 'في شاشة الدخول: المساعدة وتواصل معنا والإبلاغ عن مشكلة — دون حساب.'),
            ('Or use the <a href="support.html?topic=signin#contact">website form</a>; we reply by email.', 'أو استخدم <a href="support.html?topic=signin#contact">نموذج الموقع</a>؛ ونرد بالبريد.')]),
    ]),
]


# Additional native-language step-by-step guides stay inside existing accordion groups.
for _index, (_key, _icon, _en, _ar, _guides) in enumerate(TUTORIALS):
    _additions = TUTORIAL_ADDITIONS.get(_key, [])
    TUTORIALS[_index] = (_key, _icon, _en, _ar, _guides + [
        (entry['t'][0], entry['t'][1], [(step[0], step[1]) for step in entry['steps']])
        for entry in _additions])
TUTORIALS.append(('journey', '🎬', JOURNEY_LABEL[0], JOURNEY_LABEL[1], [
    (entry['t'][0], entry['t'][1], [(step[0], step[1]) for step in entry['steps']])
    for entry in JOURNEY_TUTORIAL_ADDITIONS['journey']
]))

TUT_CLIPS = {'Add anything in two taps': 'quickadd', 'Decide together with an activity': 'plan', 'Plan a trip': 'trip',
             'Save a place from Google Maps': 'places', 'Send a little love': 'love', 'Choose your language and theme': 'themes',
             'Count down (or up) to a special date': 'counters'}


def page_tutorials():
    h = head('tutorials.html', 'OneSpace tutorials — step-by-step guides', 'دروس OneSpace — أدلة خطوة بخطوة',
             'Step-by-step OneSpace guides: invite your partner, quick add, phone calendar, activities, trips, surprises, counters, places from Google Maps, scrapbooks and privacy.',
             'أدلة OneSpace خطوة بخطوة: دعوة الشريك والإضافة السريعة وتقويم الهاتف والأنشطة والرحلات والمفاجآت والعدّادات والأماكن من خرائط Google والألبومات والخصوصية.')
    jump = ''.join(f'<a class="chip" href="#{k}">{i} {T(e, a)}</a>' for k, i, e, a, _ in TUTORIALS)
    body = ''
    for k, i, e, a, guides in TUTORIALS:
        items = ''
        for t, tar, steps in guides:
            ol = ''.join(f'<li>{T(x, y)}</li>' for x, y in steps)
            v = clip(TUT_CLIPS[t], t, tar, 'xs') if t in TUT_CLIPS else ''
            body_html = (f'<div style="display:flex;gap:22px;align-items:flex-start;flex-wrap:wrap">{v}<ol style="padding-inline-start:22px;margin:0;flex:1;min-width:220px">{ol}</ol></div>'
                         if v else f'<ol style="padding-inline-start:22px;margin:0">{ol}</ol>')
            items += f'<details data-faq>{T(t, tar, "summary")}<div>{body_html}</div></details>'
        body += f'<h2 class="faq-group" id="{k}">{i} {T(e, a)}</h2><div>{items}</div>'
    sk = K('Search tutorials…', 'ابحث في الدروس…')
    return h + page_hero('Tutorials', 'الدروس', 'Step-by-step guides.', 'أدلة خطوة بخطوة.',
                         'Short, practical how-tos for the things couples do most. Prefer to see it? <a href="how-it-works.html">Try the demo</a>.',
                         'إرشادات قصيرة وعملية لأكثر ما يفعله الأزواج. تفضّل أن تراه؟ <a href="how-it-works.html">جرّب العرض</a>.',
                         extra=f'<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:22px">{jump}</div><div style="max-width:560px;margin-top:18px"><label class="sr" for="faq-search">Search</label><input id="faq-search" class="search" type="search" placeholder="Search tutorials…" data-i18n-attr="placeholder:{sk}"></div>') + f"""
<section style="padding-top:10px"><div class="narrow">{body}<p id="faq-empty" hidden>{T('Nothing matches. <a href="support.html">Ask us</a>.', 'لا شيء مطابق. <a href="support.html">اسألنا</a>.')}</p></div></section>
""" + story_case_cards(['reunion-from-flight-to-memory', 'a-sunday-that-didnt-belong-to-chores', 'sofa-that-both-of-us-chose']) + cta_band() + foot()


AVAILABILITY = [
    ('Available now', 'متاح الآن', 'i-green', ['Android app (closed test on Google Play)', 'Everything on the Features page', 'Use it on your own or as a couple', 'English and Arabic', 'Help without signing in'],
     [_nov_ar('Android app (closed test on Google Play)'), 'كل ما في صفحة المزايا', _nov_ar('Use it on your own or as a couple'), 'العربية والإنجليزية', 'المساعدة دون تسجيل الدخول']),
    ('In testing', 'قيد الاختبار', 'i-gold', ['iPhone app via TestFlight', 'Sharing into OneSpace from iPhone apps'],
     ['تطبيق iPhone عبر TestFlight', 'المشاركة إلى OneSpace من تطبيقات iPhone']),
    ('On the roadmap', 'في الخطة', 'i-violet', ['Founder Member benefits (announced before pricing)', 'Smarter love reminders', 'Pricing — not decided yet'],
     ['مزايا الأعضاء المؤسسين (تُعلن قبل الأسعار)', 'تذكيرات حب أذكى', 'الأسعار — لم تُحدد بعد']),
]


def availability():
    cards = ''.join(f'<div class="card"><div class="ico {c}">{"✅" if c == "i-green" else "🧪" if c == "i-gold" else "🗺"}</div>{T(t, ta, "h3")}<ul class="ticks" style="margin-top:12px">{"".join(f"<li>{T(x, y)}</li>" for x, y in zip(en, ar))}</ul></div>'
                    for t, ta, c, en, ar in AVAILABILITY)
    return f'<section class="tint" id="status"><div class="wrap"><div class="sec-head">{T("Where things stand", "أين وصلنا", "h2")}{T("What you can use today, what is being tested and what is planned.", "ما يمكنك استخدامه اليوم، وما يُختبر، وما هو مخطط له.", "p", "muted")}</div><div class="grid g3">{cards}</div></div></section>'


GUIDES = [
    {'slug': 'guide-long-distance-ideas.html', 'emoji': '🌍', 'bg': 'linear-gradient(135deg,#E6F3F3,#CFE6E8)', 'mins': 6,
     'title': ('15 small ways to feel close in a long-distance relationship', '15 طريقة صغيرة للشعور بالقرب في علاقة عن بُعد'),
     'desc': ('Practical, low-effort rituals that make the distance feel smaller — from time-zone etiquette to letters that open on the right day.', 'عادات عملية وسهلة تجعل المسافة أصغر — من آداب فروق التوقيت إلى رسائل تُفتح في اليوم المناسب.'),
     'intro': ('Distance rarely breaks a relationship in one big moment. It wears it down in small ones: a missed call, a day you couldn’t share, a plan that drifted. The fix is also small — a handful of rituals you can keep up for months. Here are fifteen that couples actually stick to.',
               'نادرًا ما تكسر المسافة العلاقة في لحظة كبيرة. إنها تُتعبها في لحظات صغيرة: مكالمة فائتة، ويوم لم تتشاركاه، وخطة تلاشت. والحل صغير أيضًا — بضع عادات يمكنكما الاستمرار عليها لأشهر. إليكما خمس عشرة عادة يلتزم بها الأزواج فعلًا.'),
     'sections': [
        ('Respect each other’s clock', 'احترما ساعة كلٍّ منكما', [
            ('Know the time there before you call. A quick glance saves a lot of “sorry, did I wake you?”', 'اعرف الوقت هناك قبل أن تتصل. نظرة سريعة توفّر كثيرًا من «آسف، هل أيقظتك؟»'),
            ('Agree on one “golden hour” a day when you are both awake and free — and protect it.', 'اتفقا على «ساعة ذهبية» يوميًا تكونان فيها مستيقظين ومتفرغين — واحمياها.'),
            ('Send messages that don’t need an answer, like “thinking of you”. They land without pressure.', 'أرسل رسائل لا تحتاج ردًا مثل «أفكر فيك». تصل دون ضغط.')]),
        ('Share the boring parts', 'تشاركا التفاصيل العادية', [
            ('Keep one shared list — groceries, errands, gifts. Seeing each other’s ordinary day is surprisingly intimate.', 'احتفظا بقائمة مشتركة واحدة — مشتريات ومشاوير وهدايا. رؤية اليوم العادي للآخر حميمية بشكل مفاجئ.'),
            ('Do a one-minute daily check-in: a mood and one honest line about your day.', 'قوما بتواصل يومي في دقيقة: شعور وسطر صادق عن يومك.'),
            ('Swap a daily selfie. In a month you have a diary of the distance.', 'تبادلا سيلفي يوميًا. بعد شهر ستكون لديكما يوميات المسافة.')]),
        ('Always have the next date', 'ليكن هناك موعد قادم دائمًا', [
            ('Never end a visit without the next one on the calendar, even if it’s tentative.', 'لا تُنهيا زيارة دون أن تكون التالية في التقويم، ولو مبدئيًا.'),
            ('Count it down together. Watching a number shrink is a real comfort on hard days.', 'عُدّا لها تنازليًا معًا. رؤية الرقم يصغر عزاء حقيقي في الأيام الصعبة.'),
            ('Plan the trip together — flights, packing, what you’ll do first. Planning is half the joy.', 'خططا للرحلة معًا — الطيران والتجهيز وأول ما ستفعلانه. التخطيط نصف المتعة.')]),
        ('Make love tangible', 'اجعلا الحب ملموسًا', [
            ('Write a letter that opens on a specific day: their birthday, their exam, the day they land.', 'اكتب رسالة تُفتح في يوم محدد: عيد ميلاده، أو امتحانه، أو يوم وصوله.'),
            ('Keep a bucket list of places you’ll visit together, and add to it after every call.', 'احتفظا بقائمة أحلام للأماكن التي ستزورانها معًا، وأضيفا إليها بعد كل مكالمة.'),
            ('Watch the same film at the same time, then rate it separately and compare.', 'شاهدا الفيلم نفسه في الوقت نفسه، ثم قيّماه كلٌّ وحده وقارنا.')]),
        ('Protect the relationship from logistics', 'احميا العلاقة من الأعباء', [
            ('Move decisions out of chat. Compare options in one place so calls can be about you.', 'أخرجا القرارات من المحادثة. قارنا الخيارات في مكان واحد لتكون المكالمات عنكما.'),
            ('Remember the dates that matter — and the ones that matter only to the two of you.', 'تذكّرا التواريخ المهمة — وتلك التي لا تهم سواكما.'),
            ('Say thank you for the small things. A “proud of you” travels further than you think.', 'قولا شكرًا على الأشياء الصغيرة. «فخور بك» تصل أبعد مما تظن.')]),
     ],
     'how': ('In OneSpace: Today shows both clocks and weathers, counters count down to the reunion, letters stay sealed until their day, and trips keep flights and packing in one place.',
             'في OneSpace: يعرض «اليوم» الساعتين والطقسين، وتعدّ العدّادات حتى اللقاء، وتبقى الرسائل مغلقة حتى يومها، وتجمع الرحلات الطيران والتجهيز في مكان واحد.')},
    {'slug': 'guide-mental-load.html', 'emoji': '🏡', 'bg': 'linear-gradient(135deg,#FDECE6,#F9D7CB)', 'mins': 5,
     'title': ('How to share the mental load at home (without a spreadsheet fight)', 'كيف تتقاسمان العبء الذهني في البيت (دون شجار على جدول)'),
     'desc': ('The invisible work of remembering, planning and noticing — and a simple system to split it fairly.', 'العمل غير المرئي من التذكّر والتخطيط والانتباه — ونظام بسيط لتقسيمه بعدل.'),
     'intro': ('The mental load is not the chores themselves. It is remembering that they exist: noticing the milk is low, knowing the car needs a service, keeping track of whose birthday is next. When one person carries all of it, resentment grows quietly. Here is a calm way to share it.',
               'العبء الذهني ليس الأعمال المنزلية نفسها، بل تذكّر وجودها: ملاحظة أن الحليب أوشك على النفاد، ومعرفة أن السيارة تحتاج صيانة، ومتابعة عيد ميلاد من القادم. حين يحمل شخص واحد كل ذلك، يكبر الاستياء بصمت. إليكما طريقة هادئة لتقاسمه.'),
     'sections': [
        ('Make the invisible visible', 'اجعلا غير المرئي مرئيًا', [
            ('For one week, both of you jot down every “I need to remember…” thought.', 'لمدة أسبوع، يدوّن كل منكما كل فكرة «يجب أن أتذكّر…».'),
            ('Put everything in one shared place, not in two heads and five chats.', 'ضعا كل شيء في مكان مشترك واحد، لا في رأسين وخمس محادثات.'),
            ('Look at the list together without blame. Most couples are surprised.', 'انظرا إلى القائمة معًا دون لوم. يتفاجأ معظم الأزواج.')]),
        ('Own outcomes, not tasks', 'تولَّيا النتائج لا المهام', [
            ('Split by area: “bills are yours, school forms are mine” — including the remembering.', 'قسّما حسب المجال: «الفواتير لك ونماذج المدرسة لي» — بما في ذلك التذكّر.'),
            ('Give every reminder an owner. A reminder for “someone” is a reminder for no one.', 'اجعلا لكل تذكير صاحبًا. التذكير لـ«أحد ما» تذكير لا أحد.'),
            ('Use repeats for anything recurring, so nobody re-remembers the same thing monthly.', 'استخدما التكرار لكل ما يتكرر، حتى لا يتذكر أحد الشيء نفسه كل شهر.')]),
        ('Decide once, together', 'قررا مرة واحدة، معًا', [
            ('Big purchases and plans go in one place with options side by side.', 'المشتريات الكبيرة والخطط في مكان واحد مع الخيارات جنبًا إلى جنب.'),
            ('Each of you marks what you like; talk only about the gap.', 'يحدد كل منكما ما يعجبه؛ وتحدثا فقط عن نقاط الاختلاف.'),
            ('Record the decision and link the reminder that follows from it.', 'سجّلا القرار واربطا التذكير الذي يترتب عليه.')]),
        ('Keep a weekly 10-minute reset', 'خصصا 10 دقائق أسبوعيًا للمراجعة', [
            ('Sunday evening: look at the next seven days together.', 'مساء الأحد: انظرا معًا إلى الأيام السبعة القادمة.'),
            ('Move anything stuck, reassign anything unfair.', 'حرّكا ما تعثّر، وأعيدا توزيع ما ليس عادلًا.'),
            ('End with one fun plan — the relationship is not a to-do list.', 'اختما بخطة ممتعة واحدة — العلاقة ليست قائمة مهام.')]),
     ],
     'how': ('In OneSpace: lists and reminders have an owner and repeats, Today shows what needs each of you, and activities let you compare options and record a decision with its linked reminder.',
             'في OneSpace: للقوائم والتذكيرات صاحب وتكرار، ويعرض «اليوم» ما يحتاجه كل منكما، وتتيح الأنشطة مقارنة الخيارات وتسجيل القرار مع تذكيره المرتبط.')},
    {'slug': 'guide-anniversary-planning.html', 'emoji': '💍', 'bg': 'linear-gradient(135deg,#F0EBFB,#E0D6F6)', 'mins': 5,
     'title': ('Never forget an anniversary again: a gentle planning system', 'لن تنسى ذكرى بعد اليوم: نظام تخطيط لطيف'),
     'desc': ('Which dates to track, how early to start, gift-idea habits and how to keep a surprise a surprise.', 'أي التواريخ تتابع، ومتى تبدأ، وعادات أفكار الهدايا، وكيف تبقى المفاجأة مفاجأة.'),
     'intro': ('Forgetting an important date rarely means you don’t care — it usually means it lived only in your head. A tiny system fixes that for good, and makes the day itself better, because you have time to plan.',
               'نسيان تاريخ مهم نادرًا ما يعني أنك لا تهتم — بل غالبًا أنه كان في رأسك فقط. نظام صغير يحل ذلك نهائيًا، ويجعل اليوم نفسه أجمل لأن لديك وقتًا للتخطيط.'),
     'sections': [
        ('Write down the dates that matter', 'دوّن التواريخ المهمة', [
            ('The obvious ones: birthdays, wedding anniversary, engagement.', 'الواضحة: أعياد الميلاد وذكرى الزواج والخطوبة.'),
            ('The quiet ones: the day you met, your first trip, the day you moved in.', 'الهادئة: يوم التقيتما، وأول رحلة، ويوم انتقلتما للعيش معًا.'),
            ('Track both the date itself and its yearly anniversary — “8 years since” feels different from “in 12 days”.', 'تابع التاريخ نفسه وذكراه السنوية — «8 سنوات مضت» تختلف عن «بعد 12 يومًا».')]),
        ('Start earlier than you think', 'ابدأ أبكر مما تظن', [
            ('Set a “start preparing” reminder three weeks ahead for big dates, one week for small ones.', 'اضبط تذكير «ابدأ التحضير» قبل ثلاثة أسابيع للتواريخ الكبيرة، وأسبوع للصغيرة.'),
            ('Book anything that sells out — restaurants, flights, hotels — first.', 'احجز أولًا ما ينفد — المطاعم والطيران والفنادق.'),
            ('Set a budget so the day is joyful, not stressful.', 'حدد ميزانية ليكون اليوم مبهجًا لا مرهقًا.')]),
        ('Keep a running gift-idea list', 'احتفظ بقائمة أفكار هدايا دائمة', [
            ('When your partner mentions something they like, save it that minute.', 'حين يذكر شريكك شيئًا يحبه، احفظه في الدقيقة نفسها.'),
            ('Note price and how sure you are; mark it bought when it is.', 'دوّن السعر ومدى تأكدك؛ وعلّمه «تم الشراء» عند شرائه.'),
            ('Keep the list private — some things are better as surprises.', 'اجعل القائمة خاصة — بعض الأشياء أجمل كمفاجآت.')]),
        ('Turn the day into a memory', 'حوّل اليوم إلى ذكرى', [
            ('Write a letter in advance that opens that morning.', 'اكتب رسالة مسبقًا تُفتح صباح ذلك اليوم.'),
            ('Take one photo of both of you, every year, in the same pose.', 'التقطا صورة واحدة لكما كل عام بالوضعية نفسها.'),
            ('Save it to a scrapbook — in ten years you’ll be glad you did.', 'احفظاها في ألبوم — بعد عشر سنوات ستكونان ممتنين لذلك.')]),
     ],
     'how': ('In OneSpace: counters show the day itself and its next anniversary, occasions hold gift ideas, a budget and an “Only me” option, and letters can be sealed until the morning of.',
             'في OneSpace: تعرض العدّادات اليوم نفسه وذكراه القادمة، وتضم المناسبات أفكار الهدايا والميزانية وخيار «أنا فقط»، ويمكن إغلاق الرسائل حتى صباح اليوم.')},
]


# Nine optional new reading resources: keep the guide hub concise by hiding
# the additional cards until the visitor explicitly asks to explore them.
GUIDES.insert(2, {'slug': SOLO_GUIDE['slug'], 'emoji': SOLO_GUIDE['emoji'], 'bg': SOLO_GUIDE['bg'], 'mins': SOLO_GUIDE['mins'],
                  'title': tuple(SOLO_GUIDE['title'][:2]), 'desc': tuple(SOLO_GUIDE['desc'][:2]),
                  'intro': tuple(SOLO_GUIDE['intro'][:2]), 'how': tuple(SOLO_GUIDE['how'][:2]),
                  'sections': [(h[0], h[1], [(t[0], t[1]) for t in tips]) for h, tips in SOLO_GUIDE['sections']]})


def _from_localized_guide(entry):
    return {'slug': entry['slug'], 'emoji': entry['emoji'], 'bg': entry['bg'],
            'mins': entry['mins'], 'title': entry['title'][:2],
            'desc': entry['desc'][:2], 'intro': entry['intro'][:2],
            'how': entry['how'][:2],
            'sections': [(heading[0], heading[1],
                         [(tip[0], tip[1]) for tip in tips])
                         for heading, tips in entry['sections']]}
GUIDES.extend([_from_localized_guide(g) for g in GUIDE_ADDITIONS_1 + GUIDE_ADDITIONS_2])


def guide_cards(guides=None):
    return ''.join(f"""<a class="card link art-card reveal" href="{g['slug']}"><div class="cover" style="background:{g['bg']}">{g['emoji']}</div>
  {T(g['title'][0], g['title'][1], 'h3')}{T(g['desc'][0], g['desc'][1], 'p')}<span class="muted" style="font-size:13px">{g['mins']} {T('min read', 'دقائق قراءة')}</span></a>""" for g in (GUIDES if guides is None else guides))


def page_guides():
    h = head('guides.html', 'Relationship guides for couples — OneSpace', 'أدلة العلاقات للأزواج — OneSpace',
             'Practical guides for couples: long-distance ideas, sharing the mental load at home, and never forgetting an anniversary.',
             'أدلة عملية للأزواج: أفكار للعلاقات عن بُعد، وتقاسم العبء الذهني في البيت، وعدم نسيان الذكرى أبدًا.')
    return (h + page_hero('Guides', 'الأدلة', 'Small ideas for a shared life.', 'أفكار صغيرة لحياة مشتركة.',
                         'Practical, kind and short. Written for real life — on your own, sharing a sofa or a time difference.',
                         _nov_ar('Practical, kind and short. Written for real life — on your own, sharing a sofa or a time difference.')) + \
        f'<section style="padding-top:20px"><div class="wrap"><div class="grid g3">{guide_cards(GUIDES[:3])}</div>'
        + '<details class="journey-show-more guide-show-more"><summary>'
        + N('Explore 10 more practical guides')
        + '</summary><div class="grid g3" style="margin-top:22px">'
        + guide_cards(GUIDES[3:]) + '</div></details></div></section>'
        + cta_band() + foot())


def guide_page(g):
    t_en, t_ar = g['title']
    h = head(g['slug'], t_en + ' — OneSpace', t_ar + ' — OneSpace', g['desc'][0], g['desc'][1])
    body = ''
    for st, st_ar, tips in g['sections'] + [(*heading, tips) for heading, tips in GUIDE_MORE.get(g['slug'], [])]:
        body += f'{T(st, st_ar, "h2")}<ol>{"".join(f"<li>{T(x, y)}</li>" for x, y in tips)}</ol>'
    ld = {'@context': 'https://schema.org', '@type': 'Article', 'headline': t_en, 'description': g['desc'][0], 'inLanguage': 'en',
          'publisher': {'@type': 'Organization', 'name': 'OneSpace'}, 'datePublished': '2026-11-16', 'mainEntityOfPage': BASE + g['slug']}
    others = ''.join(f'<li><a href="{o["slug"]}">{T(o["title"][0], o["title"][1])}</a></li>' for o in [other for other in GUIDES if other is not g][:4])
    return h + f"""<section class="page-hero"><div class="narrow">
  <div class="crumbs"><a href="./">{T('Home', 'الرئيسية')}</a> › <a href="guides.html">{T('Guides', 'الأدلة')}</a></div>
  <div style="font-size:56px;margin-top:16px">{g['emoji']}</div>{T(t_en, t_ar, 'h1')}
  <p class="muted">{g['mins']} {T('min read', 'دقائق قراءة')} · OneSpace</p></div></section>
<section style="padding-top:10px"><div class="narrow article">
  {T(g['intro'][0], g['intro'][1], 'p', 'lead')}{body}
  <div class="tip">💡 {T(g['how'][0], g['how'][1])}</div>
  {T('More guides', 'أدلة أخرى', 'h2')}<ul>{others}</ul>
</div></section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
""" + cta_band() + foot()


_NEW_22 = ['Use OneSpace on your own, and invite someone when you’re ready.',
           'Today shows your day, your partner’s and what you do together side by side — with work days, days off and public holidays for your country.',
           'Events say who’s taking part and can have their own time zone.',
           'A daily selfie calendar, scrapbooks you can both edit, and Nudge partner.',
           'Invite your partner by email; invitations expire after 48 hours.']
WHATS_NEW = [
    ('November 2026', 'نوفمبر 2026', 'Made for you — on your own or together', _nov_ar('Made for you — on your own or together'),
     _NEW_22, [_nov_ar(x) for x in _NEW_22]),
    ('November 2026', 'نوفمبر 2026', 'The Founding 500 is open', 'باب المؤسسين الـ500 مفتوح',
     ['Join with your email and confirm it to become a Founder Member.', 'Invite your partner with your own link — they become a Founder Member too.', 'The reunion counter is right in every “living apart” setting; theme previews fit smaller phones.'],
     [_nov_ar('Join with your email and confirm it to become a Founder Member.'), _nov_ar('Invite your partner with your own link — they become a Founder Member too.'), 'عدّاد اللقاء صحيح في كل إعدادات «متباعدان»، ومعاينات السمات تناسب الهواتف الأصغر.']),
    ('November 2026', 'نوفمبر 2026', 'Places, counters and a map', 'الأماكن والعدّادات والخريطة',
     ['Our places: been there and bucket list, pinned on a map, shared from Google Maps.', 'Counters that tell the date itself from its anniversary, with progress bars and a Today line.', 'Plan a trip from the bucket-list places you pick.'],
     ['أماكننا: ما زرتماه وقائمة الأحلام على خريطة، ومشاركة من خرائط Google.', 'عدّادات تفرّق بين التاريخ نفسه وذكراه، مع أشرطة تقدّم وخط اليوم.', 'خطط لرحلة من أماكن قائمة الأحلام التي تختارها.']),
    ('November 2026', 'نوفمبر 2026', 'Clearer notifications and smarter gestures', 'إشعارات أوضح ولمسات أذكى',
     ['Notifications now say who did what, grouped by day.', 'Love gestures in a logical order, and no “far away” messages for couples who live together.', '@mentions built into the conversation field.'],
     ['الإشعارات تقول الآن من فعل ماذا، مجمعة حسب اليوم.', 'لمسات الحب بترتيب منطقي، ولا رسائل «من بعيد» لمن يعيشان معًا.', 'الإشارات (@) مدمجة في حقل المحادثة.']),
    ('November 2026', 'نوفمبر 2026', 'Sign-up, help and calendars', 'التسجيل والمساعدة والتقويم',
     ['Help, contact and “report a problem” from the sign-in screen and this website — no account needed.', 'Send OneSpace events to your phone calendar.', 'Arabic translation completed across Today, trips and check-ins.'],
     ['المساعدة والتواصل والإبلاغ عن مشكلة من شاشة الدخول ومن هذا الموقع — دون حساب.', 'أرسل مواعيد OneSpace إلى تقويم هاتفك.', 'اكتملت الترجمة العربية في «اليوم» والرحلات والتواصل اليومي.']),
]


def page_whats_new():
    h = head('whats-new.html', "What's new in OneSpace", 'الجديد في OneSpace',
             'The latest OneSpace updates: places and a map, smarter counters, clearer notifications, Arabic improvements and more.',
             'أحدث تحديثات OneSpace: الأماكن والخريطة وعدّادات أذكى وإشعارات أوضح وتحسينات العربية وغيرها.')
    items = ''.join(f'''<article class="reveal">{T(w, war, 'div', 'when')}{T(t, tar, 'h3')}<ul class="ticks">{''.join(f"<li>{T(e, a)}</li>" for e, a in zip(en, ar))}</ul></article>'''
                    for w, war, t, tar, en, ar in WHATS_NEW)
    return h + page_hero("What's new", 'الجديد', 'Better every week, shaped by real couples.', 'أفضل كل أسبوع، بآراء أزواج حقيقيين.',
                         'OneSpace is in an early test. Here is what changed recently — and how to tell us what to build next.',
                         'OneSpace في تجربة مبكرة. إليك ما تغيّر مؤخرًا — وكيف تخبرنا بما نبنيه بعد ذلك.') + f'''
<section style="padding-top:30px"><div class="narrow"><div class="timeline">{items}</div>
<div class="panel" style="margin-top:50px">{T('Have an idea?', 'لديك فكرة؟', 'h3')}{T('Many of these features came from testers. Tell us what would help the two of you.', 'جاءت كثير من هذه المزايا من المختبرين. أخبرنا بما يساعدكما.', 'p', 'muted')}
<div class="cta-row" style="margin-top:14px"><a class="btn btn-primary" href="support.html?topic=idea">{T('Suggest a feature', 'اقترح ميزة')}</a><a class="btn btn-ghost" href="join.html">{T('Join the test', 'انضم للتجربة')}</a></div></div>
</div></section>''' + availability() + foot()


FAQ = [
    ('Getting started', 'البدء', [
        ('What is OneSpace?', 'ما هو OneSpace؟', 'A private app for your everyday life — on your own or with your partner: a calendar, lists, reminders, trips, occasions, places, counters and memories in one place, plus letters and little gestures for couples.', _nov_ar('A private app for your everyday life — on your own or with your partner: a calendar, lists, reminders, trips, occasions, places, counters and memories in one place, plus letters and little gestures for couples.')),
        ('Can I use OneSpace without a partner?', _nov_ar('Can I use OneSpace without a partner?'), 'Yes. Your account has its own private space, whether or not you have a partner. Use lists, reminders, trips, notes and memories on your own. If you later invite someone, your private records stay yours; only content shared in the current relationship is visible to that partner.', _nov_ar('Yes. Your account has its own private space, whether or not you have a partner. Use lists, reminders, trips, notes and memories on your own. If you later invite someone, your private records stay yours; only content shared in the current relationship is visible to that partner.')),
        ('How do I get it?', 'كيف أحصل عليه؟', 'OneSpace is in a closed test on Android through Google Play. <a href="join.html">Join the Founding 500</a>, confirm your email, and we will invite people in small groups. iPhone is coming next through TestFlight.', _nov_ar('OneSpace is in a closed test on Android through Google Play.') + ' <a href="join.html">انضم إلى المؤسسين الـ500</a>' + _nov_ar(', confirm your email, and we will invite people in small groups. iPhone is coming next through TestFlight.')),
        ('How do I invite my partner?', 'كيف أدعو شريكي؟', 'From Today, tap Invite my partner and enter their email. Only the account with that verified email can join. Your partner can open the invitation in OneSpace or use its code or QR code, then accept or decline. The invitation expires after 48 hours.', _nov_ar('From Today, tap Invite my partner and enter their email. Only the account with that verified email can join. Your partner can open the invitation in OneSpace or use its code or QR code, then accept or decline. The invitation expires after 48 hours.')),
        ('Is it free?', 'هل هو مجاني؟', 'Yes, during the early test. If that ever changes, we will tell you clearly and in advance.', 'نعم، خلال التجربة المبكرة. وإذا تغيّر ذلك سنخبرك بوضوح ومسبقًا.'),
    ]),
    ('Founder Members', 'الأعضاء المؤسسون', [
        ('What is the Founding 500?', 'ما هم المؤسسون الـ500؟', 'The first 500 people who join and confirm their email — on their own or as a couple — become Founder Members. You get the app first, a direct line to the team and a say in what we build.', _nov_ar('The first 500 people who join and confirm their email — on their own or as a couple — become Founder Members. You get the app first, a direct line to the team and a say in what we build.')),
        ('Do we both need to sign up?', 'هل يجب أن نسجّل كلانا؟', 'No. You can register on your own. If you want to invite your partner to the Founder program, send them the link from your confirmation page. They must register and confirm their own email; Founder status follows available places and the order of confirmation.', _nov_ar('No. You can register on your own. If you want to invite your partner to the Founder program, send them the link from your confirmation page. They must register and confirm their own email; Founder status follows available places and the order of confirmation.')),
        ('When does my Founder membership start?', _nov_ar('When does my Founder membership start?'), 'As soon as you click the link in the confirmation email from founders@onespace.live. Places go in the order emails are confirmed.', _nov_ar('As soon as you click the link in the confirmation email from founders@onespace.live. Places go in the order emails are confirmed.')),
        ('The confirmation email didn’t arrive.', 'لم تصل رسالة التأكيد.', 'Check spam or Promotions for founders@onespace.live. Still nothing after 10 minutes? Sign up again with the same email and we will send a fresh link.', 'تفقّد البريد العشوائي أو العروض بحثًا عن founders@onespace.live. لم يصل شيء بعد 10 دقائق؟ سجّل مجددًا بالبريد نفسه وسنرسل رابطًا جديدًا.'),
        ('What do Founder Members get?', 'ماذا يحصل الأعضاء المؤسسون؟', 'Early access, a direct line to the team and a say in what we build. Founder benefits will be announced before any pricing is introduced.', 'وصول مبكر، وخط مباشر مع الفريق، ورأي فيما نبنيه. وسنعلن مزايا المؤسسين قبل تقديم أي أسعار.'),
        ('Can I stop the emails?', 'هل يمكنني إيقاف الرسائل؟', 'Yes — every email has an Unsubscribe link, and you stay a Founder Member.', _nov_ar('Yes — every email has an Unsubscribe link, and you stay a Founder Member.')),
    ]),
    ('Using OneSpace', 'استخدام OneSpace', [
        ('Does it work for couples who live together?', 'هل يناسب الأزواج الذين يعيشون معًا؟', 'Yes. Choose “Together” and Today focuses on your home and shared plans. Distance-only messages are never sent.', 'نعم. اختر «معًا» فيركز «اليوم» على البيت والخطط المشتركة. ولا تُرسل رسائل البعد أبدًا.'),
        ('Can I keep something from my partner?', 'هل يمكنني إخفاء شيء عن شريكي؟', 'Yes — mark items “Only me”. They stay private to you, always — for example a surprise gift or occasion.', _nov_ar('Yes — mark items “Only me”. They stay private to you, always — for example a surprise gift or occasion.')),
        ('Does it sync with my phone calendar?', 'هل يتزامن مع تقويم هاتفي؟', 'You can send OneSpace events one way to your phone calendar (Google, Samsung or iPhone calendar). Changes in your phone calendar do not come back.', 'يمكنك إرسال مواعيد OneSpace في اتجاه واحد إلى تقويم هاتفك (Google أو Samsung أو iPhone). التغييرات في تقويم هاتفك لا تعود إلى التطبيق.'),
        ('Can I write my own love notes?', 'هل يمكنني كتابة رسائل الحب بنفسي؟', 'Yes. Every gesture can carry your own words, and you can set a private reminder to send a little love.', 'نعم. كل لمسة يمكن أن تحمل كلماتك، ويمكنك ضبط تذكير خاص لإرسال لمسة حب.'),
        ('Which languages are supported?', 'ما اللغات المدعومة؟', 'English and Arabic (right to left). Each of you picks your own.', 'الإنجليزية والعربية (من اليمين لليسار). يختار كل منكما لغته.'),
    ]),
    ('Privacy & account', 'الخصوصية والحساب', [
        ('Who can see my space?', _nov_ar('Who can see my space?'), 'Only you — and your partner, for the things you share. Photos and documents are stored privately and opened with short-lived links.', _nov_ar('Only you — and your partner, for the things you share. Photos and documents are stored privately and opened with short-lived links.')),
        ('Do you sell data or show ads?', 'هل تبيعون البيانات أو تعرضون إعلانات؟', 'No, never.', 'لا، أبدًا.'),
        ('How do I download or delete my data?', _nov_ar('How do I download or delete my data?'), 'In the app: Me → Your data and account. Account deletion has a 7-day period to change your mind. Locked out? Use <a href="delete-account.html">this form</a>.', _nov_ar('In the app: Me → Your data and account. Account deletion has a 7-day period to change your mind. Locked out? Use') + ' <a href="delete-account.html">هذا النموذج</a>.'),
        ('What happens if we break up?', 'ماذا يحدث إذا انفصلنا؟', 'In Me → Profile → My Space, the owner can remove the partner or delete the shared space, and the invited partner can leave it. After explicit confirmation, all shared content and attachments are permanently deleted for both people. Each retains their own private content. Nothing from that relationship is carried to a future shared space.', _nov_ar('In Me → Profile → My Space, the owner can remove the partner or delete the shared space, and the invited partner can leave it. After explicit confirmation, all shared content and attachments are permanently deleted for both people. Each retains their own private content. Nothing from that relationship is carried to a future shared space.')),
    ]),
    ('Help', 'المساعدة', [
        ('I can’t sign in.', 'لا أستطيع تسجيل الدخول.', 'Use “Forgot password” on the sign-in screen, or <a href="support.html?topic=signin#contact">contact us</a> — no account needed.', 'استخدم «نسيت كلمة المرور» في شاشة الدخول، أو <a href="support.html?topic=signin#contact">تواصل معنا</a> — دون حساب.'),
        ('How do I report a bug?', 'كيف أبلغ عن خلل؟', 'In the app: Me → Help and support → Report a technical issue (it can add a screenshot and the details we need). Or use the <a href="support.html?topic=issue#contact">website form</a>.', 'في التطبيق: «أنا» ← «المساعدة والدعم» ← «الإبلاغ عن مشكلة تقنية» (يمكنه إرفاق لقطة شاشة والتفاصيل التي نحتاجها). أو استخدم <a href="support.html?topic=issue#contact">نموذج الموقع</a>.'),
        ('Is there an iPhone app?', 'هل يوجد تطبيق iPhone؟', 'It is being prepared for TestFlight. Join early access and choose iPhone — we will invite you when it is ready.', 'يجري تجهيزه عبر TestFlight. انضم مبكرًا واختر iPhone — وسندعوك عند جاهزيته.'),
    ]),
]


def page_faq():
    from bs4 import BeautifulSoup
    h = head('faq.html', 'OneSpace FAQ', 'الأسئلة الشائعة — OneSpace',
             'Answers about OneSpace: getting started, inviting your partner, privacy, calendar sync, languages, export, deletion and help.',
             'إجابات عن OneSpace: البدء ودعوة الشريك والخصوصية ومزامنة التقويم واللغات والتصدير والحذف والمساعدة.')
    body = ''
    for g, gar, qs in FAQ:
        qs = qs + [(*q, *a) for q, a in FAQ_MORE.get(g, [])]
        items = ''.join(f'<details data-faq>{T(q, qa, "summary")}{T(a, aa, "div")}</details>' for q, qa, a, aa in qs)
        body += f'{T(g, gar, "h2", "faq-group")}<div>{items}</div>'
    sk = K('Search questions…', 'ابحث في الأسئلة…')
    jsonld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': BeautifulSoup(a, 'html.parser').get_text(' ', strip=True)}} for g, _, qs in FAQ for q, _, a, _ in (qs + [(*q0, *a0) for q0, a0 in FAQ_MORE.get(g, [])])]}
    return h + page_hero('FAQ', 'الأسئلة الشائعة', 'Questions, answered.', 'أسئلة وأجوبتها.', 'Can’t find it? <a href="support.html">Contact us</a> — even without an account.',
                         'لم تجد ما تبحث عنه؟ <a href="support.html">تواصل معنا</a> — حتى دون حساب.',
                         extra=f'<div style="max-width:560px;margin-top:24px"><label class="sr" for="faq-search">Search</label><input id="faq-search" class="search" type="search" placeholder="Search questions…" data-i18n-attr="placeholder:{sk}"></div>') + f'''
<section style="padding-top:10px"><div class="narrow">{body}<p id="faq-empty" hidden>{T('No matching questions. Try another word or <a href="support.html">ask us</a>.', 'لا توجد أسئلة مطابقة. جرّب كلمة أخرى أو <a href="support.html">اسألنا</a>.')}</p></div></section>
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
''' + cta_band() + foot()


def radio(name, opts):
    return '<div class="radio-cards">' + ''.join(f'<label><input type="radio" name="{name}" value="{v}"{" checked" if i == 0 else ""}> {T(e, a)}</label>' for i, (v, e, a) in enumerate(opts)) + '</div>'


def share_buttons():
    return f'''<div class="cta-row" style="justify-content:center">
  <a class="btn btn-primary" data-share="whatsapp" href="https://wa.me/" target="_blank" rel="noopener">{T('Send on WhatsApp', 'أرسل عبر واتساب')}</a>
  <a class="btn btn-ghost" data-share="email" href="mailto:">{T('Send by email', 'أرسل بالبريد')}</a>
  <a class="btn btn-ghost" data-share="native" href="#">{T('Copy / share link', 'انسخ / شارك الرابط')}</a></div>'''


def page_join():
    h = head('join.html', 'Join the Founding 500 — OneSpace early access', 'انضم إلى المؤسسين الـ500 — OneSpace',
             'Join the OneSpace early test for free. Tell us a little about yourself and we will send you an invite.',
             _nov_ar('Join the OneSpace early test for free. Tell us a little about yourself and we will send you an invite.'))
    ek = K('you@example.com', 'you@example.com')
    return h + f'''
<section class="page-hero"><div class="wrap split" style="align-items:start">
  <div>
    <div class="crumbs"><a href="./">{T('Home', 'الرئيسية')}</a> › {T('Join', 'انضم')}</div>
    {T('Join the Founding 500.', 'انضم إلى المؤسسين الـ500.', 'h1')}
    {N('Founder registration is open to Android and iPhone NOW — there is no need to wait for iOS to launch. The first 500 people to join — on their own or as a couple — become Founder Members. Early access is free, and benefits will be announced before pricing.', 'p', 'lead')}
    <ul class="ticks">
      <li>{N('<b>1. Tell us about yourself</b> — 30 seconds.')}</li>
      <li>{N('<b>2. Confirm your email</b> — that is when you become a Founder Member.')}</li>
      <li>{N('<b>3. Invite your partner</b> if you have one — they become a Founder Member too.')}</li>
      <li>{T('<b>4. Get the invitation when your app is ready</b> — Android first, iPhone later. Registration is open for both today.', '<b>4. استلما الدعوة عند جاهزية التطبيق</b> — أندرويد أولًا وآيفون لاحقًا. التسجيل مفتوح لكليهما اليوم.')}</li>
    </ul>
    <div class="note-box" style="margin-top:24px">{T('We only use your email for your Founder membership and the launch updates you agree to. No marketing lists, no sharing. Questions: <a href="mailto:founders@onespace.live">founders@onespace.live</a> · <a href="privacy.html">Privacy</a>', 'نستخدم بريدك فقط لعضويتك كمؤسس وتحديثات الإطلاق التي توافق عليها. لا قوائم تسويق ولا مشاركة. للأسئلة: <a href="mailto:founders@onespace.live">founders@onespace.live</a> · <a href="privacy.html">الخصوصية</a>')}</div>
  </div>
  {founding_form('j', True)}
</div></section>
<section class="tint"><div class="wrap"><div class="grid g3">
  {trust_card('🆓', 'i-green', 'Free during the test', 'مجاني خلال التجربة', 'No card, no trial timer.', 'بلا بطاقة ولا مدة تجريبية.')}
  {trust_card('🔒', 'i-teal', 'Private by design', _nov_ar('Private by design'), 'Only you — and the partner you invite — can see your space.', _nov_ar('Only you — and the partner you invite — can see your space.'))}
  {trust_card('💬', 'i-coral', 'A direct line to us', 'خط مباشر معنا', 'Testers shape what we build next.', 'المختبرون يحددون ما نبنيه بعد ذلك.')}
</div></div></section>
''' + foot()


def page_support():
    h = head('support.html', 'OneSpace support & contact', 'الدعم والتواصل — OneSpace',
             'Contact OneSpace, report a problem or get help signing in — no account needed.',
             'تواصل مع OneSpace أو أبلغ عن مشكلة أو احصل على مساعدة في الدخول — دون حساب.')
    ek = K('you@example.com', 'you@example.com')
    return h + page_hero('Support', 'الدعم', 'How can we help?', 'كيف نساعدك؟', 'Messages from this page go to the same inbox as the app. No account needed. Prefer email? Write to <a href="mailto:support@onespace.live">support@onespace.live</a>.', 'الرسائل من هذه الصفحة تصل إلى صندوق الوارد نفسه في التطبيق. دون حساب. تفضّل البريد؟ راسلنا على <a href="mailto:support@onespace.live">support@onespace.live</a>.') + f'''
<section style="padding-top:20px"><div class="wrap">
  <div class="grid g3">
    <a class="card link" href="faq.html"><div class="ico i-blue">❓</div>{T('Read the FAQ', 'اقرأ الأسئلة الشائعة', 'h3')}{T('Most answers are there.', 'معظم الإجابات هناك.', 'p')}</a>
    <a class="card link" id="signin" href="?topic=signin#contact"><div class="ico i-gold">🔑</div>{T('Can’t sign in', 'لا أستطيع الدخول', 'h3')}{T('Try “Forgot password” in the app first. Still stuck? Write to us.', 'جرّب «نسيت كلمة المرور» أولًا. ما زلت عالقًا؟ راسلنا.', 'p')}</a>
    <a class="card link" href="delete-account.html"><div class="ico i-rose">🗑</div>{T('Delete my account', 'حذف حسابي', 'h3')}{T('From the app or with a request here.', 'من التطبيق أو بطلب من هنا.', 'p')}</a>
  </div>
</div></section>
<section id="contact" class="tint"><div class="narrow"><div class="panel">
  <form data-form="support" novalidate>
    {T('Send us a message', 'أرسل لنا رسالة', 'h2', '', 'style="font-size:28px"')}
    <label for="s-topic">{T('Topic', 'الموضوع')}</label>
    <select id="s-topic" name="topic">{T('A question', 'سؤال', 'option', attrs='value="question"')}{T('Report a problem', 'الإبلاغ عن مشكلة', 'option', attrs='value="issue"')}{T('I can’t sign in', 'لا أستطيع الدخول', 'option', attrs='value="signin"')}{T('Suggest a feature', 'اقتراح ميزة', 'option', attrs='value="idea"')}{T('Make a complaint', 'تقديم شكوى', 'option', attrs='value="complaint"')}{T('Something else', 'شيء آخر', 'option', attrs='value="other"')}</select>
    <div class="f2"><div><label for="s-name">{T('Name', 'الاسم')}</label><input id="s-name" name="name" maxlength="60" autocomplete="name"></div>
    <div><label for="s-email">{T('Email for our reply *', 'بريدك لنرد عليك *')}</label><input id="s-email" name="email" type="email" required autocomplete="email" placeholder="you@example.com" data-i18n-attr="placeholder:{ek}"></div></div>
    <label for="s-subject">{T('Subject', 'العنوان')}</label><input id="s-subject" name="subject" maxlength="120">
    <label for="s-msg">{T('Message *', 'الرسالة *')}</label><textarea id="s-msg" name="message" required maxlength="4000"></textarea>
    <input class="hp" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">
    {T('For a problem, tell us your phone model and what you tapped just before it happened. Please don’t send passwords.', 'للمشكلات، أخبرنا بطراز هاتفك وما نقرت عليه قبل حدوثها. من فضلك لا ترسل كلمات المرور.', 'p', 'muted', 'style="font-size:14px;margin:12px 0 0"')}
    <div class="cta-row" style="margin-top:16px"><button class="btn btn-primary" type="submit">{T('Send message', 'أرسل الرسالة')}</button></div>
    <p class="status" role="status" aria-live="polite"></p>
  </form>
</div></div></section>
''' + foot()


def page_delete():
    h = head('delete-account.html', 'Delete your OneSpace account', 'حذف حساب OneSpace',
             'How to delete your OneSpace account and data, in the app or with a request if you cannot sign in.',
             'كيف تحذف حسابك وبياناتك في OneSpace، من التطبيق أو بطلب إن لم تستطع الدخول.')
    ek = K('you@example.com', 'you@example.com')
    return h + page_hero('Delete your account', 'حذف حسابك', 'Delete your account and data', 'احذف حسابك وبياناتك', 'You are always in control. Here is exactly what happens.', 'أنت المتحكم دائمًا. إليك ما يحدث بالضبط.') + f'''
<section style="padding-top:20px"><div class="narrow legal">
  {T('In the app (fastest)', 'من التطبيق (الأسرع)', 'h2')}
  <ol><li>{T('Open <b>Me → Your data and account</b>.', 'افتح <b>أنا ← بياناتك وحسابك</b>.')}</li><li>{N('Optional: <b>Download my data</b> first (photos and files are not included).')}</li><li>{T('Tap <b>Delete my account</b> and confirm.', 'انقر <b>حذف حسابي</b> وأكّد.')}</li></ol>
  {T('What is deleted', 'ما الذي يُحذف', 'h2')}
  {N('Nothing is deleted for 7 days — you can cancel at any time in that period and everything stays as it was. After 7 days, your account and your Only me items are permanently deleted, together with everything you shared with your current partner. Your partner keeps their own Only me items.', 'p')}
  {T('Can’t sign in?', 'لا تستطيع الدخول؟', 'h2', '', 'id="request"')}
  {T('Send a request below — or email <a href="mailto:privacy@onespace.live">privacy@onespace.live</a> — from the email on your account. We will confirm it is you, then delete the account and reply.', 'أرسل طلبًا من الأسفل — أو راسل <a href="mailto:privacy@onespace.live">privacy@onespace.live</a> — من البريد المسجل في حسابك. سنتأكد من هويتك ثم نحذف الحساب ونرد عليك.', 'p')}
  <div class="panel"><form data-form="account" novalidate>
    <label for="d-email">{T('Account email *', 'بريد الحساب *')}</label><input id="d-email" name="email" type="email" required autocomplete="email" placeholder="you@example.com" data-i18n-attr="placeholder:{ek}">
    <label for="d-msg">{T('Anything we should know? *', 'هل هناك ما يجب أن نعرفه؟ *')}</label><textarea id="d-msg" name="message" required maxlength="2000" style="min-height:90px"></textarea>
    <input class="hp" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">
    <div class="cta-row" style="margin-top:16px"><button class="btn btn-dark" type="submit">{T('Request deletion', 'اطلب الحذف')}</button></div>
    <p class="status" role="status" aria-live="polite"></p>
  </form></div>
</div></section>''' + foot()


def legal_page(page, kind):
    sections = LEGAL[kind]
    intro_en, intro_ar = LEGAL[kind + '_intro']
    if kind == 'privacy':
        h = head(page, 'Privacy policy — OneSpace', 'سياسة الخصوصية — OneSpace', 'How OneSpace collects, uses, stores and deletes your data. No ads, no data selling.', 'كيف يجمع OneSpace بياناتك ويستخدمها ويحفظها ويحذفها. بلا إعلانات ولا بيع للبيانات.')
        hero = page_hero('Privacy policy', 'سياسة الخصوصية', 'Privacy policy', 'سياسة الخصوصية', intro_en, intro_ar)
    else:
        h = head(page, 'Terms of use — OneSpace', 'شروط الاستخدام — OneSpace', 'The terms for using OneSpace during the early test.', 'شروط استخدام OneSpace خلال التجربة المبكرة.')
        hero = page_hero('Terms of use', 'شروط الاستخدام', 'Terms of use', 'شروط الاستخدام', intro_en, intro_ar)
    toc, body = [], []
    for i, (t, html_en, t_ar, html_ar) in enumerate(sections):
        toc.append(f'<a href="#s{i + 1}">{T(t, t_ar)}</a>')
        body.append(f'<h2 id="s{i + 1}">{T(t, t_ar)}</h2>{T(html_en, html_ar, "div")}')
    updated = (T('Last updated: 17 November 2026', 'آخر تحديث: 17 نوفمبر 2026', 'p', 'muted') if kind == 'privacy'
               else T('Last updated: 16 November 2026', 'آخر تحديث: 16 نوفمبر 2026', 'p', 'muted'))
    return h + hero + f'''<section style="padding-top:20px"><div class="wrap with-toc">
  <nav class="toc" aria-label="On this page">{''.join(toc)}</nav>
  <div class="legal">{updated}{''.join(body)}</div>
</div></section>''' + foot()


def store_shots():
    if not (ROOT / 'assets' / 'press' / 'store-en-1.png').exists():
        return ''
    imgs = ''.join(f'<a href="assets/press/store-en-{i}.png" download data-ar-href="assets/press/store-ar-{i}.png"><img src="assets/press/store-en-{i}.png" data-en-src="assets/press/store-en-{i}.png" data-ar-src="assets/press/store-ar-{i}.png" alt="Store screenshot {i}" loading="lazy" width="1080" height="1920"></a>' for i in range(1, 7))
    return f'''<section><div class="wrap"><div class="sec-head">{T('App store screenshots', 'لقطات متجر التطبيقات', 'h2')}{T('Real screens from the app with the fictional couple Omar and Lina. 1080×1920, English and Arabic (switch the page language).', 'شاشات حقيقية من التطبيق مع الزوجين الافتراضيين عمر ولينا. 1080×1920 بالعربية والإنجليزية (بدّل لغة الصفحة).', 'p', 'muted')}</div>
  <div class="grid assets-grid store-grid">{imgs}</div></div></section>'''


def _press_previews(html):
    # Show light previews; the links still download the full-size PNGs.
    return re.sub(r'((?:src|data-en-src|data-ar-src)=")assets/press/([\w-]+)\.png"', r'\1assets/press/preview/\2.webp"', html)


def page_share_kit():
    h = head('share-kit.html', 'OneSpace share kit', 'مواد مشاركة OneSpace',
             'Logos, colours, descriptions in English and Arabic, social images and ready-to-send messages for telling people about OneSpace.',
             'الشعارات والألوان والأوصاف بالعربية والإنجليزية وصور التواصل ورسائل جاهزة للتعريف بـ OneSpace.')
    copies = [
        ('one-liner', 'One line', 'سطر واحد', 'OneSpace — the private app for the life you share, near or far.', 'OneSpace — التطبيق الخاص للحياة التي تتشاركانها، قريبين أو بعيدين.'),
        ('short', 'Short description (store, 80 characters)', 'وصف قصير (المتجر، 80 حرفًا)', 'Plans, reminders, trips, letters and memories for two — private and calm.', 'خطط وتذكيرات ورحلات ورسائل وذكريات لشخصين — بخصوصية وهدوء.'),
        ('long', 'Long description', 'وصف طويل',
         'OneSpace is one private space for you and your partner. See your shared day in Today, keep counters for your special dates and your places on a map, plan trips and occasions together, and stay close with little gestures, sealed letters and a daily check-in. It adapts to couples who live together and couples who live apart, works in English and Arabic, has nine themes, and never shows ads or sells data.',
         'OneSpace مساحة خاصة واحدة لك ولشريكك. شاهدا يومكما المشترك في «اليوم»، واحتفظا بعدّادات لتواريخكما الخاصة وأماكنكما على خريطة، وخططا للرحلات والمناسبات معًا، وابقيا قريبين بلمسات صغيرة ورسائل مغلقة وتواصل يومي. يتكيّف مع الأزواج الذين يعيشون معًا أو متباعدين، ويعمل بالعربية والإنجليزية، وفيه تسع سمات، ولا يعرض إعلانات ولا يبيع البيانات أبدًا.'),
        ('whatsapp', 'Message to a friend', 'رسالة لصديق', 'We have been testing OneSpace — a private app just for couples: shared plans, reminders, trips and little gestures. It is free in early access: ' + BASE + 'join.html', 'نجرّب OneSpace — تطبيق خاص للأزواج فقط: خطط وتذكيرات ورحلات ولمسات صغيرة مشتركة. وهو مجاني في الوصول المبكر: ' + BASE + 'join.html'),
    ]
    copy_html = ''
    for cid, t, tar, en, ar in copies:
        copy_html += f'''<div class="kit-copy card reveal">{T(t, tar, 'h3')}<button class="btn btn-ghost btn-sm copy" type="button" data-copy="c-{cid}">{T('Copy', 'انسخ')}</button><pre id="c-{cid}">{T(en, ar)}</pre></div>'''
    colours = [('#E8745A', 'Coral'), ('#1F6E78', 'Teal'), ('#14213D', 'Ink'), ('#FBF8F1', 'Cream'), ('#F3A27E', 'Peach'), ('#4A80D8', 'Midnight accent')]
    col_html = ''.join(f'<div class="card" style="padding:14px"><div style="height:70px;border-radius:12px;background:{c};border:1px solid var(--line)"></div><b style="display:block;margin-top:10px">{n}</b><code>{c}</code></div>' for c, n in colours)
    return h + page_hero('Share kit', 'مواد المشاركة', 'Tell people about OneSpace.', 'عرّف الناس بـ OneSpace.',
                         'Ready-made words, images and colours for friends, testers, app stores and the press. Everything here may be used to talk about OneSpace.',
                         'كلمات وصور وألوان جاهزة للأصدقاء والمختبرين ومتاجر التطبيقات والصحافة. يمكن استخدام كل ما هنا للحديث عن OneSpace.') + f'''
<section style="padding-top:20px"><div class="wrap">
  <div class="sec-head">{T('Words', 'الكلمات', 'h2')}{T('Copy them as they are. Arabic appears when you switch language.', 'انسخها كما هي. تظهر العربية عند تبديل اللغة.', 'p', 'muted')}</div>
  <div class="grid g2">{copy_html}</div>
</div></section>
<section class="tint"><div class="wrap">
  <div class="sec-head">{T('Images', 'الصور', 'h2')}{T('Right-click or long-press to save.', 'انقر بزر الفأرة الأيمن أو اضغط مطولًا للحفظ.', 'p', 'muted')}</div>
  <div class="grid g3 assets-grid">
    <a href="assets/press/og-image.png" download><img src="assets/press/og-image.png" alt="OneSpace link preview image, 1200 by 630" loading="lazy" width="1200" height="630">{T('Link preview · 1200×630', 'معاينة الرابط · 1200×630', 'p', 'muted')}</a>
    <a href="assets/press/social-square.png" download><img src="assets/press/social-square.png" alt="OneSpace square social post, 1080 by 1080" loading="lazy" width="1080" height="1080">{T('Square post · 1080×1080', 'منشور مربع · 1080×1080', 'p', 'muted')}</a>
    <a href="assets/press/social-story.png" download><img src="assets/press/social-story.png" alt="OneSpace story image, 1080 by 1920" loading="lazy" width="1080" height="1920" style="max-height:420px;width:auto;margin:auto">{T('Story · 1080×1920', 'قصة · 1080×1920', 'p', 'muted')}</a>
    <a href="assets/press/store-feature.png" download><img src="assets/press/store-feature.png" alt="OneSpace store feature graphic, 1024 by 500" loading="lazy" width="1024" height="500">{T('Play Store feature graphic · 1024×500', 'صورة مميزة لمتجر Play · 1024×500', 'p', 'muted')}</a>
    <a href="assets/icon-512.png" download><img src="assets/icon-512.png" alt="OneSpace app icon" loading="lazy" width="512" height="512" style="max-width:200px;margin:auto">{T('App icon · 512×512', 'أيقونة التطبيق · 512×512', 'p', 'muted')}</a>
    <a href="assets/mark.svg" download><img src="assets/mark.svg" alt="OneSpace mark (SVG)" loading="lazy" width="200" height="200" style="max-width:200px;margin:auto">{T('Logo mark · SVG', 'رمز الشعار · SVG', 'p', 'muted')}</a>
  </div>
</div></section>
{store_shots()}
<section><div class="wrap">
  <div class="sec-head">{T('Colours', 'الألوان', 'h2')}</div>
  <div class="grid g3" style="grid-template-columns:repeat(auto-fit,minmax(150px,1fr))">{col_html}</div>
  <div class="note-box" style="margin-top:28px">{T('Please write the name as <b>OneSpace</b> — one word, capital O and S. Don’t change the logo’s colours or shape. Questions? <a href="support.html">Contact us</a>.', 'يُرجى كتابة الاسم <b>OneSpace</b> — كلمة واحدة بحرفي O وS كبيرين. لا تغيّر ألوان الشعار أو شكله. أسئلة؟ <a href="support.html">تواصل معنا</a>.')}</div>
</div></section>
''' + foot()


def page_confirm():
    h = head('confirm.html', 'Confirm your email — OneSpace Founders', 'تأكيد بريدك — مؤسسو OneSpace',
             'Confirm your email to join the OneSpace Founding 500.', _nov_ar('Confirm your email to join the OneSpace Founding 500.'))
    h = h.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex">', 1)
    return h + f"""
<section class="page-hero"><div class="narrow center" data-confirm>
  <div class="cf-state" data-state="loading"><div style="font-size:46px">⏳</div>{T('Confirming your email…', 'جارٍ تأكيد بريدك…', 'h1')}</div>
  <div class="cf-state" data-state="ok" hidden>
    <div style="font-size:46px">🎉</div>
    {N('Welcome to the Founding 500!', 'h1')}
    <div class="founder-badge"><span>{N('Founder Member')}</span><b>{T('Founding 500', 'المؤسسون الـ500')}</b></div>
    <p class="lead" data-role-first>{N('Your email is confirmed — you’re one of the Founding 500. We sent the details to your inbox.')}</p>
    <p class="lead" data-role-partner hidden>{N('You have joined your partner — you’re both Founder Members.')}</p>
    <div class="panel" data-invite hidden style="text-align:start;margin-top:20px">
      {T('Now invite your partner', 'الآن ادعُ شريكك', 'h3')}
      {N('Have a partner? Send them this link and they join the Founding 500 with you:', 'p', 'muted')}
      <input class="invite-url" readonly data-invite-url value="">
      <div class="cta-row" style="margin-top:12px"><a class="btn btn-primary" data-invite-wa href="#" target="_blank" rel="noopener">{T('Send on WhatsApp', 'أرسل عبر واتساب')}</a>
      <button class="btn btn-ghost" type="button" data-invite-copy>{T('Copy link', 'انسخ الرابط')}</button></div>
    </div>
    <p style="margin-top:22px"><a class="btn btn-ghost" href="how-it-works.html">{T('While you wait: try the demo →', 'أثناء الانتظار: جرّب العرض ←')}</a></p>
  </div>
  <div class="cf-state" data-state="waitlist" hidden>
    <div style="font-size:46px">🕊</div>{N('You’re on the waitlist', 'h1')}
    {N('Your email is confirmed. All 500 Founder places are taken, so we’ll invite you as soon as more places open.', 'p', 'lead')}</div>
  <div class="cf-state" data-state="expired" hidden>
    <div style="font-size:46px">⌛</div>{T('This link has expired', 'انتهت صلاحية هذا الرابط', 'h1')}
    {T('Links last 7 days. Sign up again with the same email and we’ll send a fresh one.', 'تصلح الروابط 7 أيام. سجّل مجددًا بالبريد نفسه وسنرسل رابطًا جديدًا.', 'p', 'lead')}
    <a class="btn btn-primary" href="join.html">{T('Sign up again', 'سجّل مجددًا')}</a></div>
  <div class="cf-state" data-state="invalid" hidden>
    <div style="font-size:46px">🔗</div>{T('We couldn’t use this link', 'لم نتمكن من استخدام هذا الرابط', 'h1')}
    {T('Open the newest email from founders@onespace.live, or sign up again.', 'افتح أحدث رسالة من founders@onespace.live، أو سجّل مجددًا.', 'p', 'lead')}
    <a class="btn btn-primary" href="join.html">{T('Go to sign-up', 'إلى التسجيل')}</a></div>
</div></section>""" + foot()


def page_unsubscribe():
    h = head('unsubscribe.html', 'Unsubscribe — OneSpace', 'إلغاء الاشتراك — OneSpace', 'Stop OneSpace Founder emails.', 'أوقف رسائل مؤسسي OneSpace.')
    h = h.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex">', 1)
    return h + f"""
<section class="page-hero"><div class="narrow center" data-unsub>
  <div class="cf-state" data-state="ask"><div style="font-size:46px">✉️</div>{T('Stop Founder emails?', 'إيقاف رسائل المؤسسين؟', 'h1')}
    {N('You will stop receiving OneSpace launch updates and invitations. You stay a Founder Member.', 'p', 'lead')}
    <button class="btn btn-primary" type="button" data-unsub-go>{T('Unsubscribe', 'إلغاء الاشتراك')}</button></div>
  <div class="cf-state" data-state="done" hidden><div style="font-size:46px">✅</div>{T('You’re unsubscribed', 'تم إلغاء اشتراكك', 'h1')}
    {T('No more emails from us. Changed your mind? Sign up again with the same email.', 'لن نراسلك بعد الآن. غيّرت رأيك؟ سجّل مجددًا بالبريد نفسه.', 'p', 'lead')}</div>
  <div class="cf-state" data-state="invalid" hidden><div style="font-size:46px">🔗</div>{T('We couldn’t use this link', 'لم نتمكن من استخدام هذا الرابط', 'h1')}
    {T('Reply “unsubscribe” to any of our emails, or write to <a href="mailto:privacy@onespace.live">privacy@onespace.live</a>.', 'ردّ بكلمة «إلغاء» على أي رسالة منا، أو راسل <a href="mailto:privacy@onespace.live">privacy@onespace.live</a>.', 'p', 'lead')}</div>
</div></section>""" + foot()


def page_404():
    h = head('404.html', 'Page not found — OneSpace', 'الصفحة غير موجودة — OneSpace', 'This page does not exist.', 'هذه الصفحة غير موجودة.')
    return h.replace('<link rel="stylesheet" href="assets/os.css">', '<base href="/"><link rel="stylesheet" href="assets/os.css">').replace('<meta name="description"', '<meta name="robots" content="noindex"><meta name="description"', 1) + f'''
<section class="page-hero" style="padding:110px 0"><div class="narrow center">
  <div style="font-size:64px">🧭</div>{T('This page wandered off.', 'هذه الصفحة تاهت.', 'h1')}
  {T('It may have moved when we tidied the site. Try one of these:', 'ربما انتقلت عندما رتّبنا الموقع. جرّب أحد هذه:', 'p', 'lead')}
  <div class="cta-row" style="justify-content:center"><a class="btn btn-primary" href="./">{T('Home', 'الرئيسية')}</a><a class="btn btn-ghost" href="features.html">{T('Features', 'المزايا')}</a><a class="btn btn-ghost" href="faq.html">{T('FAQ', 'الأسئلة')}</a></div>
</div></section>''' + foot()


def redirect(target, title):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{title} — OneSpace</title>
<meta name="robots" content="noindex"><link rel="canonical" href="{BASE}{target}">
<meta http-equiv="refresh" content="0; url={target}"></head>
<body><p>This page moved to <a href="{target}">{target}</a>.</p><script>location.replace('{target}'+location.search+location.hash)</script></body></html>
'''


PAGES = {
    'index.html': (page_index, '1.0', 'weekly'), 'features.html': (page_features, '0.9', 'weekly'), 'connect-care.html': (page_connect_care, '0.9', 'weekly'),
    'long-distance.html': (lambda: persona_page('long-distance.html', True), '0.8', 'monthly'),
    'living-together.html': (lambda: persona_page('living-together.html', False), '0.8', 'monthly'),
    'on-my-own.html': (page_solo, '0.8', 'monthly'),
    'how-it-works.html': (page_how, '0.8', 'monthly'), 'whats-new.html': (page_whats_new, '0.7', 'weekly'),
    'scenarios.html': (page_scenarios, '0.8', 'monthly'), 'faq.html': (page_faq, '0.7', 'monthly'), 'compare.html': (page_compare, '0.8', 'monthly'), 'tutorials.html': (page_tutorials, '0.7', 'monthly'), 'guides.html': (page_guides, '0.8', 'weekly'), 'join.html': (page_join, '0.9', 'monthly'),
    'support.html': (page_support, '0.6', 'monthly'), 'share-kit.html': ((lambda: _press_previews(page_share_kit())), '0.4', 'monthly'),
    'privacy.html': (lambda: legal_page('privacy.html', 'privacy'), '0.4', 'yearly'),
    'terms.html': (lambda: legal_page('terms.html', 'terms'), '0.4', 'yearly'),
    'delete-account.html': (page_delete, '0.4', 'yearly'),
}
for _d in DEEP:
    PAGES[_d['slug']] = ((lambda d=_d: deep_page(d)), '0.9', 'monthly')
for _g in GUIDES:
    PAGES[_g['slug']] = ((lambda g=_g: guide_page(g)), '0.7', 'monthly')
REDIRECTS = {'v4.html': ('./', 'Home'), 'v4-tutorial.html': ('how-it-works.html', 'How it works')}


def arabic_page(html, name):
    """The same page, rendered in Arabic on the server so search engines can index it at /ar/."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    for el in soup.find_all(attrs={'data-i18n': True}):
        k = el.get('data-i18n')
        if k in AR:
            el.clear()
            el.append(BeautifulSoup(AR[k], 'html.parser'))
    for el in soup.find_all(attrs={'data-i18n-attr': True}):
        for pair in el['data-i18n-attr'].split(';'):
            attr, k = pair.split(':')
            if k in AR:
                el[attr] = AR[k]
    for el in soup.find_all(attrs={'data-ar-src': True}):
        el['src'] = el['data-ar-src']
        if el.get('data-ar-poster'):
            el['poster'] = el['data-ar-poster']
    hroot = soup.find('html')
    hroot['lang'], hroot['dir'] = 'ar', 'rtl'
    t = soup.find('title')
    if t and t.get('data-ar'):
        t.string = revise(t['data-ar'])
    slug = '' if name == 'index.html' else name
    soup.find('link', rel='canonical')['href'] = BASE + 'ar/' + slug
    desc = soup.find('meta', attrs={'name': 'description'})
    for prop, val in (('og:title', t.string if t else None), ('og:description', desc['content'] if desc else None), ('og:url', BASE + 'ar/' + slug)):
        m = soup.find('meta', property=prop)
        if m is not None and val:
            m['content'] = val
    og = soup.find('meta', property='og:type')
    if og is not None:
        og.insert_after(soup.new_tag('meta', property='og:locale', content='ar_AR'))
    for b in soup.find_all('button', class_='lang'):
        b.string = 'English'
        b['aria-label'] = 'Switch to English'
    localize_structured(soup, 'ar', BASE + 'ar/' + slug)
    out = revise(str(soup))
    # Shared files live at the site root, one level up from /ar/.
    return re.sub(r'((?:src|href|poster|data-en-src|data-ar-src|data-en-poster|data-ar-poster|srcset)=")(assets/|site\.webmanifest)', r'\1/\2', out)


def llms_txt():
    lines = ['# OneSpace', '', '> OneSpace is a private app for couples — living together or apart — that keeps the shared life in one place: '
             'one shared watchlist, one place to compare things to buy, one trip with every flight option, one calendar, reminders for me, '
             'my partner or both, occasions with budgets, counters, letters and memories. English, Arabic, Spanish, French and German on the website. Android early access; iPhone planned.', '',
             '## Main pages']
    for n, (_, p, _c) in PAGES.items():
        if n in ('privacy.html', 'terms.html', 'delete-account.html'):
            continue
        lines.append(f'- [{n.replace(".html", "").replace("-", " ").title() if n != "index.html" else "Home"}]({BASE}{"" if n == "index.html" else n})')
    lines += ['', '## Languages', f'- [العربية]({BASE}ar/)', f'- [Español]({BASE}es/)', f'- [Français]({BASE}fr/)', f'- [Deutsch]({BASE}de/)', '', '## Legal', f'- [Privacy]({BASE}privacy.html)', f'- [Terms]({BASE}terms.html)', '']
    return '\n'.join(lines)



def refresh_legal_revisions():
    """Keep document/version dates independent for every published language.

    Each legal page's semantic content is fingerprinted after localization.
    A changed fingerprint after its first recorded build bumps only that
    locale/document revision; routine site builds never change legal dates.
    """
    from bs4 import BeautifulSoup
    manifest_path = ROOT / 'assets' / 'legal-revisions.json'
    revisions = json.loads(manifest_path.read_text(encoding='utf-8'))
    labels = {
        'en': ('Last updated: ', 'Version '),
        'ar': ('آخر تحديث: ', 'الإصدار '),
        'es': ('Última actualización: ', 'Versión '),
        'fr': ('Dernière mise à jour : ', 'Version '),
        'de': ('Zuletzt aktualisiert: ', 'Version '),
    }
    months = {
        'ar': ('يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو',
               'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'),
        'es': ('enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
               'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'),
        'fr': ('janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet',
               'août', 'septembre', 'octobre', 'novembre', 'décembre'),
        'de': ('Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli',
               'August', 'September', 'Oktober', 'November', 'Dezember'),
    }
    for document in ('privacy', 'terms', 'delete-account'):
        doc_versions = revisions.setdefault(document, {})
        for locale in LANGS:
            html_path = ROOT / ('' if locale == 'en' else locale) / (document + '.html')
            soup = BeautifulSoup(html_path.read_text(encoding='utf-8'), 'html.parser')
            legal = soup.select_one('.legal')
            if legal is None:
                raise ValueError(f'No .legal content: {html_path}')
            intro = soup.select_one('.page-hero .lead')
            meaningful = []
            for child in legal.children:
                if getattr(child, 'name', None) == 'p' and (
                    'muted' in child.get('class', []) or
                    'legal-revision' in child.get('class', [])
                ):
                    continue
                meaningful.append(str(child))
            digest = hashlib.sha256((str(intro or '') + ''.join(meaningful)).encode('utf-8')).hexdigest()
            entry = doc_versions.setdefault(locale, {'date': TODAY, 'version': '1.0'})
            previous_digest = entry.get('content_hash')
            if previous_digest and previous_digest != digest:
                try:
                    major, minor = (int(x) for x in entry['version'].split('.'))
                    entry['version'] = f'{major}.{minor + 1}'
                except (KeyError, ValueError):
                    entry['version'] = '1.1'
                entry['date'] = TODAY
            entry['content_hash'] = digest

            for child in list(legal.children):
                if getattr(child, 'name', None) == 'p' and (
                    'muted' in child.get('class', []) or
                    'legal-revision' in child.get('class', [])
                ):
                    child.decompose()
            revised_on = date.fromisoformat(entry['date'])
            if locale == 'en':
                printed = revised_on.strftime('%-d %B %Y')
            elif locale == 'ar':
                printed = f'{revised_on.day} {months[locale][revised_on.month - 1]} {revised_on.year}'
            elif locale == 'es':
                printed = f'{revised_on.day} de {months[locale][revised_on.month - 1]} de {revised_on.year}'
            elif locale == 'fr':
                printed = f'{revised_on.day} {months[locale][revised_on.month - 1]} {revised_on.year}'
            else:
                printed = f'{revised_on.day}. {months[locale][revised_on.month - 1]} {revised_on.year}'

            p = soup.new_tag('p', attrs={'class': 'legal-revision'})
            p.append(labels[locale][0])
            t = soup.new_tag('time')
            t['datetime'] = entry['date']
            t.string = printed
            p.append(t)
            p.append(' · ' + labels[locale][1] + entry['version'])
            legal.insert(0, p)
            meta = soup.new_tag('meta')
            meta['name'] = 'last-modified'
            meta['content'] = entry['date']
            if soup.head:
                soup.head.append(meta)
            html_path.write_text(str(soup), encoding='utf-8')
    manifest_path.write_text(json.dumps(revisions, ensure_ascii=False, indent=2) + '\n',
                             encoding='utf-8')


def main():
    for name, (fn, _, _) in PAGES.items():
        (ROOT / name).write_text(fn(), encoding='utf-8')
    (ROOT / '404.html').write_text(page_404(), encoding='utf-8')
    for name, (target, title) in REDIRECTS.items():
        (ROOT / name).write_text(redirect(target, title), encoding='utf-8')
    # The approved editorial language review is applied after all original copy is registered.
    AR.update({k: revise(v) for k, v in AR.items()})
    (ROOT / 'assets' / 'ar.js').write_text('window.ONESPACE_AR=' + json.dumps(AR, ensure_ascii=False, sort_keys=True) + ';\n', encoding='utf-8')
    (ROOT / 'ar').mkdir(exist_ok=True)
    (ROOT / 'confirm.html').write_text(page_confirm(), encoding='utf-8')
    (ROOT / 'ar' / 'confirm.html').write_text(arabic_page((ROOT / 'confirm.html').read_text(encoding='utf-8'), 'confirm.html'), encoding='utf-8')
    (ROOT / 'unsubscribe.html').write_text(page_unsubscribe(), encoding='utf-8')
    (ROOT / 'ar' / 'unsubscribe.html').write_text(arabic_page((ROOT / 'unsubscribe.html').read_text(encoding='utf-8'), 'unsubscribe.html'), encoding='utf-8')
    for name in PAGES:
        (ROOT / 'ar' / name).write_text(arabic_page((ROOT / name).read_text(encoding='utf-8'), name), encoding='utf-8')
    # Every language reuses the identical full English DOM: screenshots, tutorial,
    # demo, theme preview, interactive forms and all original product pages.
    count = build_locales(ROOT, list(PAGES) + ['confirm.html', 'unsubscribe.html'])
    # Link contextual feature mentions only after each narrative is fully localized.
    # English, Arabic and ES/FR/DE retain exactly the same prose.
    journey_links = linkify_journeys(ROOT, JOURNEYS, JOURNEY_FEATURES)
    print('Scenario feature links by locale:', journey_links)
    print(f'Localized {count} complete pages from source')
    refresh_legal_revisions()
    urls = ''
    for n, (_, p, c) in PAGES.items():
        slug = '' if n == 'index.html' else n
        alt = ''.join(f'<xhtml:link rel="alternate" hreflang="{lang}" href="{BASE}{"" if lang == "en" else lang+"/"}{slug}"/>' for lang in LANGS)
        alt += f'<xhtml:link rel="alternate" hreflang="x-default" href="{BASE}{slug}"/>'
        for lang in LANGS:
            loc = BASE+('' if lang=='en' else lang+'/')+slug
            priority = p if lang=='en' else f'{max(float(p)-0.1,0.1):.1f}'
            urls += f'  <url><loc>{loc}</loc><lastmod>{TODAY}</lastmod><changefreq>{c}</changefreq><priority>{priority}</priority>{alt}</url>\n'
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
                                      f'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n{urls}</urlset>\n', encoding='utf-8')
    (ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nDisallow: /v4.html\nDisallow: /v4-tutorial.html\nDisallow: /confirm.html\nDisallow: /ar/confirm.html\nDisallow: /unsubscribe.html\nDisallow: /ar/unsubscribe.html\nDisallow: /es/confirm.html\nDisallow: /fr/confirm.html\nDisallow: /de/confirm.html\nDisallow: /es/unsubscribe.html\nDisallow: /fr/unsubscribe.html\nDisallow: /de/unsubscribe.html\n\nSitemap: {BASE}sitemap.xml\n', encoding='utf-8')
    (ROOT / f'{INDEXNOW_KEY}.txt').write_text(INDEXNOW_KEY + '\n', encoding='utf-8')
    (ROOT / 'llms.txt').write_text(llms_txt(), encoding='utf-8')
    (ROOT / 'site.webmanifest').write_text(json.dumps({'name': 'OneSpace', 'short_name': 'OneSpace', 'start_url': './', 'display': 'standalone',
        'background_color': '#FFFFFF', 'theme_color': '#14213D', 'icons': [{'src': 'assets/icon-512.png', 'sizes': '512x512', 'type': 'image/png'},
        {'src': 'assets/apple-touch-icon.png', 'sizes': '180x180', 'type': 'image/png'}]}, indent=1) + '\n', encoding='utf-8')
    # Publish /privacy/, /faq/ and all other canonical routes in every language.
    # Keep the legacy .html pages as redirects for existing bookmarks and Founder emails.
    from pretty_routes import publish_pretty_routes
    count_clean = publish_pretty_routes(ROOT, PAGES)
    print(f'Published {count_clean} clean localized routes and legacy redirects')
    # Cache-busting: each page asks for os.css / os.js / ar.js by content hash, so a change reaches browsers at once.
    ver = {a: hashlib.sha256((ROOT / 'assets' / a).read_bytes()).hexdigest()[:10] for a in ('os.css', 'os.js', 'ar.js')}
    for f in list(ROOT.glob('*.html')) + [p for lang in ('ar',)+NEW_LANGS for p in (ROOT/lang).rglob('*.html')] + list(p for p in ROOT.glob('*/index.html') if p.parent.name not in ('ar','es','fr','de')):
        t = f.read_text(encoding='utf-8')
        u = re.sub(r'assets/(os\.css|os\.js|ar\.js)(\?v=[0-9a-f]+)?"', lambda m: f'assets/{m.group(1)}?v={ver[m.group(1)]}"', t)
        if u != t: f.write_text(u, encoding='utf-8')
    print(f'{len(PAGES)} original pages, {len(REDIRECTS)} redirects, {len(AR)} Arabic strings, {count} full ES/FR/DE pages')


if __name__ == '__main__':
    main()
