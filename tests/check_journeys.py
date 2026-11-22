"""Acceptance tests for the 24 realistic, fully localized OneSpace journeys."""
from pathlib import Path
from bs4 import BeautifulSoup
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'content'))
from journeys_apart_01 import JOURNEYS as A1
from journeys_apart_02 import JOURNEYS as A2
from journeys_together_01 import JOURNEYS as T1
from journeys_together_02 import JOURNEYS as T2
from journeys_solo_01 import JOURNEYS as S1
from journeys_ui import FEATURES
J=A1+A2+T1+T2+S1
assert len(J)==30,len(J)
assert sum(j['mode']=='apart' for j in J)==12
assert sum(j['mode']=='together' for j in J)==12
assert sum(j['mode']=='solo' for j in J)==6
assert len({j['slug'] for j in J})==30
for j in J:
    assert 4<=len(j['stages'])<=7,(j['slug'],len(j['stages']))
    assert sum(len(stage[0].split()) for stage in j['stages'])>=(140 if j['mode']=='solo' else 200),j['slug']
    assert len(j['features'])>=4,j['slug']
    for v in [j['title'],j['teaser'],*j['stages']]:
        assert len(v)==5 and all(v),j['slug']
        assert not v[0].startswith(('INT.','CUT TO:','EXT.','SCENE ')),j['slug']
for lang in ('en','ar','es','fr','de'):
    prefix='' if lang=='en' else lang+'/'
    html=(ROOT/prefix/'scenarios.html').read_text(encoding='utf8')
    doc=BeautifulSoup(html,'html.parser')
    assert len(doc.select('details.journey-episode'))==30,lang
    assert not doc.select('div.story-scene'),lang
    for mode,slug,count in [('apart','long-distance.html',12),('together','living-together.html',12),('solo','on-my-own.html',6)]:
        mode_page=BeautifulSoup((ROOT/prefix/slug).read_text(encoding='utf8'),'html.parser')
        assert len(mode_page.select('a.journey-preview'))==count,(lang,mode)
        assert len(mode_page.select('details.journey-show-more'))==1,(lang,mode)
        more = mode_page.select_one('details.journey-show-more summary')
        assert more,(lang,mode)
        assert more.get_text(' ',strip=True).strip()[-1] not in ['+','−','×','x'],(lang,mode,'extra manual icon')
    for j in J:
        ep=doc.select_one('#story-'+j['slug'])
        assert ep is not None,(lang,j['slug'])
        assert len(ep.select('.journey-beat'))==len(j['stages']),(lang,j['slug'])
        assert len(ep.select('.journey-feature-chip'))==len(j['features']),(lang,j['slug'])
        assert not ep.select('.story-toggle'), (lang,j['slug'],'duplicate expand indicator')
        narrative = ep.select('.journey-beat p')
        assert len(narrative) == len(j['stages'])
        loc = ('en','ar','es','fr','de').index(lang)
        for i, paragraph in enumerate(narrative):
            assert paragraph.get_text('', strip=False) == j['stages'][i][loc], (lang,j['slug'],i,'narrative changed')
            assert len(paragraph.select('a.journey-inline-link')) <= 2, (lang,j['slug'],i,'too many links')
            assert not paragraph.has_attr('data-i18n'), (lang,j['slug'],i,'client could wipe links')
        links = ep.select('.journey-beat a.journey-inline-link')
        assert len(links) >= 2, (lang,j['slug'],'too few contextual feature links')
        assert len(links) <= 10, (lang,j['slug'],'too many contextual feature links')
        assert all(a.get('href') in {FEATURES[key][5] for key in j['features']} for a in links), (lang,j['slug'],'unrelated link')
        if lang in ('en','ar'):
            body=ep.get_text(' ',strip=True)
            assert j['title'][0 if lang=='en' else 1] in body,(lang,j['slug'])
        elif lang in ('es','fr','de'):
            body=ep.get_text(' ',strip=True)
            loc=('es','fr','de').index(lang)+2
            assert j['title'][loc] in body,(lang,j['slug'])
            assert j['stages'][0][loc] == narrative[0].get_text('',strip=False),(lang,j['slug'],'missing narrative translation')
# Editorial acceptance for the four requested journey changes, all five languages.
by_slug = {j['slug']: j for j in J}
assert all('documents' in by_slug['reunion-from-flight-to-memory']['stages'][2][0].lower() for _ in [0])
assert 'themes' in by_slug['anniversary-across-the-ocean']['features']
assert 'Automatic seasonal appearance' in by_slug['anniversary-across-the-ocean']['stages'][3][0]
assert 'exact location' in by_slug['the-apartment-before-the-move']['stages'][1][0]
assert 'memories' in by_slug['her-family-celebration-from-afar']['features']
assert '22 available layouts' in by_slug['her-family-celebration-from-afar']['stages'][2][0]
assert 'PDF' in by_slug['her-family-celebration-from-afar']['stages'][4][0]
for locale_index in range(5):
    assert 'PDF' in by_slug['her-family-celebration-from-afar']['stages'][4][locale_index]
    assert '22' in by_slug['her-family-celebration-from-afar']['stages'][2][locale_index]
comparison=(ROOT/'compare.html').read_text(encoding='utf8')
tutorials=(ROOT/'tutorials.html').read_text(encoding='utf8')
assert 'the-sofa-decision' not in comparison
assert 'sofa-that-both-of-us-chose' in comparison
assert 'course-together-across-time-zones' in comparison
assert 'reunion-from-flight-to-memory' in tutorials
print('PASS: 30 complete journeys (12 apart, 12 together, 6 solo), contextual feature links, clean expand/collapse icons, five-language parity.')
