"""Publish human-readable GitHub Pages URLs while retaining every legacy .html link.

Directory index files make /privacy/, /faq/ and /ar/privacy/ work on GitHub Pages.
Existing HTML files stay available as navigation bridges, preserving query strings
and URL fragments for Founder invite, confirmation, and unsubscribe tokens.
"""
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
import re

BASE = "https://onespace.live/"
LANGS = ("en", "ar", "es", "fr", "de")
URL_ATTR = re.compile(r'(?P<attr>\b(?:href|src|poster|data-(?:en|ar)-(?:src|poster|href))=)(?P<quote>["\'])(?P<url>.*?)(?P=quote)')
SITE_URL = re.compile(r'https://(?:www\.)?onespace\.live/(?P<path>(?:ar/|es/|fr/|de/)?[a-z0-9-]+\.html)(?=[#?"\'<> ]|$)')


def pretty_path(name, lang="en"):
    prefix = "" if lang == "en" else lang + "/"
    return "/" + prefix + ("" if name == "index.html" else name[:-5] + "/")


def pretty_site_url(name, lang="en"):
    return "https://onespace.live" + pretty_path(name, lang)


def clean_site_link(url, known_names):
    """Rewrite only known page URLs; do not touch assets or external domains."""
    def change(match):
        path = match.group("path")
        parts = path.split("/")
        name, locale = parts[-1], (parts[0] if len(parts) > 1 else "en")
        return pretty_site_url(name, locale) if name in known_names else match.group(0)
    return SITE_URL.sub(change, url)


def rewrite_references(html, name, lang, known_names):
    source = pretty_site_url(name, lang).replace("/" + name[:-5] + "/", "/" + name) if name != "index.html" else pretty_site_url(name, lang)
    # The source URL must use the old /page.html location when resolving relative links.
    source = BASE + ("" if lang == "en" else lang + "/") + name

    def swap(match):
        original = match.group("url")
        if not original or original.startswith(("#", "//", "mailto:", "tel:", "sms:", "data:", "javascript:")):
            return match.group(0)
        parsed = urlsplit(original)
        if parsed.scheme and parsed.netloc not in ("onespace.live", "www.onespace.live"):
            return match.group(0)
        resolved = urlsplit(urljoin(source, original))
        path = resolved.path
        parts = path.strip("/").split("/")
        filename = parts[-1]
        if filename in known_names:
            locale = parts[0] if len(parts) > 1 and parts[0] in LANGS else "en"
            path = pretty_path(filename, locale)
        elif path == "/index.html":
            path = "/"
        if parsed.scheme and parsed.netloc:
            target = urlunsplit(("https", "onespace.live", path, resolved.query, resolved.fragment))
        else:
            target = urlunsplit(("", "", path, resolved.query, resolved.fragment))
        return match.group("attr") + match.group("quote") + target + match.group("quote")

    result = URL_ATTR.sub(swap, html)
    # JSON-LD, translated editorial links and social metadata also use the canonical URLs.
    return clean_site_link(result, known_names)


def publish_pretty_routes(root: Path, pages):
    # Non-public callback pages get working clean routes too, but retain noindex.
    names = set(pages) | {"confirm.html", "unsubscribe.html"}
    for locale in LANGS:
        prefix = Path("") if locale == "en" else Path(locale)
        for name in sorted(names):
            original = root / prefix / name
            if not original.exists():
                raise FileNotFoundError(f"Missing original page: {original}")
            html = original.read_text(encoding="utf-8")
            clean = rewrite_references(html, name, locale, names)
            if name == "index.html":
                # Home pages must use clean links immediately, without a redirect hop.
                original.write_text(clean, encoding="utf-8")
                continue
            destination = root / prefix / name[:-5] / "index.html"
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(clean, encoding="utf-8")
            # Change the source page's canonical so old bookmarks don't create duplicate SEO.
            legacy = clean_site_link(html, names)
            target = pretty_path(name, locale)
            # Inline script at the end of head runs before deferred application JS.
            # location.search and location.hash are preserved, including sensitive
            # Founder confirmation and unsubscribe fragments.
            bridge = "<script>location.replace(" + repr(target) + "+location.search+location.hash)</script>"
            legacy = legacy.replace("</head>", bridge + "</head>", 1)
            original.write_text(legacy, encoding="utf-8")

    for name in ("sitemap.xml", "llms.txt"):
        path = root / name
        path.write_text(clean_site_link(path.read_text(encoding="utf-8"), names), encoding="utf-8")

    robots = root / "robots.txt"
    policy = robots.read_text(encoding="utf-8")
    policy += "".join(
        "Disallow: " + pretty_path(name, lang) + "\n"
        for lang in LANGS
        for name in ("confirm.html", "unsubscribe.html")
    )
    robots.write_text(policy, encoding="utf-8")
    return len(names) * len(LANGS)
