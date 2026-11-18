"""Editorial linkification for the 24 end-to-end scenarios.

Operates after translation to preserve native, complete paragraph copy and
locale-specific relative URLs. Only the first occurrence of each relevant
feature in a journey is linked, with no more than two per paragraph.
"""
import re
from bs4 import BeautifulSoup, NavigableString

FEATURE_TERMS = {
  "today": {
    "en": ["Since You Were Away", "Today view", "Today"],
    "ar": ["أثناء غيابك", "شاشة «اليوم»", "«اليوم»"],
    "es": ["Mientras no estabas", "pantalla Hoy", "en Hoy", "abre Hoy"],
    "fr": ["Aujourd’hui", "aujourd’hui"],
    "de": ["öffnet Heute", "auf Heute", "Heute"],
  },
  "gestures": {
    "en": ["thank-you gesture", "personal gesture", "love gesture", "little-love gesture", "kiss gesture", "gesture"],
    "ar": ["لمسة حب", "لمسة شكر", "لمسة قبلة", "لفتة"],
    "es": ["gesto de agradecimiento", "gesto de cariño", "un gesto", "un beso"],
    "fr": ["petite attention", "une attention", "un baiser"],
    "de": ["Liebesgeste", "eine Geste", "Geste"],
  },
  "checklists": {
    "en": ["repeating morning checklist", "recurring checklist", "shared checklist", "packing checklist", "preparation checklist", "checklist", "to-do"],
    "ar": ["قائمة الصباح المتكررة", "قائمة البيت المتكررة", "قائمة تجهيز", "قائمة مشتركة", "قائمة المهام", "القوائم", "قائمة"],
    "es": ["lista matinal recurrente", "lista recurrente", "lista compartida", "lista de equipaje", "lista de tareas", "lista"],
    "fr": ["liste du matin récurrente", "liste commune", "liste de bagages", "liste récurrente", "liste"],
    "de": ["tägliche Checkliste", "wiederkehrende Aufgaben", "gemeinsame Liste", "Packliste", "Checkliste", "Liste"],
  },
  "activities": {
    "en": ["shared Coordinate activity", "Coordinate activity", "shared activity", "activity"],
    "ar": ["نشاطًا مشتركًا", "نشاط مشترك", "النشاط", "نشاط"],
    "es": ["actividad compartida", "actividad"],
    "fr": ["activité commune", "activité partagée", "activité"],
    "de": ["gemeinsame Aktivität", "Aktivität"],
  },
  "sharing": {
    "en": ["Smart Sharing", "shares it from her Android browser", "shares their links from his Android browser", "shares a store link", "shares their links"],
    "ar": ["المشاركة الذكية", "يشارك روابطها من متصفح أندرويد", "تشارك رابط متجر", "يشارك"],
    "es": ["comparte los enlaces desde Android", "comparte un enlace desde Android", "comparte"],
    "fr": ["partage les liens depuis son navigateur Android", "partage un lien depuis Android", "partage"],
    "de": ["teilt die Links über Android", "teilt einen Shoplink über Android", "teilt"],
  },
  "comparison": {
    "en": ["comparison table", "the comparison", "compare options", "compare their choices", "compare"],
    "ar": ["جدول المقارنة", "المقارنة", "يقارنان", "تقارن", "يقارن"],
    "es": ["tabla comparativa", "la comparación", "comparan", "comparar"],
    "fr": ["tableau comparatif", "la comparaison", "comparent", "comparer"],
    "de": ["Vergleichstabelle", "vergleichen", "Vergleich"],
  },
  "reminders": {
    "en": ["linked reminder", "shared reminder", "private reminder", "repeating reminder", "reminder", "deadline"],
    "ar": ["التذكيرات", "تذكيرًا", "تذكير", "موعدًا نهائيًا"],
    "es": ["recordatorio recurrente", "recordatorio privado", "recordatorio", "plazo"],
    "fr": ["rappel récurrent", "rappel privé", "rappel", "échéance"],
    "de": ["wiederkehrende Erinnerung", "private Erinnerung", "Erinnerung", "Frist"],
  },
  "contacts": {
    "en": ["contact card", "contact details", "contact number", "contact information"],
    "ar": ["بطاقة تواصل", "بطاقة التواصل", "بطاقة الوكيل", "بطاقات تواصل", "بيانات التواصل", "رقم التواصل"],
    "es": ["ficha de contacto", "contacto guardado", "contacto del", "contactos"],
    "fr": ["fiche contact", "contact du", "contact"],
    "de": ["Kontaktkarte", "Kontaktkarten", "Maklerkontakt", "Kontakt"],
  },
  "trips": {
    "en": ["shared trip", "trip", "travel plan", "travel documents"],
    "ar": ["رحلة مشتركة", "الرحلة", "الرحلات", "خطة السفر"],
    "es": ["viaje compartido", "viaje", "viajes"],
    "fr": ["voyage commun", "voyage", "voyages"],
    "de": ["gemeinsame Reise", "Reise", "Reisen"],
  },
  "places": {
    "en": ["Our Places", "shared map", "bucket list", "place as visited"],
    "ar": ["«أماكننا»", "الخريطة", "قائمة الأحلام", "أماكننا"],
    "es": ["Nuestros lugares", "mapa", "lugares"],
    "fr": ["Nos lieux", "carte", "lieux"],
    "de": ["Unsere Orte", "Karte", "Orte"],
  },
  "counters": {
    "en": ["reunion counter", "counter"],
    "ar": ["عدّادًا للقاء", "عدّاد", "العدّادات"],
    "es": ["cuenta atrás", "contador"],
    "fr": ["compte à rebours", "compteur"],
    "de": ["Countdown", "Zähler"],
  },
  "memories": {
    "en": ["shared memory", "shared Memories", "memories", "memory", "scrapbook"],
    "ar": ["ذكرى مشتركة", "الذكريات", "ذكرى", "الألبوم"],
    "es": ["recuerdo compartido", "Recuerdos", "recuerdo", "álbum"],
    "fr": ["souvenir partagé", "souvenirs", "souvenir", "album"],
    "de": ["gemeinsame Erinnerung", "Erinnerungen", "Erinnerung", "Scrapbook"],
  },
  "watchlist": {
    "en": ["shared watchlist", "watchlist"],
    "ar": ["قائمة المشاهدة المشتركة", "قائمة المشاهدة"],
    "es": ["lista común", "lista para ver"],
    "fr": ["liste de visionnage", "liste de films"],
    "de": ["gemeinsame Watchlist", "Watchlist"],
  },
  "calendar": {
    "en": ["shared calendar", "calendar event", "calendar"],
    "ar": ["التقويم المشترك", "التقويم"],
    "es": ["calendario compartido", "calendario"],
    "fr": ["calendrier partagé", "calendrier"],
    "de": ["gemeinsamen Kalender", "Kalender"],
  },
  "journal": {
    "en": ["private Feelings Journal", "Feelings Journal", "private journal", "journal"],
    "ar": ["يوميات مشاعرها الخاصة", "اليوميات الخاصة", "يومياتها", "اليوميات"],
    "es": ["diario emocional privado", "diario privado", "diario"],
    "fr": ["journal des émotions privé", "journal privé", "journal"],
    "de": ["privates Gefühlstagebuch", "Gefühlstagebuch", "Tagebuch"],
  },
  "checkins": {
    "en": ["daily check-in", "check-in"],
    "ar": ["تواصلًا يوميًا", "التواصل اليومي", "التواصل"],
    "es": ["registro diario"],
    "fr": ["bilan quotidien", "bilan"],
    "de": ["täglichen Check-in", "Check-in"],
  },
  "notes": {
    "en": ["shared note", "private note", "note"],
    "ar": ["ملاحظة مشتركة", "ملاحظة خاصة", "ملاحظات", "ملاحظة"],
    "es": ["nota privada", "notas", "nota"],
    "fr": ["notes privées", "notes", "note"],
    "de": ["private Notiz", "Notizen", "Notiz"],
  },
  "letters": {
    "en": ["sealed letter", "love letter"],
    "ar": ["رسالة حب", "الرسالة المغلقة", "رسالة"],
    "es": ["carta de amor", "carta"],
    "fr": ["lettre d’amour", "lettre"],
    "de": ["Liebesbrief", "Brief"],
  },
  "occasions": {
    "en": ["private occasion", "shared occasion", "occasion", "anniversary"],
    "ar": ["مناسبة خاصة", "مناسبة مشتركة", "المناسبة", "عيد الميلاد"],
    "es": ["ocasión privada", "ocasión compartida", "ocasión"],
    "fr": ["occasion privée", "occasion commune", "occasion"],
    "de": ["privaten Anlass", "Anlass"],
  },
  "privacy": {
    "en": ["Only me", "private attachments"],
    "ar": ["«أنا فقط»", "الخصوصية"],
    "es": ["Solo yo"],
    "fr": ["Moi uniquement"],
    "de": ["Nur ich"],
  },
}

def linkify_journeys(root, journeys, features):
    """Link distinct contextual feature mentions in all 5 fully translated pages."""
    count = {}
    for index, locale in enumerate(("en", "ar", "es", "fr", "de")):
        path = root / (locale if locale != "en" else "") / "scenarios.html"
        soup = BeautifulSoup(path.read_text(encoding="utf8"), "html.parser")
        linked = 0
        for journey in journeys:
            episode = soup.find(id="story-" + journey["slug"])
            if episode is None:
                raise RuntimeError("Missing journey on " + str(path) + ": " + journey["slug"])
            used = set()
            for para in episode.select(".journey-beat p"):
                if para.find(True):
                    raise RuntimeError("Journey paragraphs unexpectedly contain nested markup")
                text = para.get_text()
                candidates = []
                for feature in journey["features"]:
                    if feature in used:
                        continue
                    for phrase in FEATURE_TERMS.get(feature, {}).get(locale, ()):
                        pat = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
                        for m in re.finditer(pat, text, flags=re.IGNORECASE):
                            candidates.append((m.start(), -(m.end()-m.start()), m.end(), feature))
                candidates.sort()
                selected = []
                for start, negative_size, end, feature in candidates:
                    if feature in used or len(selected) >= 2 or len(used) >= 10:
                        continue
                    if any(start < prev_end and end > prev_start for prev_start, prev_end, _ in selected):
                        continue
                    used.add(feature)
                    selected.append((start, end, feature))
                if selected:
                    before = text
                    para.clear()
                    cursor = 0
                    for start, end, feature in sorted(selected):
                        if cursor < start:
                            para.append(NavigableString(before[cursor:start]))
                        tag = soup.new_tag("a", href=features[feature][5])
                        tag["class"] = "journey-inline-link"
                        tag.string = before[start:end]
                        para.append(tag)
                        cursor = end
                        linked += 1
                    if cursor < len(before):
                        para.append(NavigableString(before[cursor:]))
                # This paragraph has already been translated on the server.
                # Avoid client-side i18n replacing the linked DOM with plain text.
                para.attrs.pop("data-i18n", None)
        path.write_text(str(soup), encoding="utf8")
        count[locale] = linked
    return count
