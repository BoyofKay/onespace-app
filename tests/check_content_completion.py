"""Checks approved content expansion and full EN/AR/ES/FR/DE parity."""
from pathlib import Path
from bs4 import BeautifulSoup
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'content'))
from guide_additions_1 import GUIDE_ADDITIONS_1
from guide_additions_2 import GUIDE_ADDITIONS_2
from faq_additions import FAQ_ADDITIONS
from faq_master import web_groups as _faq_web_groups
import tutorial_videos
assert sum(map(len,FAQ_ADDITIONS.values()))==18  # 12 + 6 closed-tester answers (26 Nov 2026)
# 27 Nov 2026: the FAQ is content/faq/*.json (website items) plus the website-only Founder group.
def _expected_faq_total():
    en=BeautifulSoup((ROOT/'faq.html').read_text(encoding='utf8'),'html.parser')
    total=len(en.select('details[data-faq]'))
    web=sum(len(g['items']) for g in _faq_web_groups())
    # 27 Nov 2026 (owner): only the shared FAQ; no Founder Members group.
    assert total==web and not en.select('#founders'),(total,web)
    return total
EXPECTED_FAQ=_expected_faq_total()

# 27 Nov 2026 (D110): the tutorials page is one video tutorial per feature (17).
VIDEO_TUTORIALS=tutorial_videos.tutorials()
assert len(VIDEO_TUTORIALS)==17 and len({t['id'] for t in VIDEO_TUTORIALS})==17
ALL_GUIDES=GUIDE_ADDITIONS_1+GUIDE_ADDITIONS_2
assert len(ALL_GUIDES)==9 and len({g['slug'] for g in ALL_GUIDES})==9
for lang_idx,lang in enumerate(('en','ar','es','fr','de')):
    prefix='' if lang=='en' else lang+'/'
    faq=BeautifulSoup((ROOT/prefix/'faq.html').read_text(encoding='utf8'),'html.parser')
    tutorials=BeautifulSoup((ROOT/prefix/'tutorials.html').read_text(encoding='utf8'),'html.parser')
    listing=BeautifulSoup((ROOT/prefix/'guides.html').read_text(encoding='utf8'),'html.parser')
    assert len(faq.select('details[data-faq]'))==EXPECTED_FAQ,(lang,'FAQ count')
    faq_schema=[json.loads(s.string) for s in faq.select('script[type="application/ld+json"]')
                if s.string and json.loads(s.string).get('@type')=='FAQPage']
    assert len(faq_schema)==1,(lang,'FAQ schema')
    assert len(faq_schema[0]['mainEntity'])==EXPECTED_FAQ,(lang,'FAQ JSON-LD length')
    for i,entry in enumerate(faq_schema[0]['mainEntity']):
        card=faq.select('details[data-faq]')[i]
        assert entry['name']==card.summary.get_text(' ',strip=True),(lang,'FAQ schema name',i)
        assert entry['acceptedAnswer']['text']==card.find('div').get_text(' ',strip=True),(lang,'FAQ schema answer',i)
    assert len(tutorials.select('article.tut[data-tut]'))==17,(lang,'tutorial count')
    faq_ids={d.get('id') for d in faq.select('details[data-faq]')}
    tut_text=tutorials.get_text(' ',strip=True)
    for t in VIDEO_TUTORIALS:
        card=tutorials.select_one(f'article.tut#{t["id"]}')
        assert card,(lang,'tutorial missing',t['id'])
        assert t['title'][lang] in card.get_text(' ',strip=True),(lang,'tutorial title',t['id'])
        buttons=card.select('.tut-chapters button[data-t]')
        assert len(buttons)==len(t['chapters']),(lang,'chapter count',t['id'])
        for c in t['chapters']:
            assert c[lang] in card.get_text(' ',strip=True),(lang,'chapter caption',t['id'],c['en'])
        for key in ('partner','solo','works'):
            if key in t: assert t[key][lang] in card.get_text(' ',strip=True),(lang,key,t['id'])
        link=card.select_one('.faq-more a')['href'].split('#')[1]
        assert link in faq_ids,(lang,'tutorial FAQ link',t['id'],link)
    assert len(listing.select('a.art-card'))==13,(lang,'guide cards')
    assert len(listing.select('details.guide-show-more'))==1,(lang,'extra guides are opt-in')
    assert len(listing.select('details.guide-show-more a.art-card'))==10,(lang,'hidden guides')
    assert len(tutorials.select('a[href*="scenarios.html#story-"]'))>=2,(lang,'tutorial journey links')
    # 27 Nov 2026: only the website-only Founder questions still come from faq_additions;
    # the rest of the FAQ is content/faq/*.json (checked by the schema/count tests above).
    for grp in []:  # Founder Members questions removed from the FAQ (27 Nov 2026)
        for q,a in grp:
            assert q[lang_idx] in faq.get_text(' ',strip=True),(lang,'FAQ question',q[0])
            assert a[lang_idx] in faq.get_text(' ',strip=True),(lang,'FAQ answer',q[0])
    for guide in ALL_GUIDES:
        page=BeautifulSoup((ROOT/prefix/guide['slug']).read_text(encoding='utf8'),'html.parser')
        content=page.get_text(' ',strip=True)
        assert guide['title'][lang_idx] in content,(lang,guide['slug'],'title')
        assert guide['intro'][lang_idx] in content,(lang,guide['slug'],'intro')
        assert guide['how'][lang_idx] in content,(lang,guide['slug'],'how')
        for heading,tips in guide['sections']:
            assert heading[lang_idx] in content,(lang,guide['slug'],'heading')
            for tip in tips:
                assert tip[lang_idx] in content,(lang,guide['slug'],'tip')
        assert page.select_one('link[rel="canonical"]'),(lang,guide['slug'],'canonical')
        article_schemas=[json.loads(s.string) for s in page.select('script[type="application/ld+json"]')
                         if s.string and json.loads(s.string).get('@type')=='Article']
        assert len(article_schemas)==1,(lang,guide['slug'],'article structured data')
        schema=article_schemas[0]
        assert schema['inLanguage']==lang,(lang,guide['slug'],'article wrong language')
        assert schema['headline']==page.h1.get_text(' ',strip=True),(lang,guide['slug'],'article wrong headline')
        assert schema['mainEntityOfPage']=='https://onespace.live/'+prefix+guide['slug'].replace('.html','/'),(lang,guide['slug'],'canonical JSON-LD')
print(f'PASS: {EXPECTED_FAQ} FAQs, 17 video tutorials with chapter captions, 13 guides, all five locales.')
