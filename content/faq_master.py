"""27 Nov 2026 (owner decision): ONE FAQ for the website and the app.

The source is content/faq/*.json (EN, AR, ES, FR, DE). The website FAQ page is
built from it here, and the app's lib/features/support/faq_content.dart is
generated from the same files (tools/faq/sync_faq.py in the app repository), so
the two can no longer drift apart.

Each answer is a list of blocks: ["p", text], ["steps", [texts]] or
["bullets", [texts]]. "where": both | web | app. "tutorial": true adds a link
to that feature's video tutorial (tutorials.html#<id>, D110).
"""
import json
from pathlib import Path

LANGS = ('en', 'ar', 'es', 'fr', 'de')
ROOT = Path(__file__).resolve().parent / 'faq'
TUTORIAL_LINK = {
    'en': 'Watch the video tutorial →', 'ar': 'شاهد الدرس بالفيديو ←', 'es': 'Ver el tutorial en vídeo →',
    'fr': 'Voir le tutoriel vidéo →', 'de': 'Video-Tutorial ansehen →',
}


def groups():
    return [json.loads(p.read_text(encoding='utf-8')) for p in sorted(ROOT.glob('*.json'))]


def web_groups():
    out = []
    for g in groups():
        items = [i for i in g['items'] if i.get('where', 'both') in ('both', 'web')]
        if items:
            out.append({**g, 'items': items})
    return out


def _texts(block):
    kind, value = block
    return [value] if kind == 'p' else list(value)


def register_translations(glossary):
    """Adds ES/FR/DE for every FAQ text to the build glossary (keyed by English)."""
    def add(t):
        for lang in ('es', 'fr', 'de'):
            glossary.setdefault(lang, {})[t['en']] = t[lang]
    add(TUTORIAL_LINK)
    for g in groups():
        add(g['title'])
        for item in g['items']:
            add(item['q'])
            for block in item['a']:
                for t in _texts(block):
                    add(t)


def answer_html(item, T):
    """Answer as paragraphs, numbered steps and bullet points (no wall of text)."""
    html = ''
    for kind, value in item['a']:
        if kind == 'p':
            html += T(value['en'], value['ar'], 'p')
        else:
            tag = 'ol' if kind == 'steps' else 'ul'
            html += f'<{tag} class="faq-{kind}">' + ''.join(T(v['en'], v['ar'], 'li') for v in value) + f'</{tag}>'
    if item.get('tutorial'):
        import tutorial_videos  # a feature with its own video opens at that video (D110)
        anchor = f'#{item["id"]}' if item['id'] in {t['id'] for t in tutorial_videos.tutorials()} else ''
        html += f'<p class="faq-more"><a href="tutorials.html{anchor}">{T(TUTORIAL_LINK["en"], TUTORIAL_LINK["ar"])}</a></p>'
    return html


def answer_plain(item):
    parts = []
    for block in item['a']:
        parts += [t['en'] for t in _texts(block)]
    return ' '.join(parts)
