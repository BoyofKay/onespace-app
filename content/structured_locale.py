"""Synchronize localized FAQ and Article JSON-LD with visible translated pages.
Structured metadata should never describe English copy on a different-language URL.
"""
import json

def localize_structured(soup, locale, canonical):
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            data = json.loads(script.string or script.get_text())
        except (TypeError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        kind = data.get('@type')
        if kind == 'FAQPage':
            cards = soup.select('details[data-faq]')
            questions = data.get('mainEntity')
            if not isinstance(questions, list) or len(cards) != len(questions):
                raise RuntimeError('FAQ structured data and visible questions disagree')
            for card, question in zip(cards, questions):
                title = card.find('summary')
                answer = card.find('div')
                if not title or not answer:
                    raise RuntimeError('FAQ question or answer is missing')
                question['name'] = title.get_text(' ', strip=True)
                question['acceptedAnswer']['text'] = answer.get_text(' ', strip=True)
            script.string = json.dumps(data, ensure_ascii=False)
        elif kind == 'Article':
            heading = soup.find('h1')
            meta = soup.find('meta', attrs={'name': 'description'})
            if heading:
                data['headline'] = heading.get_text(' ', strip=True)
            if meta:
                data['description'] = meta.get('content', '')
            data['inLanguage'] = locale
            data['mainEntityOfPage'] = canonical
            script.string = json.dumps(data, ensure_ascii=False)
