"""Non-destructive website security and search-discovery regression checks."""
from pathlib import Path
from bs4 import BeautifulSoup
import re

ROOT=Path(__file__).resolve().parents[1]
MAIN=['index.html','join.html','support.html','faq.html','scenarios.html',
      'living-together.html','long-distance.html','compare.html','tutorials.html']
LANGS=('en','ar','es','fr','de')
for lang in LANGS:
    prefix='' if lang=='en' else lang+'/'
    for page in MAIN:
        html=(ROOT/prefix/page).read_text(encoding='utf-8')
        soup=BeautifulSoup(html,'html.parser')
        title=soup.title
        assert title and title.get_text(strip=True), (lang,page,'title')
        canonical=soup.find('link',rel='canonical')
        assert canonical and canonical.get('href','').startswith('https://onespace.live/'), (lang,page,'canonical')
        alternate={a.get('hreflang') for a in soup.find_all('link',rel='alternate')}
        assert set(LANGS).issubset(alternate), (lang,page,'hreflang parity')
        assert soup.html.get('lang')==lang, (lang,page,'wrong locale')
        assert soup.find('meta',attrs={'name':'referrer'}), (lang,page,'referrer policy')
        csp=soup.find('meta',attrs={'http-equiv':'Content-Security-Policy'})
        assert csp and "object-src 'none'" in csp.get('content',''), (lang,page,'CSP')
        for a in soup.select('a[target="_blank"]'):
            assert 'noopener' in a.get('rel',[]), (lang,page,'external link opener access')
        assert not re.search(r'(?i)sb_secret_|SUPABASE_SERVICE_ROLE_KEY',html), (lang,page,'privileged key reference')
    home=(ROOT/prefix/'index.html').read_text(encoding='utf-8')
    assert 'id="reviews-preview"' not in home and 'data-testimonial-carousel' not in home, (lang,'fake reviews exposed')
    for sensitive in ('confirm.html','unsubscribe.html'):
        txt=(ROOT/prefix/sensitive).read_text(encoding='utf-8')
        assert 'noindex' in txt, (lang,sensitive,'indexing')
src=(ROOT/'backend/founders/functions/_lib.ts').read_text(encoding='utf-8')
assert "return ok === true ? 'ok' : 'blocked'" in src, 'Turnstile must fail closed'
assert "j.hostname === 'onespace.live'" in src, 'Turnstile hostname binding absent'
assert "turnstile_unavailable === true" not in src, 'unverified token bypass'
assert "const fast =" not in src, 'client timing should not bypass checks'
js=(ROOT/'assets/os.js').read_text(encoding='utf-8')
assert "turnstile_unavailable: true" not in js, 'frontend captcha bypass'
assert "$$('form[data-form]').forEach" in js, 'multi-form handler missing'
index=(ROOT/'index.html').read_text(encoding='utf-8')
assert '"aggregateRating"' not in index and 'class="store-rating-row"' not in index
assert '"price": "0"' not in index and "'price': '0'" not in index, 'unconfirmed pricing in structured data'
sitemap=(ROOT/'sitemap.xml').read_text(encoding='utf-8')
for lang in LANGS:
    prefix='' if lang=='en' else lang+'/'
    assert '<loc>https://onespace.live/'+prefix+'scenarios.html</loc>' in sitemap, (lang,'missing scenarios')
print('PASS: public web security controls, hidden reviews, safe links, 5-language SEO parity, no unconfirmed price')
