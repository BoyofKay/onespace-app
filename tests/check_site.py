"""OneSpace static-site smoke checks — no external dependencies."""
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGES = ["index.html", "compare.html", "smart-sharing.html", "decide-together.html", "trips.html", "occasions.html", "watchlists.html", "memories.html", "everyday.html", "features.html", "connect-care.html", "long-distance.html", "living-together.html",
         "how-it-works.html", "tutorials.html", "whats-new.html", "faq.html", "join.html",
         "support.html", "share-kit.html", "guides.html", "guide-long-distance-ideas.html", "guide-mental-load.html", "guide-anniversary-planning.html", "privacy.html", "terms.html", "delete-account.html", "404.html"]
PAGES += ["ar/" + p for p in PAGES if p != "404.html"]  # server-rendered Arabic twins
EN_PAGES = [p for p in PAGES if not p.startswith("ar/") and p != "404.html"]
PAGES += [f"{lang}/{p}" for lang in ("es", "fr", "de") for p in EN_PAGES]  # full site mirrors
REDIRECTS = ["v4.html", "v4-tutorial.html"]
# Claims the app does not make (D1: automatic gestures retired; D55: voice hidden) and private data.
FORBIDDEN = ["automatically at the right moment", "Automatic gestures", "voice command", "Kandice", "ph.ahmed"]


class Inspect(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.ids = set()
        self.h1 = 0
        self.main = 0
        self.meta_description = False
        self.ui = {k: 0 for k in ('img','video','source','picture','form','theme','views','view','track','share')}

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag in self.ui:
            self.ui[tag] += 1
        for marker, attr in (('theme','data-theme-pick'),('views','data-views'),
                             ('view','data-view'),('track','data-track'),('share','data-share')):
            if attr in values:
                self.ui[marker] += 1
        if tag == "h1":
            self.h1 += 1
        if tag == "main":
            self.main += 1
        if tag == "meta" and values.get("name") == "description":
            self.meta_description = True
        if "id" in values:
            if values["id"] in self.ids:
                raise AssertionError(f"Duplicate id {values['id']}")
            self.ids.add(values["id"])
        if tag in ("a", "img", "script", "link"):
            ref = values.get("href") or values.get("src")
            if ref:
                self.refs.append((tag, ref))
        if tag == "img" and "alt" not in values:
            raise AssertionError("Image without alt text")


def main():
    errors = []
    parsed = {}
    for path in PAGES:
        file = ROOT / path
        if not file.exists():
            errors.append(f"Missing page: {path}")
            continue
        parser = Inspect()
        try:
            parser.feed(file.read_text(encoding="utf-8"))
            parsed[path] = parser
            if parser.h1 != 1:
                errors.append(f"{path}: expected one H1, got {parser.h1}")
            if parser.main != 1:
                errors.append(f"{path}: expected one main, got {parser.main}")
            if not parser.meta_description and path != "404.html":
                errors.append(f"{path}: missing description")
        except Exception as ex:
            errors.append(f"{path}: {ex}")

    for name, parser in parsed.items():
        for tag, ref in parser.refs:
            url = urlsplit(ref)
            if url.scheme or ref.startswith("//") or ref.startswith("mailto:"):
                continue
            clean = url.path
            here = (ROOT / name).parent
            if clean == "":
                target = ROOT / name
            elif clean.startswith("/"):
                target = ROOT / clean.lstrip("/")
                if clean.endswith("/"):
                    target = target / "index.html"
            elif clean in (".", "./"):
                target = here / "index.html"
            else:
                target = here / clean.removeprefix("./")
                if target.is_dir():
                    target = target / "index.html"
            if not target.exists():
                errors.append(f"{name}: {tag} refers to missing {ref}")
                continue
            if url.fragment and target.suffix == ".html":
                target_name = target.relative_to(ROOT).as_posix()
                dest = parsed.get(target_name)
                if dest and url.fragment not in dest.ids:
                    errors.append(f"{name}: missing anchor {ref}")

    # Localization must preserve the REAL English website design and functionality.
    # No replacement mini-landing pages are permitted: every original feature
    # page, screenshot, demo view, themed-phone control and form must survive.
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    for locale in ("es", "fr", "de"):
        for en in EN_PAGES:
            localized = f"{locale}/{en}"
            original = parsed.get(en)
            target = parsed.get(localized)
            if not original or not target:
                errors.append(f"{localized}: missing full source-equivalent page")
                continue
            for marker in original.ui:
                if original.ui[marker] != target.ui[marker]:
                    errors.append(f"{localized}: {marker} parity mismatch: {target.ui[marker]} != {original.ui[marker]}")
            doc = (ROOT / localized).read_text(encoding="utf-8")
            # Regression: translating <!doctype html> used to print a literal
            # 'HTML' above the Spanish navigation bar.
            if not doc.lstrip().lower().startswith("<!doctype html>"):
                errors.append(f"{localized}: HTML5 doctype lost or translated into visible text")
            if en == "index.html":
                if "store-platform-symbol" not in doc:
                    errors.append(f"{localized}: store platform icons missing")
                if "nav-join" not in doc:
                    errors.append(f"{localized}: compact navigation CTA missing")
                if locale == "de" and "Ihre Beziehung ist nicht zufrieden" in doc:
                    errors.append(f"{localized}: incorrect privacy marketing translation")

            slug = "" if en == "index.html" else en
            for expected in (f'lang="{locale}"', f'hreflang="{locale}"',
                             f'href="https://onespace.live/{locale}/{slug}"',
                             'goatcounter.com/count', '/assets/os.js'):
                if expected not in doc:
                    errors.append(f"{localized}: missing {expected}")
            if f'<loc>https://onespace.live/{locale}/{slug}</loc>' not in sitemap:
                errors.append(f"sitemap missing {localized}")
        for state in ("confirm.html", "unsubscribe.html"):
            translated = ROOT / locale / state
            if not translated.exists() or 'noindex' not in translated.read_text(encoding='utf8'):
                errors.append(f"{locale}/{state}: must exist and stay non-indexable")
    for lang in ("es","fr","de"):
        import json
        data = json.loads((ROOT / "content" / "translations" / (lang+".json")).read_text(encoding="utf-8"))
        if len(data) < 1300:
            errors.append(f"{lang}: translation catalogue too small ({len(data)} strings)")
    css = (ROOT / "assets" / "os.css").read_text(encoding="utf-8")
    for marker in ("scrollbar-color:var(--teal)", "store-platform-symbol", ".top .actions .nav-join"):
        if marker not in css:
            errors.append(f"Localized visual polish missing from CSS: {marker}")
    if not (ROOT / "robots.txt").exists() or not (ROOT / "sitemap.xml").exists():
        errors.append("Missing SEO files")
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    for marker in ('id="founding"', 'data-founder-entry', 'id="the-difference"', 'data-views="tabs"', 'data-theme-pick='):
        if marker not in index:
            errors.append(f"Missing interactive UI on the homepage: {marker}")
    join_page = (ROOT / "join.html").read_text(encoding="utf-8")
    if 'data-form="join"' not in join_page:
        errors.append("The canonical Founder signup form is missing from join.html")
    if 'data-form="join"' in index:
        errors.append("The homepage must link to the single Founder signup, not duplicate it")
    if 'href="compare.html"' not in index:
        errors.append("Why OneSpace must be reachable from the main navigation")
    # Preserve the original interactive marketing experiences and real app media.
    for marker in ('id="tour"', 'data-theme-pick=', 'id="connect-care-showcase"',
                   'id="reviews-preview"', 'data-review-preview="test-only"'):
        if marker not in index:
            errors.append(f"Missing preserved experience or test-labelled prototype: {marker}")
    if 'AI-GENERATED PLACEHOLDERS' not in index:
        errors.append("Review testing prototypes must be visibly labelled as AI generated")
    if '<meta itemprop="ratingValue"' in index or '"aggregateRating"' in index:
        errors.append("Fictional testing prototypes must not feed rating structured data")
    connect=(ROOT/"connect-care.html").read_text(encoding="utf-8")
    for marker in ('id="letters"', 'id="gestures"', 'id="checkins"', 'id="journal"',
                   'assets/app/en/letters.webp', 'assets/app/en/love.webp'):
        if marker not in connect:
            errors.append(f"Connect & Care missing section or real screenshot: {marker}")
    smart=(ROOT/"smart-sharing.html").read_text(encoding="utf-8")
    if 'Three simple steps.' not in smart or 'Four simple steps.' in smart:
        errors.append("Smart sharing must display its actual three-step process")
    if 'class="btn btn-primary btn-sm" href="join.html"' in index.split("<footer>",1)[-1].split("</footer>",1)[0]:
        errors.append("Footer must not have a join CTA")
    # Next marketing iteration: all six real demo steps, theme grid, search,
    # schedule-aware notifications and truthful platform-neutral Founder sign-up.
    demo = (ROOT / "how-it-works.html").read_text(encoding="utf-8")
    for marker in ('data-demo-wizard', 'data-demo-prev', 'data-next="tour"',
                   'data-demo-progress', 'demo-theme-grid', 'data-views="tour"'):
        if marker not in demo:
            errors.append(f"Guided demo missing: {marker}")
    if demo.count('class="demo-step"') != 6:
        errors.append("The guided demo must have exactly six selectable steps")
    if demo.count('data-theme-pick=') != 9:
        errors.append("The guided demo must preserve all nine existing themes")
    if 'data-testimonial-carousel' not in index or 'data-slide-next' not in index:
        errors.append("Missing compact testimonial carousel")
    if index.count('class="store-rating-row"') != 10:
        errors.append("Each of two store panels needs a full five-row rating breakdown")
    if index.count('class="footer-social-item"') != 5:
        errors.append("All five noninteractive footer social placeholders are required")
    if 'href="#"' in index.split('<div class="footer-social">')[-1].split('</div>', 1)[0]:
        errors.append("Social placeholders must not have fake links")
    for marker in ('id="smart-details"', 'assets/app/en/notifications.webp',
                   'Illustrative layout', 'data-nosnippet'):
        if marker not in index:
            errors.append(f"Missing smart feature or test disclaimer: {marker}")
    if not (ROOT / 'assets/app/en/checkins.png').is_file():
        errors.append("Genuine demo couple check-in screenshot must exist")
    join = (ROOT / "join.html").read_text(encoding="utf-8")
    for marker in ('iPhone', 'Founder registration is open to Android and iPhone couples',
                   'name="platform"'):
        if marker not in join:
            errors.append(f"Founder sign-up must be available to iPhone owners: {marker}")
    if 'Join the Founding 500 today' not in index or 'registration is open to both Android and iPhone users' not in index:
        errors.append("Public store section must not imply iPhone users must wait to register")
    # Feedback follow-through: no unrelated map in Smart Sharing, no double Connect,
    # the editorial headings use the existing signature coral italic, and demo themes
    # live within the wizard shell rather than a second detached module.
    sharing = (ROOT / 'smart-sharing.html').read_text(encoding='utf-8')
    features = (ROOT / 'features.html').read_text(encoding='utf-8')
    if 'assets/app/en/places_map.webp' in sharing.split('<section class="tint">',1)[0]:
        errors.append("Smart Sharing hero cannot show an unrelated map screenshot")
    if 'sharing-preview-wrap' not in sharing or 'assets/app/en/lists.webp' not in sharing:
        errors.append("Smart Sharing must illustrate its share flow and show a real shared list")
    if 'editorial-hero-title' not in sharing or 'editorial-hero-title' not in features:
        errors.append("Key feature headlines must use established brand serif accent")
    if features.count('id="connect"') != 1:
        errors.append("Features page must have one Connect section, not duplicate Connect & Care")
    if 'demo-theme-inline' not in demo or 'demo-theme-picker' in demo:
        errors.append("Theme selector must be integrated inside the guided demo")
    if 'class="watch-clips"' not in index and 'watch-clips' not in index:
        errors.append("Real screenshot/clip showcase must not use the old scrolling strip")
    if "iOS coming soon” refers to the app release" in index:
        errors.append("Do not repeat the awkward iOS-registration clarification")
    if 'class="review-brand-icon"' not in index:
        errors.append("Reviews preview must include app platform artwork")
    connect = (ROOT / 'connect-care.html').read_text(encoding='utf-8')
    if 'assets/app/en/connect.webp' in connect.split('id="journal"',1)[-1].split('connection-followup',1)[0]:
        errors.append("Feelings journal must not claim a generic Connect screen is the journal")
    if 'gesture-capture-slots' not in connect:
        errors.append("Gesture popup and history capture slots must be preserved")
    # Ensure new marketing UI and original protected flows survive regeneration.
    for locale in ("index.html", "ar/index.html"):
        page = (ROOT / locale).read_text(encoding="utf-8")
        for marker in ('id="get-the-app"', 'Google Play', 'App Store',
                       'aria-controls="mega-features"', 'id="mega-features"',
                       'aria-controls="mega-couples"', 'aria-controls="mega-learn"',
                       'family=Inter:wght'):
            if marker not in page:
                errors.append(f"{locale}: missing generated navigation/store marker: {marker}")
        if "store_android_waitlist" not in page or "store_iphone_waitlist" not in page:
            errors.append(f"{locale}: store cards must link to Founder waitlist")
        if 'id="founding"' not in page or 'data-theme-pick=' not in page:
            errors.append(f"{locale}: founder area or theme wizard missing")
    if 'href="https://play.google.com/store/apps/' in index or 'href="https://apps.apple.com/app/' in index:
        errors.append("Do not link to unpublished store listings")
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    for path in PAGES:
        if path != "404.html" and (ROOT / path).exists() and ("/" + path.removesuffix("index.html") + "</loc>") not in sitemap:
            errors.append(f"sitemap.xml is missing {path}")
    for path in REDIRECTS:
        if 'http-equiv="refresh"' not in (ROOT / path).read_text(encoding="utf-8"):
            errors.append(f"{path} should redirect")
    for path in PAGES + ["assets/ar.js", "assets/os.js"]:
        text = (ROOT / path).read_text(encoding="utf-8")
        for word in FORBIDDEN:
            if word.lower() in text.lower():
                errors.append(f"{path}: contains forbidden text '{word}'")
    # A single-element selector ($) must never be iterated like a list ($).
    # Such a runtime error used to stop the mega menu and all later page widgets.
    js_source = (ROOT / "assets/os.js").read_text(encoding="utf-8")
    if re.search(r"(?<!\$)\$\([^;\n]+\)\.(?:forEach|length)\b", js_source):
        errors.append("assets/os.js: singleton $() selector treated as a list; use $()")
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print(f"PASS: {len(parsed)} HTML pages, local links and anchors, descriptions, images and interactive landmarks")


if __name__ == "__main__":
    main()
