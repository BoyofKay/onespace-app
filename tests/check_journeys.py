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
J=A1+A2+T1+T2
assert len(J)==24,len(J)
assert sum(j['mode']=='apart' for j in J)==12
assert sum(j['mode']=='together' for j in J)==12
assert len({j['slug'] for j in J})==24
for j in J:
    assert 4<=len(j['stages'])<=7,(j['slug'],len(j['stages']))
    assert sum(len(stage[0].split()) for stage in j['stages'])>=200,j['slug']
    assert len(j['features'])>=4,j['slug']
    for v in [j['title'],j['teaser'],*j['stages']]:
        assert len(v)==5 and all(v),j['slug']
        assert not v[0].startswith(('INT.','CUT TO:','EXT.','SCENE ')),j['slug']
for lang in ('en','ar','es','fr','de'):
    prefix='' if lang=='en' else lang+'/'
    html=(ROOT/prefix/'scenarios.html').read_text(encoding='utf8')
    doc=BeautifulSoup(html,'html.parser')
    assert len(doc.select('details.journey-episode'))==24,lang
    assert not doc.select('div.story-scene'),lang
    for mode,slug in [('apart','long-distance.html'),('together','living-together.html')]:
        mode_page=BeautifulSoup((ROOT/prefix/slug).read_text(encoding='utf8'),'html.parser')
        assert len(mode_page.select('a.journey-preview'))==12,(lang,mode)
        assert len(mode_page.select('details.journey-show-more'))==1,(lang,mode)
        assert mode_page.select_one('details.journey-show-more summary'),(lang,mode)
    for j in J:
        ep=doc.select_one('#story-'+j['slug'])
        assert ep is not None,(lang,j['slug'])
        assert len(ep.select('.journey-beat'))==len(j['stages']),(lang,j['slug'])
        assert len(ep.select('.journey-feature-chip'))==len(j['features']),(lang,j['slug'])
        if lang in ('en','ar'):
            body=ep.get_text(' ',strip=True)
            assert j['title'][0 if lang=='en' else 1] in body,(lang,j['slug'])
        elif lang in ('es','fr','de'):
            body=ep.get_text(' ',strip=True)
            loc=('es','fr','de').index(lang)+2
            assert j['title'][loc] in body,(lang,j['slug'])
            assert j['stages'][0][loc] in body,(lang,j['slug'],'missing narrative translation')
comparison=(ROOT/'compare.html').read_text(encoding='utf8')
tutorials=(ROOT/'tutorials.html').read_text(encoding='utf8')
assert 'the-sofa-decision' not in comparison
assert 'sofa-that-both-of-us-chose' in comparison
assert 'course-together-across-time-zones' in comparison
assert 'reunion-from-flight-to-memory' in tutorials
print('PASS: 24 complete journeys, 12 apart + 12 together, deep-link previews, all five languages, no screenplay layout.')
