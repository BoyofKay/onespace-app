#!/usr/bin/env python3
"""Regression checks for reviewed website legal, FAQ and relationship guide translations."""
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
import json
import sys
sys.path.insert(0, str(ROOT / 'content'))
from locale_legal_review import LEGAL_EDITORIAL
from locale_faq_review import FAQ_EDITORIAL
from faq_master import web_groups as _faq_web_groups
from locale_guides_review import GUIDE_EDITORIAL
# 27 Nov 2026: the FAQ is content/faq/*.json (website items) plus the website-only Founder group.
def _expected_faq_total():
    en=BeautifulSoup((ROOT/'faq.html').read_text(encoding='utf8'),'html.parser')
    total=len(en.select('details[data-faq]'))
    web=sum(len(g['items']) for g in _faq_web_groups())
    # 27 Nov 2026 (owner): only the shared FAQ; no Founder Members group.
    assert total==web and not en.select('#founders'),(total,web)
    return total
EXPECTED_FAQ=_expected_faq_total()

catalog = json.loads((ROOT / 'content' / 'translations' / 'source_catalog.json').read_text(encoding='utf8'))
for language in ('es', 'fr', 'de'):
  for name, corrections in [('privacy/terms', LEGAL_EDITORIAL[language]),
                             ('FAQ', FAQ_EDITORIAL[language]),
                             ('guides', GUIDE_EDITORIAL[language])]:
    unused = [key for key in corrections if key not in catalog]
    assert not unused, f'{language}: {name} review refers to nonexistent source strings: {unused[:5]}'

CHECKS = {
  'es': {
    'privacy': ['Qué datos recopilamos','No recopilamos','60 días','180 días','siete días',
                'privacy@onespace.live', 'founders@onespace.live', 'unsubscribe'],
    'terms': ['18 años','contenido','elementos compartidos','OneSpace'],
    'account': ['Me → Your data and account', 'Correo de tu cuenta', 'privacy@onespace.live'],
    'faq': ['unidireccional', 'Google'],  # Founder questions removed 27 Nov 2026
    'guide': ['Respeten los horarios del otro', 'Compartan también lo cotidiano'],
  },
  'fr': {
    'privacy': ['Quelles données recueillons-nous ?', 'Nous ne recueillons pas',
                '60 jours','180 jours','sept jours','privacy@onespace.live','founders@onespace.live','unsubscribe'],
    'terms': ['18 ans','contenus','Partagé','OneSpace'],
    'account': ['Me → Your data and account', 'Adresse e-mail du compte', 'privacy@onespace.live'],
    'faq': ['un seul sens', 'Google'],
    'guide': ['Respecter le rythme de l’autre', 'Partager aussi le quotidien'],
  },
  'de': {
    'privacy': ['Welche Daten wir erfassen', 'Wir erfassen keine','60 Tagen','180 Tagen',
                'sieben Tage','privacy@onespace.live','founders@onespace.live','unsubscribe'],
    'terms': ['18 Jahre','Inhalte','Geteilt','OneSpace'],
    'account': ['Me → Your data and account', 'E-Mail-Adresse deines Kontos', 'privacy@onespace.live'],
    'faq': ['nur in eine Richtung','Google'],
    'guide': ['Nehmt Rücksicht auf eure Tageszeiten', 'Teilt auch die alltäglichen Dinge'],
  },
}
for lang, paths in CHECKS.items():
  for category, phrases in paths.items():
    relative = {
      'privacy': 'privacy.html',
      'terms': 'terms.html',
      'faq': 'faq.html',
      'guide': 'guide-long-distance-ideas.html',
      'account': 'delete-account.html'
    }[category]
    page = ROOT / lang / relative
    assert page.exists(), page
    soup = BeautifulSoup(page.read_text(encoding='utf8'), 'html.parser')
    content = soup.get_text(' ',strip=True)
    for phrase in phrases:
      assert phrase in content, f'{page}: missing reviewed copy {phrase!r}'
    if category == 'privacy':
      assert content.count('60') >= 1 and content.count('180') >= 1 and content.count('7') >= 1, page
      assert 'mailto:privacy@onespace.live' in page.read_text(), page
      assert soup.find('b', string=lambda s: bool(s and s.strip().lower() in
                           {'no recopilamos','pas','keine'})), f'{page}: legally vital negative emphasis lost'
    if category == 'faq':
      assert len(soup.select('details[data-faq]')) == EXPECTED_FAQ, f'{page}: FAQ coverage'
  # Critical untranslated or dangerously mistranslated legal fragments must never return.
  privacy = (ROOT/lang/'privacy.html').read_text(encoding='utf8')
  banned = {
    'es':['nosotros hacemos <b>no</b>', 'mostradores', 'cheques, nunca'],
    'fr':['Nous faisons <b>pas</b>', 'They are deleted after 60 days', 'comptoirs'],
    'de':['Das tun wir <b>nicht</b>', 'Schecks durch', 'Schalter.</li>']
  }[lang]
  for expression in banned:
    assert expression not in privacy, f'Outdated {lang} mistranslation reappeared: {expression}'
print('PASS: reviewed legal/FAQ/guides source-key coverage and translated UI assertions for ES, FR, DE.')
