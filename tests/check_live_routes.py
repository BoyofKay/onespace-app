"""Read-only real-network smoke test for live canonical GitHub Pages routes."""
import sys
import urllib.request
from html.parser import HTMLParser

ROOT = "https://onespace.live"
CHECKS = {
    "/": "/",
    "/privacy/": "/privacy/",
    "/terms/": "/terms/",
    "/delete-account/": "/delete-account/",
    "/support/": "/support/",
    "/faq/": "/faq/",
    "/guides/": "/guides/",
    "/tutorials/": "/tutorials/",
    "/features/": "/features/",
    "/join/": "/join/",
    "/ar/privacy/": "/ar/privacy/",
    "/es/faq/": "/es/faq/",
    "/fr/terms/": "/fr/terms/",
    "/de/delete-account/": "/de/delete-account/",
    "/confirm/": "/confirm/",
    "/unsubscribe/": "/unsubscribe/",
}
LEGACY = {"/privacy.html": "/privacy/", "/terms.html": "/terms/",
          "/delete-account.html": "/delete-account/", "/faq.html": "/faq/",
          "/join.html": "/join/", "/confirm.html": "/confirm/",
          "/unsubscribe.html": "/unsubscribe/"}


class Head(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonical = ""
        self.noindex = False

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == "link" and attr.get("rel") == "canonical":
            self.canonical = attr.get("href", "")
        if tag == "meta" and attr.get("name") == "robots":
            self.noindex = "noindex" in attr.get("content", "").lower()


def get(path):
    req = urllib.request.Request(ROOT + path, headers={"User-Agent": "OneSpaceWebsiteLiveRouteCheck/1.0"})
    with urllib.request.urlopen(req, timeout=20) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.status, response.read().decode(charset, "replace")


failures = []
for path, canonical in CHECKS.items():
    try:
        status, html = get(path)
        head = Head()
        head.feed(html)
        expected = ROOT + canonical
        if status != 200 or head.canonical != expected or "OneSpace" not in html:
            failures.append(f"{path}: status={status}, canonical={head.canonical}")
        if path in ("/confirm/", "/unsubscribe/") and not head.noindex:
            failures.append(f"{path}: expected noindex")
        print(f"{path}: {status} canonical={head.canonical}")
    except Exception as error:
        failures.append(f"{path}: {type(error).__name__}: {error}")

for old, new in LEGACY.items():
    try:
        status, html = get(old)
        expected = "location.replace('" + new + "'+location.search+location.hash)"
        if status != 200 or expected not in html:
            failures.append(f"{old}: legacy redirect does not preserve search and hash")
        print(f"legacy {old} => {new}: {status}")
    except Exception as error:
        failures.append(f"{old}: {type(error).__name__}: {error}")

for path in ("/assets/os.css", "/assets/os.js"):
    try:
        status, _ = get(path)
        if status != 200:
            failures.append(f"{path}: status={status}")
    except Exception as error:
        failures.append(f"{path}: {type(error).__name__}: {error}")

if failures:
    for item in failures:
        print("FAIL:", item, file=sys.stderr)
    raise SystemExit(1)
print(f"PASS: {len(CHECKS)} live clean routes, {len(LEGACY)} legacy routes, and 2 assets")
