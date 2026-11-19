"""Live check: page views and events reach GoatCounter, and no personal data is in them."""
import asyncio
import sys
from urllib.parse import urlsplit, parse_qs

from playwright.async_api import async_playwright

SITE = 'https://onespace.live/'
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
TEST_EMAIL = 'check@example.com'


async def main():
    hits = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--disable-blink-features=AutomationControlled'])
        ctx = await browser.new_context(user_agent=UA, viewport={'width': 1366, 'height': 900}, locale='en-US')
        page = await ctx.new_page()

        async def on_response(r):
            if 'goatcounter.com/count' in r.url:
                q = parse_qs(urlsplit(r.url).query)
                hits.append((r.status, q.get('p', [''])[0], q.get('e', ['false'])[0], r.url))
        page.on('response', lambda r: asyncio.ensure_future(on_response(r)))

        await page.goto(SITE + '?utm_source=onespace-check&utm_medium=qa&utm_campaign=one-space-smoke', wait_until='load')
        await page.wait_for_timeout(2500)
        await page.locator('[data-theme-pick]').nth(1).click()
        await page.locator('[data-views="tabs"] [data-view]').nth(2).click()
        # The homepage is deliberately not a duplicate signup form.
        await page.locator('a[href="/join/"]:visible').first.click()
        await page.wait_for_url('**/join/')
        assert (await page.evaluate("sessionStorage.getItem('os-utm')")).find('onespace-check') >= 0
        assert await page.evaluate("sessionStorage.getItem('os-landing')") == '/'
        form = page.locator('form[data-form="join"]')
        await form.locator('input[name="email"]').fill(TEST_EMAIL)  # never submitted
        await page.wait_for_timeout(1500)
        await page.goto(SITE + 'how-it-works/?utm_source=onespace-check', wait_until='load')
        await page.wait_for_timeout(2000)
        for _ in range(6):
            await page.locator('[data-next="tour"]').click()
        await page.goto(SITE + 'ar/faq/?utm_source=onespace-check', wait_until='load')
        await page.wait_for_timeout(2500)
        await browser.close()

    print(f'{len(hits)} requests to GoatCounter:')
    for status, path, event, _ in hits:
        print(f'  {status}  {"event" if event == "true" else "view "}  {path}')
    problems = []
    if not any(e != 'true' and s < 300 for s, _, e, _ in hits):
        problems.append('no page view was accepted')
    if not any(e == 'true' and s < 300 for s, _, e, _ in hits):
        problems.append('no event was accepted')
    if any(s >= 300 for s, *_ in hits):
        problems.append('some requests were rejected')
    if any(TEST_EMAIL in u or 'check%40example' in u for *_, u in hits):
        problems.append('the typed email address reached GoatCounter')
    if problems:
        print('FAIL: ' + '; '.join(problems))
        sys.exit(1)
    print('PASS: views and events accepted; no personal data sent')

asyncio.run(main())
