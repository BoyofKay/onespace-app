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
from tutorial_additions import TUTORIAL_ADDITIONS
from tutorial_journeys import JOURNEY_TUTORIAL_ADDITIONS
assert sum(map(len,FAQ_ADDITIONS.values()))==12
assert sum(map(len,TUTORIAL_ADDITIONS.values()))==12
assert len(JOURNEY_TUTORIAL_ADDITIONS['journey'])==2
ALL_GUIDES=GUIDE_ADDITIONS_1+GUIDE_ADDITIONS_2
assert len(ALL_GUIDES)==9 and len({g['slug'] for g in ALL_GUIDES})==9
for lang_idx,lang in enumerate(('en','ar','es','fr','de')):
    prefix='' if lang=='en' else lang+'/'
    faq=BeautifulSoup((ROOT/prefix/'faq.html').read_text(encoding='utf8'),'html.parser')
    tutorials=BeautifulSoup((ROOT/prefix/'tutorials.html').read_text(encoding='utf8'),'html.parser')
    listing=BeautifulSoup((ROOT/prefix/'guides.html').read_text(encoding='utf8'),'html.parser')
    assert len(faq.select('details[data-faq]'))==50,(lang,'FAQ count')
    faq_schema=[json.loads(s.string) for s in faq.select('script[type="application/ld+json"]')
                if s.string and json.loads(s.string).get('@type')=='FAQPage']
    assert len(faq_schema)==1,(lang,'FAQ schema')
    assert len(faq_schema[0]['mainEntity'])==50,(lang,'FAQ JSON-LD length')
    for i,entry in enumerate(faq_schema[0]['mainEntity']):
        card=faq.select('details[data-faq]')[i]
        assert entry['name']==card.summary.get_text(' ',strip=True),(lang,'FAQ schema name',i)
        assert entry['acceptedAnswer']['text']==card.find('div').get_text(' ',strip=True),(lang,'FAQ schema answer',i)
    assert len(tutorials.select('details[data-faq]'))==29,(lang,'tutorial count')
    assert len(listing.select('a.art-card'))==12,(lang,'guide cards')
    assert len(listing.select('details.guide-show-more'))==1,(lang,'extra guides are opt-in')
    assert len(listing.select('details.guide-show-more a.art-card'))==9,(lang,'hidden guides')
    assert len(tutorials.select('a[href*="scenarios.html#story-"]'))>=2,(lang,'tutorial journey links')
    for grp in FAQ_ADDITIONS.values():
        for q,a in grp:
            assert q[lang_idx] in faq.get_text(' ',strip=True),(lang,'FAQ question',q[0])
            assert a[lang_idx] in faq.get_text(' ',strip=True),(lang,'FAQ answer',q[0])
    for group in [*TUTORIAL_ADDITIONS.values(),*JOURNEY_TUTORIAL_ADDITIONS.values()]:
        for guide in group:
            assert guide['t'][lang_idx] in tutorials.get_text(' ',strip=True),(lang,'tutorial title')
            for step in guide['steps']:
                rendered=BeautifulSoup(step[lang_idx],'html.parser').get_text(' ',strip=True)
                assert rendered in tutorials.get_text(' ',strip=True),(lang,'tutorial step',guide['t'][0],rendered)
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
        assert schema['mainEntityOfPage']=='https://onespace.live/'+prefix+guide['slug'],(lang,guide['slug'],'canonical JSON-LD')
print('PASS: 50 FAQs, 29 step-by-step tutorials with full journeys, 12 guides, all five locales.')
