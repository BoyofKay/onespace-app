"""Live end-to-end test of the Founder waitlist form and confirmation page."""
import asyncio
import sys

from playwright.async_api import async_playwright

SITE = 'https://onespace.live/'
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'


async def main(email, token, lang):
    pre = 'ar/' if lang == 'ar' else ''
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-blink-features=AutomationControlled'])
        ctx = await b.new_context(user_agent=UA, locale='ar' if lang == 'ar' else 'en-US', viewport={'width': 1280, 'height': 900})
        page = await ctx.new_page()
        calls = []
        page.on('response', lambda r: calls.append((r.status, r.url)) if 'functions/v1' in r.url or 'goatcounter.com/count' in r.url else None)
        ok = True
        if email:
            await page.goto(f'{SITE}{pre}join.html?utm_source=onespace-check', wait_until='load')
            f = page.locator('form[data-form="join"]')
            await f.locator('input[name="email"]').fill(email)
            await f.locator('input[name="name"]').fill('Check')
            await f.locator('input[name="platform"][value="android"]').check(force=True)
            await f.locator('input[name="consent"]').check(force=True)
            await page.wait_for_timeout(3000)
            await f.locator('button[type=submit]').click()
            await page.wait_for_timeout(6000)
            done = await page.locator('#j-done').is_visible()
            status = await f.locator('.status').inner_text()
            print('form submitted · "check your inbox" shown:', done, '· status text:', repr(status))
            ok &= done
        if token:
            await page.goto(f'{SITE}{pre}confirm.html#t={token}', wait_until='load')
            await page.wait_for_timeout(6000)
            vis = [s for s in ['loading', 'ok', 'waitlist', 'expired', 'invalid'] if await page.locator(f'[data-state="{s}"]').is_visible()]
            num = await page.locator('[data-number]').inner_text()
            inv = await page.locator('[data-invite-url]').input_value()
            print('confirmation page state:', vis, '· number:', num, '· invite link:', inv, '· address now:', page.url)
            ok &= vis == ['ok'] and '#' in page.url is False
        await page.screenshot(path='e2e.png', full_page=False)
        for c in calls:
            print('  ', c[0], c[1].split('?')[0])
        await b.close()
    print('PASS' if ok else 'FAIL')
    sys.exit(0 if ok else 1)

asyncio.run(main(*(sys.argv[1:4] + [''] * 3)[:3]))
