"""27 Nov 2026 (owner decision D110): one short video tutorial per feature.

Each tutorial covers ONE feature (stories that mix features live on the
Stories & scenarios page). The videos are recorded fresh by the screenshot
robot (OneSpace repo, set "tutorial") with the fictional demo couple, English
first. Chapter captions sit under the video in every language; tapping one
jumps to that moment (assets/os.js, data-tut). "What your partner sees",
"On your own" and "Works with" appear only where a tutorial has them.

Source: content/tutorial_videos.json (EN, AR, ES, FR, DE). Chapter times come
from assets/app/video/en_<clip>.chapters.json, written by the robot.
"""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = Path(__file__).resolve().parent / 'tutorial_videos.json'
VIDEO = ROOT / 'assets' / 'app' / 'video'
BOXES = (
    ('partner', {'en': 'What your partner sees', 'ar': 'ما يراه شريكك', 'es': 'Lo que ve tu pareja',
                 'fr': 'Ce que voit votre partenaire', 'de': 'Was dein Partner sieht'}),
    ('solo', {'en': 'On your own', 'ar': 'بمفردك', 'es': 'Por tu cuenta', 'fr': 'Seul(e)', 'de': 'Allein'}),
    ('works', {'en': 'Works with', 'ar': 'يعمل مع', 'es': 'Funciona con', 'fr': 'Fonctionne avec', 'de': 'Funktioniert mit'}),
)
FAQ_LINK = {'en': 'Exact steps in the FAQ →', 'ar': 'الخطوات بالتفصيل في الأسئلة الشائعة ←',
            'es': 'Pasos exactos en las preguntas frecuentes →', 'fr': 'Étapes détaillées dans la FAQ →',
            'de': 'Genaue Schritte in den FAQ →'}
PAGE = [
    {'en': 'OneSpace tutorials — a short video for every feature', 'es': 'Tutoriales de OneSpace: un vídeo corto para cada función',
     'fr': 'Tutoriels OneSpace : une courte vidéo pour chaque fonction', 'de': 'OneSpace-Tutorials: ein kurzes Video für jede Funktion'},
    {'en': 'Short videos of every OneSpace feature in the real app: Today, calendar, lists, reminders, notes, activities, trips, occasions, counters, places, contact cards, letters, check-ins, experiences, memories and saving from any app.',
     'es': 'Vídeos cortos de cada función de OneSpace en la app real: Hoy, calendario, listas, recordatorios, notas, actividades, viajes, ocasiones, contadores, lugares, fichas de contacto, cartas, check-ins, experiencias, recuerdos y guardar desde cualquier app.',
     'fr': 'De courtes vidéos de chaque fonction de OneSpace dans la vraie app : Aujourd’hui, calendrier, listes, rappels, notes, activités, voyages, occasions, compteurs, lieux, fiches contact, lettres, check-ins, expériences, souvenirs et enregistrement depuis n’importe quelle app.',
     'de': 'Kurze Videos jeder OneSpace-Funktion in der echten App: Heute, Kalender, Listen, Erinnerungen, Notizen, Aktivitäten, Reisen, Anlässe, Zähler, Orte, Kontaktkarten, Briefe, Check-ins, Erlebnisse, Erinnerungen und Speichern aus jeder App.'},
    {'en': 'See each feature in action.', 'es': 'Mira cada función en acción.', 'fr': 'Voyez chaque fonction en action.', 'de': 'Sieh jede Funktion in Aktion.'},
    {'en': 'A short video of every feature in the real app, with Adam and Lina, a fictional couple. Tap a caption to jump to that moment. For exact steps, each tutorial links to the FAQ; for real-life stories, see',
     'es': 'Un vídeo corto de cada función en la app real, con Adam y Lina, una pareja ficticia. Toca un título para saltar a ese momento. Para los pasos exactos, cada tutorial enlaza con las preguntas frecuentes; para historias reales, consulta',
     'fr': 'Une courte vidéo de chaque fonction dans la vraie app, avec Adam et Lina, un couple fictif. Touchez un titre pour aller à ce moment. Pour les étapes exactes, chaque tutoriel renvoie à la FAQ ; pour des histoires réelles, voyez',
     'de': 'Ein kurzes Video jeder Funktion in der echten App, mit Adam und Lina, einem fiktiven Paar. Tippe auf einen Titel, um zu dieser Stelle zu springen. Genaue Schritte findest du über den Link zu den FAQ; echte Geschichten unter'},
    {'en': 'Stories & scenarios', 'es': 'Historias y escenarios', 'fr': 'Histoires et scénarios', 'de': 'Geschichten und Szenarien'},
]
CHAPTERS = {'en': 'Chapters', 'ar': 'الفصول', 'es': 'Capítulos', 'fr': 'Chapitres', 'de': 'Kapitel'}


def tutorials():
    return json.loads(SOURCE.read_text(encoding='utf-8'))


def _texts(t):
    yield t['title']
    yield t['helps']
    yield from t['chapters']
    for key, _ in BOXES:
        if key in t:
            yield t[key]


def register_translations(glossary):
    """Adds ES/FR/DE for every tutorial text to the build glossary (keyed by English)."""
    fixed = PAGE + [FAQ_LINK, CHAPTERS] + [label for _, label in BOXES]
    for text in fixed + [x for t in tutorials() for x in _texts(t)]:
        for lang in ('es', 'fr', 'de'):
            glossary.setdefault(lang, {})[text['en']] = text[lang]


def chapter_times(t):
    f = VIDEO / f'en_{t["clip"]}.chapters.json'
    times = json.loads(f.read_text()) if f.exists() else []
    n = len(t['chapters'])
    if len(times) < n:  # no robot marks yet: spread the captions evenly
        times = [round(i * 4.0, 1) for i in range(n)]
    return times[:n]


def has_video(t):
    return (VIDEO / f'en_{t["clip"]}.mp4').exists()


def _clock(s):
    s = int(s)
    return f'{s // 60}:{s % 60:02d}'


def tutorial_html(t, T, K):
    """One tutorial: the video, its chapter captions, the optional boxes and a link to the FAQ steps."""
    src = f'assets/app/video/en_{t["clip"]}'
    label = K(t['title']['en'], t['title']['ar'])
    video = (f'<div class="tut-video"><video src="{src}.mp4" poster="{src}.jpg" controls playsinline preload="none" '
             f'aria-label="{escape(t["title"]["en"])}" data-i18n-attr="aria-label:{label}"></video></div>'
             if has_video(t) else '')
    caps = ''.join(f'<li><button type="button" data-t="{sec}"><span class="tut-time">{_clock(sec)}</span>'
                   f'{T(c["en"], c["ar"])}</button></li>'
                   for c, sec in zip(t['chapters'], chapter_times(t)))
    boxes = ''.join(f'<div class="tut-box">{T(label["en"], label["ar"], "b")}{T(t[key]["en"], t[key]["ar"], "p")}</div>'
                    for key, label in BOXES if key in t)
    faq = f'<p class="faq-more"><a href="faq.html#features-{t["id"]}">{T(FAQ_LINK["en"], FAQ_LINK["ar"])}</a></p>'
    return (f'<article class="tut" id="{t["id"]}" data-tut>{video}<div class="tut-body">'
            f'{T(t["title"]["en"], t["title"]["ar"], "h2")}{T(t["helps"]["en"], t["helps"]["ar"], "p", "muted")}'
            f'{T(CHAPTERS["en"], CHAPTERS["ar"], "p", "tut-label")}<ol class="tut-chapters">{caps}</ol>{boxes}{faq}</div></article>')
