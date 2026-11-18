from pathlib import Path
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
required={'mega-features':{'features.html','smart-sharing.html','decide-together.html','trips.html',
    'everyday.html','occasions.html','watchlists.html','memories.html','compare.html'},
 'mega-couples':{'long-distance.html','living-together.html'},
 'mega-learn':{'guides.html','tutorials.html','faq.html','whats-new.html'}}
for locale in ('en','ar','es','fr','de'):
    prefix='' if locale=='en' else locale+'/'
    page=ROOT/prefix/'index.html'
    soup=BeautifulSoup(page.read_text(encoding='utf8'),'html.parser')
    panel_ids={p.get('id') for p in soup.select('.drop-panel.mega-panel')}
    assert panel_ids==set(required), (locale,panel_ids)
    for pid,links in required.items():
        panel=soup.select_one('#'+pid)
        assert panel, (locale,pid)
        assert panel.select_one('.mega-intro'), (locale,pid,'missing intro')
        assert panel.select_one('.mega-section'), (locale,pid,'missing groups')
        assert not panel.select('.e, .card, img, [class*="icon"]'), (locale,pid,'old icon tiles')
        all_links=[a.get('href','') for a in panel.select('a')]
        for target in links:
            expected=('/'+locale+'/'+target if locale in ('es','fr','de') else
                      target if locale=='en' else '/ar/'+target)
            assert expected in all_links or target in all_links, (locale,pid,target,all_links)
    assert len(soup.select('.mega-panel .mega-link'))==14, locale
    assert not soup.select('.mega-panel .mega-link .e'), locale
    # Keep the real page body, not a miniature landing page.
    assert len(soup.select('img'))>=3,locale

css=(ROOT/'assets/os.css').read_text(encoding='utf8')
for phrase in ('font-size:12.75px!important','font-size:10.5px!important','border-inline-end',
               '.mega-intro','.mega-link-copy','@media (max-width:1250px)'):
    assert phrase in css,phrase
print('PASS: full five-language mega menu parity, destination links, no icon cards, restrained typography.')
