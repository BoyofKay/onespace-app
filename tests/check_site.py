"""OneSpace static-site smoke checks — no external dependencies."""
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGES = ["index.html", "compare.html", "smart-sharing.html", "decide-together.html", "trips.html", "occasions.html", "watchlists.html", "memories.html", "everyday.html", "features.html", "long-distance.html", "living-together.html",
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
