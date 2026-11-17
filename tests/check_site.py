"""OneSpace static-site smoke checks — no external dependencies."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGES = ["index.html", "compare.html", "smart-sharing.html", "decide-together.html", "trips.html", "occasions.html", "watchlists.html", "memories.html", "everyday.html", "features.html", "long-distance.html", "living-together.html",
         "how-it-works.html", "tutorials.html", "whats-new.html", "faq.html", "join.html",
         "support.html", "share-kit.html", "guides.html", "guide-long-distance-ideas.html", "guide-mental-load.html", "guide-anniversary-planning.html", "privacy.html", "terms.html", "delete-account.html", "404.html"]
PAGES += ["ar/" + p for p in PAGES if p != "404.html"]  # server-rendered Arabic twins
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

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
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

    if not (ROOT / "robots.txt").exists() or not (ROOT / "sitemap.xml").exists():
        errors.append("Missing SEO files")
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    for marker in ('id="founding"', 'data-form="join"', 'data-views="tabs"', 'data-theme-pick='):
        if marker not in index:
            errors.append(f"Missing interactive UI on the homepage: {marker}")
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
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print(f"PASS: {len(parsed)} HTML pages, local links and anchors, descriptions, images and interactive landmarks")


if __name__ == "__main__":
    main()
