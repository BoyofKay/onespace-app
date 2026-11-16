"""OneSpace static-site smoke checks — no external dependencies."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGES = ["index.html", "features.html", "long-distance.html", "living-together.html",
         "tutorials.html", "faq.html", "privacy.html", "terms.html", "support.html",
         "delete-account.html", "404.html"]


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
            if clean == "":
                target = ROOT / name
            elif clean in (".", "./"):
                target = ROOT / "index.html"
            else:
                target = ROOT / clean.removeprefix("./")
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
    for field in ("waitlistForm", "tourAppCards", "themes", "early-access", "tourNext"):
        if f'id="{field}"' not in index:
            errors.append(f"Missing interactive UI: {field}")
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print(f"PASS: {len(parsed)} HTML pages, local links and anchors, descriptions, images and interactive landmarks")


if __name__ == "__main__":
    main()
