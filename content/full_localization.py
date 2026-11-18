"""Locale-preserving translation layer for the canonical OneSpace page generator.

Every translated page is built from the exact original English DOM. No reduced
templates, no missing tutorials, demo cards, screenshot assets or theme controls.
JSON translations are committed; a release NEVER calls a translation service.
"""
import json
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from bs4 import BeautifulSoup, NavigableString, Doctype, Comment, ProcessingInstruction, CData

LANGS = ('en', 'ar', 'es', 'fr', 'de')
NEW_LANGS = ('es', 'fr', 'de')
INERT = {'script', 'style', 'svg', 'code', 'pre', 'textarea'}
ATTRS = ('title', 'alt', 'placeholder', 'aria-label')
SKIP = re.compile(r'^(?:[\W_0-9]+|[A-Za-z0-9.+-]+@[A-Za-z0-9.-]+|(?:https?://|www\.)\S+)$', re.UNICODE)
BASE = 'https://onespace.live/'
NAME = {'es':'Español', 'fr':'Français', 'de':'Deutsch'}
FORM_MESSAGES = {
 'es':{'sending':'Enviando…','missing':'Completa los campos obligatorios.','email':'Comprueba tu correo electrónico.','consent':'Marca la casilla para recibir nuestros correos.','busy':'Demasiados intentos; inténtalo de nuevo en unos minutos.','failed':'No se ha podido enviar. Comprueba la conexión y vuelve a intentarlo.','verify':'Un momento: necesitamos comprobar que eres una persona.','verify_failed':'No se ha podido completar la comprobación; vuelve a cargar la página.','sent':'Gracias. Hemos recibido tu mensaje y te responderemos por correo.'},
 'fr':{'sending':'Envoi en cours…','missing':'Merci de remplir les champs obligatoires.','email':'Vérifiez votre adresse e-mail.','consent':'Cochez la case pour recevoir nos e-mails.','busy':'Trop de tentatives. Réessayez dans quelques minutes.','failed':'Envoi impossible. Vérifiez votre connexion et réessayez.','verify':'Un instant : nous devons vérifier que vous êtes une personne.','verify_failed':'La vérification a échoué. Actualisez la page.','sent':'Merci. Nous avons reçu votre message et vous répondrons par e-mail.'},
 'de':{'sending':'Wird gesendet…','missing':'Bitte fülle die Pflichtfelder aus.','email':'Bitte überprüfe deine E-Mail-Adresse.','consent':'Bitte stimme dem E-Mail-Empfang zu.','busy':'Zu viele Versuche. Bitte versuche es in einigen Minuten erneut.','failed':'Senden fehlgeschlagen. Bitte überprüfe deine Verbindung und versuche es erneut.','verify':'Einen Moment: Wir prüfen kurz, ob du ein Mensch bist.','verify_failed':'Die Überprüfung ist fehlgeschlagen. Bitte lade die Seite neu.','sent':'Danke! Wir haben deine Nachricht erhalten und antworten per E-Mail.'}
}
SITE_MESSAGES = {
  "es": {
    "kit.copied": "Copiado",
    "share.text": "Me gustaría que probáramos OneSpace: un espacio privado para nuestros planes, gestos de cariño y recuerdos.",
    "founders.invite-copied": "Enlace copiado",
    "password.show": "Mostrar contraseña",
    "password.hide": "Ocultar contraseña"
  },
  "fr": {
    "kit.copied": "Copié",
    "share.text": "J’aimerais qu’on essaie OneSpace : un espace privé pour nos projets, nos petites attentions et nos souvenirs.",
    "founders.invite-copied": "Lien copié",
    "password.show": "Afficher le mot de passe",
    "password.hide": "Masquer le mot de passe"
  },
  "de": {
    "kit.copied": "Kopiert",
    "share.text": "Ich würde gern OneSpace mit dir ausprobieren: einen privaten Ort für unsere Pläne, kleinen Liebesgesten und Erinnerungen.",
    "founders.invite-copied": "Link kopiert",
    "password.show": "Passwort anzeigen",
    "password.hide": "Passwort verbergen"
  }
}

MAIL_LANGUAGE_HINT = {
    'es':'Por ahora, los correos de confirmación y acceso anticipado se envían en inglés o árabe.',
    'fr':'Pour le moment, les e-mails de confirmation et d’accès anticipé sont envoyés en anglais ou en arabe.',
    'de':'Bestätigungs- und Frühzugangs-E-Mails werden derzeit auf Englisch oder Arabisch versendet.'
}

GLOSSARY = {
 'es': {'Today':'Hoy','Remember':'Recordar','Coordinate':'Organizar','Connect':'Conectar','Me':'Yo','Home':'Inicio',
        'Features':'Funciones','Demo':'Demostración','Tutorials':'Tutoriales','Guides':'Guías','FAQ':'Preguntas frecuentes',
        'Join the Founding 500':'Únete a los primeros 500 miembros fundadores','Founding 500':'500 miembros fundadores',
        'Our places':'Nuestros lugares','Counters':'Contadores de días','The Founding 500':'Los 500 miembros fundadores',
        'Living apart':'Vivir a distancia','Living together':'Vivir juntos','A little love':'Un poquito de cariño',
        'Shared experiences':'Experiencias compartidas','Contact cards':'Fichas de contactos','Our memories':'Nuestros recuerdos',
        'Our story':'Nuestra historia','Privacy policy':'Política de privacidad','Terms of use':'Condiciones de uso',
        'Email *':'Correo electrónico *','Your phone':'Tu teléfono','Your first name':'Tu nombre','Language':'Idioma',
        'Get the app':'Consigue la app','Where visits come from':'Origen de las visitas'},
 'fr': {'Today':"Aujourd’hui",'Remember':'Se souvenir','Coordinate':'Organiser','Connect':'Échanger','Me':'Moi','Home':'Accueil',
        'Features':'Fonctionnalités','Demo':'Démo','Tutorials':'Tutoriels','Guides':'Guides','FAQ':'Questions fréquentes',
        'Join the Founding 500':'Rejoindre les 500 premiers membres fondateurs','Founding 500':'500 membres fondateurs',
        'Our places':'Nos lieux','Counters':'Compteurs de jours','The Founding 500':'Les 500 membres fondateurs',
        'Living apart':'Vivre à distance','Living together':'Vivre ensemble','A little love':"Une petite attention",
        'Shared experiences':'Expériences partagées','Contact cards':'Fiches de contact','Our memories':'Nos souvenirs',
        'Our story':'Notre histoire','Privacy policy':'Politique de confidentialité','Terms of use':"Conditions d’utilisation",
        'Email *':'E-mail *','Your phone':'Votre téléphone','Your first name':'Votre prénom','Language':'Langue',
        'Get the app':"Découvrir l’application"},
 'de': {'Today':'Heute','Remember':'Merken','Coordinate':'Planen','Connect':'Verbinden','Me':'Ich','Home':'Startseite',
        'Features':'Funktionen','Demo':'Demo','Tutorials':'Anleitungen','Guides':'Ratgeber','FAQ':'Häufige Fragen',
        'Join the Founding 500':'Zu den ersten 500 Gründungsmitgliedern gehören','Founding 500':'500 Gründungsmitglieder',
        'Our places':'Unsere Orte','Counters':'Tageszähler','The Founding 500':'Die 500 Gründungsmitglieder',
        'Living apart':'Getrennt leben','Living together':'Zusammenleben','A little love':'Eine kleine Liebesgeste',
        'Shared experiences':'Gemeinsame Erlebnisse','Contact cards':'Kontaktkarten','Our memories':'Unsere Erinnerungen',
        'Our story':'Unsere Geschichte','Privacy policy':'Datenschutzerklärung','Terms of use':'Nutzungsbedingungen',
        'Email *':'E-Mail *','Your phone':'Dein Handy','Your first name':'Dein Vorname','Language':'Sprache',
        'Get the app':'App entdecken'}
}

from locale_editorial import CURATED
from locale_menu import MENU_EDITORIAL
from locale_legal_review import LEGAL_EDITORIAL
from locale_faq_review import FAQ_EDITORIAL
from locale_guides_review import GUIDE_EDITORIAL
from launch_enrichment import EXTRA_TRANSLATIONS
from journeys_apart_01 import JOURNEYS as JA1
from journeys_apart_02 import JOURNEYS as JA2
from journeys_together_01 import JOURNEYS as JT1
from journeys_together_02 import JOURNEYS as JT2
from journeys_ui import UI as JOURNEY_UI, FEATURES as JOURNEY_FEATURES
from faq_additions import FAQ_ADDITIONS
from tutorial_additions import TUTORIAL_ADDITIONS
from tutorial_journeys import JOURNEY_TUTORIAL_ADDITIONS, JOURNEY_LABEL
from guide_additions_1 import GUIDE_ADDITIONS_1
from guide_additions_2 import GUIDE_ADDITIONS_2
for _locale in NEW_LANGS:
    GLOSSARY[_locale].update(CURATED[_locale])
    GLOSSARY[_locale].update(MENU_EDITORIAL[_locale])
    GLOSSARY[_locale].update(LEGAL_EDITORIAL[_locale])
    GLOSSARY[_locale].update(FAQ_EDITORIAL[_locale])
    GLOSSARY[_locale].update(GUIDE_EDITORIAL[_locale])
    GLOSSARY[_locale].update(EXTRA_TRANSLATIONS[_locale])

# Preserve every paragraph of all 24 journeys in each indexable locale,
# not a shorter foreign-language version of the storytelling experience.
for _j in JA1 + JA2 + JT1 + JT2:
    for _entry in [_j['title'], _j['teaser'], *_j['stages']]:
        for _index, _language in enumerate(('es', 'fr', 'de'), 2):
            GLOSSARY[_language][_entry[0]] = _entry[_index]
for _entry in list(JOURNEY_UI.values()) + list(JOURNEY_FEATURES.values()):
    for _index, _language in enumerate(('es', 'fr', 'de'), 2):
        GLOSSARY[_language][_entry[0]] = _entry[_index]

# All additional long-form FAQ, tutorial, and guide copy must be provided in
# every shipped website language; no machine translation or English fallback.
for _locale_index, _locale in enumerate(('es','fr','de'), 2):
    _lex = GLOSSARY[_locale]
    def _add(entry):
        if entry[0] != entry[_locale_index]:
            _lex[entry[0]] = entry[_locale_index]
    for _entries in FAQ_ADDITIONS.values():
        for _q, _answer in _entries:
            _add(_q)
            _add(_answer)
    for _items in [*TUTORIAL_ADDITIONS.values(), *JOURNEY_TUTORIAL_ADDITIONS.values()]:
        for _tutorial in _items:
            _add(_tutorial['t'])
            for _step in _tutorial['steps']:
                # HTML link inside a translated step is segmented into two
                # text nodes by BeautifulSoup; translate both pieces exactly.
                if '<a href=' in _step[0]:
                    _src_parts = [str(s) for s in BeautifulSoup(_step[0], 'html.parser').stripped_strings]
                    _dst_parts = [str(s) for s in BeautifulSoup(_step[_locale_index], 'html.parser').stripped_strings]
                    if len(_src_parts) != len(_dst_parts):
                        raise RuntimeError('Localized tutorial link segments mismatch')
                    for _source, _translated in zip(_src_parts, _dst_parts):
                        _lex[_source] = _translated
                else:
                    _add(_step)
    _add(JOURNEY_LABEL)
    _add(['Explore 9 more practical guides',
          'استكشف 9 أدلة عملية أخرى',
          'Explora otras 9 guías prácticas',
          'Découvrez 9 autres guides pratiques',
          'Entdecke 9 weitere praktische Ratgeber'])
    for _guide in GUIDE_ADDITIONS_1 + GUIDE_ADDITIONS_2:
        for _field in ('title','desc','intro','how'):
            _add(_guide[_field])
        for _heading, _tips in _guide['sections']:
            _add(_heading)
            for _tip in _tips:
                _add(_tip)

def eligible(raw):
    s = str(raw).strip()
    return bool(s and len(s) > 1 and re.search(r'[A-Za-z]', s) and not SKIP.fullmatch(s)
                and s not in ('OneSpace', 'Android', 'iPhone', 'Google Play', 'App Store', 'TestFlight',
                              'WhatsApp', 'Telegram', 'Facebook', 'Instagram', 'YouTube', 'PDF', 'PNG', '© OneSpace',
                              'Omar', 'Lina', 'English', 'العربية', 'Español', 'Français', 'Deutsch'))

def content_nodes(soup):
    for node in list(soup.find_all(string=True)):
        if isinstance(node, (Doctype, Comment, ProcessingInstruction, CData)):
            continue  # Never translate the HTML doctype into visible text (e.g. 'HTML').
        if any(p.name in INERT for p in node.parents):
            continue
        # The product wordmark is deliberately in English in every locale.
        if any('brand-name' in p.get('class', []) for p in node.parents):
            continue
        # Social icons and named social networks are visual identity marks.
        if any('footer-social-item' in p.get('class', []) for p in node.parents):
            continue
        if eligible(node):
            yield node

def catalog_for_pages(pages, root):
    catalog = {}
    for page in pages:
        soup = BeautifulSoup((root / page).read_text(encoding='utf-8'), 'html.parser')
        for text_node in content_nodes(soup):
            raw = str(text_node).strip()
            catalog[raw] = catalog.get(raw, 0) + 1
        for el in soup.find_all(True):
            if el.name in INERT:
                continue
            for a in ATTRS:
                value = el.get(a)
                if value and eligible(value):
                    catalog[value] = catalog.get(value, 0) + 1
        for tag in soup.find_all('meta'):
            if tag.get('name') == 'description':
                value = tag.get('content','')
                if eligible(value):
                    catalog[value] = catalog.get(value, 0) + 1
    return dict(sorted(catalog.items()))

def translations_for(root, locale):
    file = root / 'content' / 'translations' / (locale + '.json')
    if not file.exists():
        raise RuntimeError('Missing committed reviewed translation catalogue: '+str(file))
    return json.loads(file.read_text(encoding='utf-8'))

def localized_path(name, locale):
    return BASE+locale+'/' + ('' if name == 'index.html' else name)

def root_href(path, locale):
    if not path or path.startswith(('#','//','mailto:','tel:','javascript:','data:')):
        return path
    u=urlsplit(path)
    if u.scheme or u.netloc:
        return path
    p=u.path
    if not p and (u.query or u.fragment):
        return path  # Preserve same-page support links such as ?topic=signin#contact.
    if p.startswith('/assets/') or p in ('/site.webmanifest', '/sitemap.xml'):
        return path
    if p.startswith('assets/'):
        target='/'+p
    elif p in ('site.webmanifest', 'sitemap.xml'):
        target='/'+p
    elif p.startswith('/'):
        target='/'+locale+p
    else:
        target='/'+locale+'/'+p
    return urlunsplit(('', '', target, u.query, u.fragment))

def localize_html(src, name, locale, translated):
    soup=BeautifulSoup(src,'html.parser')
    # Translate bold-emphasis legal sentences as complete clauses: machine
    # translation of "We do <b>not</b> collect ..." made nonsensical fragments.
    privacy_no_collect = None
    if name == 'privacy.html':
        for paragraph in soup.select('.legal p'):
            if paragraph.get_text(' ', strip=True).startswith('We do not collect'):
                privacy_no_collect = paragraph
                break
        if privacy_no_collect is None:
            raise RuntimeError('Privacy policy noncollection clause missing')
    missing=set()
    def tr(s):
        if not eligible(s): return s
        result=GLOSSARY.get(locale,{}).get(s) or translated.get(s)
        if result is None or not isinstance(result,str) or not result.strip():
            missing.add(s)
            return s
        return result
    for node in content_nodes(soup):
        text=str(node)
        stripped=text.strip()
        result=tr(stripped)
        if result != stripped:
            start=len(text)-len(text.lstrip())
            end=len(text)-len(text.rstrip())
            node.replace_with(NavigableString(text[:start]+result+(text[len(text)-end:] if end else '')))
    for el in soup.find_all(True):
        if el.name not in INERT:
            for key in ATTRS:
                if el.has_attr(key) and eligible(el[key]):
                    el[key]=tr(el[key])
    for m in soup.find_all('meta'):
        if m.get('name')=='description':
            m['content']=tr(m.get('content',''))
    if privacy_no_collect is not None:
        legal_clause = {
          'es': '<p><b>No recopilamos</b> tu ubicación, tus contactos, tu historial de llamadas, tu actividad de navegación ni identificadores publicitarios. Si eliges un contacto o un calendario en tu teléfono, esa selección se realiza en el dispositivo; solo almacenamos lo que guardas en OneSpace.</p>',
          'fr': '<p>Nous ne recueillons <b>pas</b> votre position, vos contacts, votre historique d’appels, votre navigation ni vos identifiants publicitaires. Lorsque vous sélectionnez un contact ou un calendrier sur votre téléphone, l’opération reste sur l’appareil ; seules les informations enregistrées dans OneSpace sont conservées.</p>',
          'de': '<p>Wir erfassen <b>keine</b> Standortdaten, Kontakte, Anruflisten, Browserverläufe oder Werbe-IDs. Wenn du auf deinem Smartphone einen Kontakt oder Kalender auswählst, erfolgt dies auf dem Gerät. Gespeichert wird nur, was du in OneSpace übernimmst.</p>'
        }
        privacy_no_collect.replace_with(BeautifulSoup(legal_clause[locale], 'html.parser').p)
    if missing:
        sample=' | '.join(sorted(missing)[:15])
        raise RuntimeError(f'Missing {locale} translations in {name}: {len(missing)} entries: {sample}')
    html=soup.find('html');html['lang']=locale;html['dir']='ltr'
    canonical=localized_path(name,locale)
    head=soup.head
    for a in list(head.find_all('link',rel='alternate')):
        a.decompose()
    for code in LANGS:
        link=soup.new_tag('link',rel='alternate',hreflang=code)
        link['href']=BASE+ ('' if code=='en' else code+'/') + ('' if name=='index.html' else name)
        head.append(link)
    link=soup.new_tag('link',rel='alternate',hreflang='x-default')
    link['href']=BASE + ('' if name=='index.html' else name)
    head.append(link)
    c=head.find('link',rel='canonical')
    if c:c['href']=canonical
    for p,value in (('og:title',soup.title.get_text(strip=True) if soup.title else None),
                    ('og:description',head.find('meta',attrs={'name':'description'}).get('content') if head.find('meta',attrs={'name':'description'}) else None),
                    ('og:url',canonical),('og:locale',locale)):
        tag=head.find('meta',attrs={'property':p})
        if not tag:
            tag=soup.new_tag('meta')
            tag['property']=p
            head.append(tag)
        if value:tag['content']=value
    for el in soup.find_all(True):
        if el.name in ('a','link'):
            if el.get('href'):el['href']=root_href(el['href'],locale)
        for attr in ('src','poster','data-ar-src','data-en-src','data-ar-poster','data-en-poster'):
            if el.get(attr):el[attr]=root_href(el[attr],locale)
        if el.name=='script' and el.get('data-goatcounter'):
            # GoatCounter's script URL belongs to an external analytics provider.
            pass
        if el.name=='form' and el.get('data-form')=='join':
            # The existing Founder backend currently sends English/Arabic emails only.
            # Keep English as the email preference until localized email templates exist.
            inp=el.find('input',attrs={'name':'language'})
            if inp:inp['value']='en'
            chooser=el.find('select',attrs={'name':'language'})
            if chooser:
                hint=soup.new_tag('p')
                hint['class']='muted'
                hint['style']='font-size:12px;margin-top:6px'
                hint.string=MAIL_LANGUAGE_HINT[locale]
                chooser.insert_after(hint)
    # Browser dynamic feedback uses the same localized language as the visible form.
    bootstrap=soup.new_tag('script')
    bootstrap.string=('window.ONESPACE_FORM_MESSAGES='+json.dumps(FORM_MESSAGES[locale],ensure_ascii=False)+';'
                      'window.ONESPACE_SITE_STRINGS='+json.dumps(SITE_MESSAGES[locale],ensure_ascii=False)+';')
    head.append(bootstrap)
    for link in soup.select('[data-language-switch]'):
        other=link.get('data-language-switch')
        if other in LANGS:
            link['href']=BASE+('' if other=='en' else other+'/')+('' if name=='index.html' else name)
            if other==locale:link['aria-current']='page'
            else:link.attrs.pop('aria-current',None)
    output=str(soup)
    # Browser URLs in srcset and inline CSS must still resolve from nested /es/, /fr/, /de/ paths.
    output=re.sub(r'(?<![A-Za-z0-9/])assets/', '/assets/', output)
    if not output.lstrip().lower().startswith('<!doctype html>'):
        raise RuntimeError(f'Localized page {locale}/{name} lost its HTML5 doctype')
    return output

def build_locales(root, pages):
    for lang in NEW_LANGS:
        data=translations_for(root,lang)
        folder=root/lang
        folder.mkdir(exist_ok=True)
        for page in pages:
            source=(root/page).read_text(encoding='utf-8')
            (folder/page).write_text(localize_html(source,page,lang,data),encoding='utf-8')
    return len(pages)*len(NEW_LANGS)
