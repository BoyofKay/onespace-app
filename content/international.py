"""Fully localized, indexable international landing pages.
Not a machine-translated copy of untranslated secondary pages. All visible page
copy and the signup flow are translated. Deep editorial pages remain en/ar.
"""
import html
import json
from pathlib import Path

LOCALES = {
  "es": {
    "label": "Español",
    "title": "OneSpace — La app privada para parejas",
    "description": "Organiza planes, recuerdos, viajes, fechas importantes y pequeños gestos con tu pareja, viváis juntos o a distancia.",
    "home": "Inicio",
    "features": "Funciones",
    "how": "Cómo funciona",
    "founders": "Acceso anticipado",
    "hero": "Dos personas. Una vida compartida. Un solo espacio.",
    "lead": "Tus planes, fechas importantes, viajes, recuerdos y pequeños gestos de cariño, organizados en un espacio privado para los dos.",
    "try": "Descubre las funciones",
    "join": "Únete a los 500 miembros fundadores",
    "eyebrow": "CREADO PARA DOS",
    "featuresTitle": "Más tiempo juntos. Menos detalles perdidos.",
    "featureData": [
      [
        "📅",
        "El día a día",
        "Un calendario compartido, listas, tareas, notas y recordatorios para saber qué viene después."
      ],
      [
        "🧭",
        "Decidir juntos",
        "Comparad opciones, precios y opiniones, conversad y guardad lo que hayáis decidido."
      ],
      [
        "✈️",
        "Viajes compartidos",
        "Organizad vuelos, reservas, itinerarios y listas de equipaje desde un mismo lugar."
      ],
      [
        "🎁",
        "Fechas especiales",
        "Prepara cumpleaños, aniversarios y sorpresas con ideas, presupuesto y recordatorios."
      ],
      [
        "♡",
        "Pequeños gestos",
        "Envía una muestra de cariño, escribe cartas y compartid cómo os sentís."
      ],
      [
        "📸",
        "Nuestros recuerdos",
        "Guardad fotos, historias, lugares visitados y recuerdos en álbumes compartidos."
      ]
    ],
    "modesTitle": "Cerca o lejos, OneSpace se adapta a vosotros.",
    "apart": "Si vivís lejos",
    "apartText": "Dos zonas horarias, una fecha para el próximo encuentro y un lugar para planear los momentos juntos.",
    "together": "Si vivís juntos",
    "togetherText": "Tareas, decisiones, celebraciones y recuerdos organizados sin que uno tenga que recordarlo todo.",
    "foundTitle": "Forma parte de los primeros 500 miembros fundadores",
    "foundLead": "Los primeros 250 pares de personas confirmadas reciben un número de fundador por pareja. La prueba inicial es gratuita; las ventajas futuras se anunciarán antes de fijar precios.",
    "email": "Correo electrónico",
    "phone": "¿Qué móvil usas?",
    "android": "Android",
    "iphone": "iPhone",
    "both": "Ambos",
    "unsure": "No lo sé todavía",
    "consent": "Acepto recibir por correo electrónico noticias sobre OneSpace y su lanzamiento.",
    "send": "Reservar mi plaza",
    "sentTitle": "Comprueba tu correo",
    "sentText": "Te hemos enviado un enlace de confirmación. Revisa también la carpeta de spam.",
    "privacy": "Privacidad (en inglés)",
    "legalNote": "Sin anuncios y sin vender datos personales. La aplicación para Android está preparando sus pruebas cerradas; la versión de iPhone está prevista para más adelante.",
    "support": "¿Tienes preguntas? Escríbenos a",
    "freesoon": "Acceso anticipado gratuito. Google Play y App Store aún no ofrecen una descarga pública.",
    "languages": "Idiomas",
    "messages": {
      "sending": "Enviando…",
      "missing": "Completa los campos obligatorios.",
      "email": "Comprueba tu correo electrónico.",
      "consent": "Marca la casilla para recibir nuestros correos.",
      "failed": "No se ha podido enviar. Vuelve a intentarlo.",
      "busy": "Demasiados intentos. Espera un poco.",
      "verify": "Una comprobación breve antes de continuar.",
      "verify_failed": "No se pudo completar la comprobación."
    }
  },
  "fr": {
    "label": "Français",
    "title": "OneSpace — L’application privée pour les couples",
    "description": "Organisez vos projets, souvenirs, voyages, dates importantes et petites attentions à deux, sous le même toit ou à distance.",
    "home": "Accueil",
    "features": "Fonctionnalités",
    "how": "Comment ça marche",
    "founders": "Accès anticipé",
    "hero": "Deux personnes. Une vie à partager. Un seul espace.",
    "lead": "Vos projets, vos dates importantes, vos voyages, vos souvenirs et vos petites attentions réunis dans un espace privé pour vous deux.",
    "try": "Découvrir les fonctionnalités",
    "join": "Rejoindre les 500 membres fondateurs",
    "eyebrow": "PENSÉ POUR DEUX",
    "featuresTitle": "Plus de temps à deux. Moins de détails oubliés.",
    "featureData": [
      [
        "📅",
        "Le quotidien",
        "Calendrier partagé, listes, tâches, notes et rappels : tout ce qui compte au même endroit."
      ],
      [
        "🧭",
        "Décider ensemble",
        "Comparez des options et des prix, échangez vos avis et conservez vos décisions."
      ],
      [
        "✈️",
        "Voyager ensemble",
        "Préparez vols, réservations, itinéraires et listes de bagages au même endroit."
      ],
      [
        "🎁",
        "Les grandes occasions",
        "Anticipez anniversaires et surprises avec des idées, un budget et des rappels."
      ],
      [
        "♡",
        "Les petites attentions",
        "Envoyez un mot tendre, écrivez des lettres et partagez votre humeur."
      ],
      [
        "📸",
        "Vos souvenirs",
        "Conservez photos, histoires et lieux visités dans des albums communs."
      ]
    ],
    "modesTitle": "Ensemble ou à distance, OneSpace suit votre rythme.",
    "apart": "Quand vous vivez à distance",
    "apartText": "Deux fuseaux horaires, la date de vos retrouvailles et un espace pour préparer vos moments ensemble.",
    "together": "Quand vous vivez ensemble",
    "togetherText": "Tâches, décisions, fêtes et souvenirs organisés sans que l’un de vous doive penser à tout.",
    "foundTitle": "Rejoignez les 500 premiers membres fondateurs",
    "foundLead": "Les 250 premiers couples confirmés reçoivent un numéro fondateur commun. L’accès initial est gratuit ; les avantages futurs seront annoncés avant toute tarification.",
    "email": "Adresse e-mail",
    "phone": "Quel téléphone utilisez-vous ?",
    "android": "Android",
    "iphone": "iPhone",
    "both": "Les deux",
    "unsure": "Je ne sais pas encore",
    "consent": "J’accepte de recevoir par e-mail les actualités de OneSpace et les informations de lancement.",
    "send": "Réserver ma place",
    "sentTitle": "Vérifiez votre boîte mail",
    "sentText": "Nous vous avons envoyé un lien de confirmation. Pensez aussi aux courriers indésirables.",
    "privacy": "Confidentialité (en anglais)",
    "legalNote": "Sans publicité ni vente de données personnelles. Les tests fermés Android sont en préparation ; une version iPhone est prévue.",
    "support": "Une question ? Écrivez-nous à",
    "freesoon": "Accès anticipé gratuit. Aucune version n’est encore disponible en téléchargement public sur les stores.",
    "languages": "Langues",
    "messages": {
      "sending": "Envoi en cours…",
      "missing": "Veuillez remplir les champs obligatoires.",
      "email": "Vérifiez votre adresse e-mail.",
      "consent": "Cochez la case pour recevoir nos e-mails.",
      "failed": "Impossible d’envoyer. Réessayez.",
      "busy": "Trop de tentatives. Réessayez un peu plus tard.",
      "verify": "Une courte vérification est nécessaire.",
      "verify_failed": "La vérification a échoué."
    }
  },
  "de": {
    "label": "Deutsch",
    "title": "OneSpace — Die private App für Paare",
    "description": "Gemeinsame Pläne, Erinnerungen, Reisen, wichtige Termine und kleine Liebesgesten – für Paare, die zusammen oder auf Distanz leben.",
    "home": "Startseite",
    "features": "Funktionen",
    "how": "So funktioniert’s",
    "founders": "Frühzugang",
    "hero": "Zwei Menschen. Ein gemeinsames Leben. Ein Raum.",
    "lead": "Eure Pläne, wichtigen Termine, Reisen, Erinnerungen und kleinen Liebesgesten – übersichtlich an einem privaten Ort für euch beide.",
    "try": "Funktionen entdecken",
    "join": "Zu den 500 Gründungsmitgliedern gehören",
    "eyebrow": "FÜR ZWEI GEMACHT",
    "featuresTitle": "Mehr Zeit füreinander. Weniger Dinge, die untergehen.",
    "featureData": [
      [
        "📅",
        "Gemeinsamer Alltag",
        "Kalender, Listen, Aufgaben, Notizen und Erinnerungen – alles an einem Ort."
      ],
      [
        "🧭",
        "Gemeinsam entscheiden",
        "Vergleicht Optionen und Preise, tauscht eure Meinungen aus und haltet Entscheidungen fest."
      ],
      [
        "✈️",
        "Reisen planen",
        "Flüge, Buchungen, Reisepläne und Packlisten gemeinsam organisieren."
      ],
      [
        "🎁",
        "Besondere Anlässe",
        "Geburtstage, Jahrestage und Überraschungen mit Ideen, Budget und Erinnerungen vorbereiten."
      ],
      [
        "♡",
        "Kleine Gesten",
        "Verschickt liebe Grüße, schreibt Briefe und teilt, wie ihr euch fühlt."
      ],
      [
        "📸",
        "Eure Erinnerungen",
        "Bewahrt Fotos, Geschichten und besuchte Orte in gemeinsamen Alben auf."
      ]
    ],
    "modesTitle": "Nah oder fern – OneSpace passt zu eurem Leben.",
    "apart": "Wenn ihr getrennt lebt",
    "apartText": "Zwei Zeitzonen, ein Countdown bis zum Wiedersehen und gemeinsame Reisepläne.",
    "together": "Wenn ihr zusammenlebt",
    "togetherText": "Aufgaben, Entscheidungen, Feiern und Erinnerungen – ohne dass eine Person an alles denken muss.",
    "foundTitle": "Werdet Teil der ersten 500 Gründungsmitglieder",
    "foundLead": "Die ersten 250 bestätigten Paare erhalten eine gemeinsame Gründungsnummer. Der frühe Zugang ist kostenlos; spätere Vorteile und Preise geben wir vorab bekannt.",
    "email": "E-Mail-Adresse",
    "phone": "Welches Handy nutzt du?",
    "android": "Android",
    "iphone": "iPhone",
    "both": "Beide",
    "unsure": "Noch nicht sicher",
    "consent": "Ich möchte per E-Mail Neuigkeiten zu OneSpace und dem Start erhalten.",
    "send": "Platz reservieren",
    "sentTitle": "Schau in dein Postfach",
    "sentText": "Wir haben dir einen Bestätigungslink geschickt. Bitte prüfe auch deinen Spam-Ordner.",
    "privacy": "Datenschutz (auf Englisch)",
    "legalNote": "Keine Werbung und kein Verkauf persönlicher Daten. Der geschlossene Android-Test wird vorbereitet; eine iPhone-Version ist geplant.",
    "support": "Noch Fragen? Schreib uns an",
    "freesoon": "Kostenloser Frühzugang. Ein öffentlicher Download über Google Play oder den App Store ist noch nicht verfügbar.",
    "languages": "Sprachen",
    "messages": {
      "sending": "Wird gesendet…",
      "missing": "Bitte fülle die Pflichtfelder aus.",
      "email": "Prüfe deine E-Mail-Adresse.",
      "consent": "Bitte bestätige den E-Mail-Empfang.",
      "failed": "Senden fehlgeschlagen. Versuche es erneut.",
      "busy": "Zu viele Versuche. Bitte warte kurz.",
      "verify": "Eine kurze Prüfung ist erforderlich.",
      "verify_failed": "Die Prüfung konnte nicht abgeschlossen werden."
    }
  }
}
LANG_LABELS = {'en':'English','ar':'العربية','es':'Español','fr':'Français','de':'Deutsch'}

def make_page(code, base):
    c=LOCALES[code]
    esc=html.escape
    url=base+code+'/'
    hreflang=''.join(f'<link rel="alternate" hreflang="{language}" href="{base+(language+"/" if language!="en" else "")}">' for language in ('en','ar','es','fr','de'))
    hreflang+=f'<link rel="alternate" hreflang="x-default" href="{base}">'
    langs=''.join(f'<a data-language-switch="{k}" href="{base+(k+"/" if k!="en" else "")}" lang="{k}"'+(' aria-current="page"' if k==code else '')+'>'+label+'</a>' for k,label in LANG_LABELS.items())
    cards=''.join(f'<article class="card reveal"><div class="ico i-teal">{icon}</div><h3>{esc(title)}</h3><p>{esc(desc)}</p></article>' for icon,title,desc in c['featureData'])
    signals=json.dumps(c['messages'],ensure_ascii=False)
    structured=json.dumps({'@context':'https://schema.org','@type':'MobileApplication','name':'OneSpace','operatingSystem':'Android, iOS','applicationCategory':'LifestyleApplication','inLanguage':code,'url':url,'description':c['description']},ensure_ascii=False)
    return f'''<!doctype html>
<html lang="{code}" dir="ltr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(c['title'])}</title><meta name="description" content="{esc(c['description'])}">
<link rel="canonical" href="{url}">{hreflang}
<meta property="og:site_name" content="OneSpace"><meta property="og:type" content="website"><meta property="og:locale" content="{code}">
<meta property="og:title" content="{esc(c['title'])}"><meta property="og:description" content="{esc(c['description'])}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{base}assets/press/og-image.png">
<meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#14213D">
<link rel="icon" href="/assets/favicon-32.png" sizes="32x32"><link rel="stylesheet" href="/assets/os.css">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<script>window.goatcounter={{path:function(){{return location.pathname}}}};window.ONESPACE_FORM_MESSAGES={signals};</script>
<script data-goatcounter="https://onespace.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
<script type="application/ld+json">{structured}</script>
</head><body>
<a class="skip" href="#main">{esc(c['home'])}</a>
<header class="top"><div class="wrap" style="display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap">
<a class="brand" href="/{code}/"><img src="/assets/mark.svg" alt="" width="34" height="34">OneSpace</a>
<nav class="os-intl-nav" aria-label="{esc(c['features'])}"><a href="#features">{esc(c['features'])}</a><a href="#how">{esc(c['how'])}</a><a class="btn btn-primary btn-sm" href="#founders" data-track="intl_join">{esc(c['founders'])}</a></nav>
<details class="os-intl-languages"><summary>🌐 {esc(c['label'])}</summary><div class="os-intl-languages-list">{langs}</div></details>
</div></header>
<main id="main">
<section class="page-hero"><div class="wrap" style="padding-top:22px;padding-bottom:28px">
<span class="eyebrow">{esc(c['eyebrow'])}</span><h1>{esc(c['hero'])}</h1>
<p class="lead" style="max-width:830px">{esc(c['lead'])}</p>
<div class="cta-row"><a class="btn btn-primary" href="#founders" data-track="intl_hero_join">{esc(c['join'])}</a>
<a class="btn btn-ghost" href="#features">{esc(c['try'])}</a></div>
</div></section>
<section id="features" class="wrap" style="padding-top:55px;padding-bottom:60px">
<div class="sec-head center"><h2>{esc(c['featuresTitle'])}</h2></div>
<div class="grid g3">{cards}</div>
</section>
<section id="how" class="tint"><div class="wrap" style="padding-top:55px;padding-bottom:55px">
<div class="sec-head center"><h2>{esc(c['modesTitle'])}</h2></div>
<div class="grid g2">
<article class="card"><div class="ico i-teal">🌍</div><h3>{esc(c['apart'])}</h3><p>{esc(c['apartText'])}</p></article>
<article class="card"><div class="ico i-coral">🏡</div><h3>{esc(c['together'])}</h3><p>{esc(c['togetherText'])}</p></article></div>
</div></section>
<section id="founders" class="wrap" style="padding-top:60px;padding-bottom:70px">
<div class="split" style="align-items:start">
<div><span class="eyebrow">{esc(c['founders'])}</span><h2>{esc(c['foundTitle'])}</h2><p class="lead">{esc(c['foundLead'])}</p>
<p>{esc(c['legalNote'])}</p><p>{esc(c['freesoon'])}</p><p><a href="/privacy.html" lang="en">{esc(c['privacy'])}</a></p></div>
<div class="panel"><form data-form="join" data-done="intl-done" novalidate>
<input name="invite" type="hidden"><input name="language" type="hidden" value="en">
<label for="intl-email">{esc(c['email'])} *</label><input type="email" name="email" id="intl-email" required autocomplete="email" placeholder="name@example.com">
<label>{esc(c['phone'])}</label><div class="radio-cards">
<label><input type="radio" name="platform" value="android" checked> {esc(c['android'])}</label>
<label><input type="radio" name="platform" value="iphone"> {esc(c['iphone'])}</label>
<label><input type="radio" name="platform" value="both"> {esc(c['both'])}</label>
<label><input type="radio" name="platform" value="unsure"> {esc(c['unsure'])}</label></div>
<input class="hp" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">
<label class="check"><input type="checkbox" name="consent" required> {esc(c['consent'])}</label>
<div class="cta-row"><button class="btn btn-primary" type="submit" data-track="intl_join_submit">{esc(c['send'])}</button></div>
<p class="status" role="status" aria-live="polite"></p></form>
<div id="intl-done" class="done" tabindex="-1"><h3>{esc(c['sentTitle'])}</h3><p>{esc(c['sentText'])}</p></div></div>
</div></section>
</main>
<footer><div class="wrap" style="padding-top:28px;padding-bottom:28px"><p>OneSpace · {esc(c['support'])} <a href="mailto:hello@onespace.live">hello@onespace.live</a>.</p>
<div class="os-intl-footer-lang">{langs}</div></div></footer>
<script src="/assets/ar.js" defer></script><script src="/assets/os.js" defer></script>
</body></html>'''
