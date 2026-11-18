# OneSpace website — approved sitemap, navigation and feature hierarchy

Status: **Implemented in the public website source**, 18 November 2026.
This document records product positioning and navigational ownership. It does not change the original logo, screenshots, interactive demo, tutorial, theme selector or showcases.

## Product positioning

**One app for both of us — to connect, share, discuss, decide, and plan together.**

Emotional connection is essential, but not the differentiator on its own. OneSpace goes beyond familiar relationship features by connecting **smart sharing into unified lists**, **two-way editing**, **conversations anchored to activities**, **comparison of options**, **decisions**, **planning for trips and occasions**, and **budgets**. All of this lives alongside letters, affectionate gestures, daily check-ins and the feelings journal.

Marketing must not claim that competitors categorically lack these features. Describe what OneSpace specifically does and how its workflows connect.

## Top navigation

| Top-level item | Destination | Contents |
|---|---|---|
| Features | Mega menu, `features.html` | Collect & Share, Plan & Decide, Connect & Care |
| Why OneSpace | `compare.html` | The product difference, concrete workflow comparison, no fabricated competitor claims |
| For couples | Mega menu | Living apart (`long-distance.html`), living together (`living-together.html`) |
| Demo | `how-it-works.html` | Existing interactive product demo |
| Learn | Mega menu | Tutorials, guides, FAQ, updates |
| Get the app | `index.html#get-the-app` | Honest Google Play / App Store availability, waitlist |
| Join free | `join.html` | One canonical Founder signup form |

### Features mega menu

| Family | User-facing item | Destination |
|---|---|---|
| Collect & Share | Smart sharing & unified lists | `smart-sharing.html` |
| Collect & Share | Watchlists & music | `watchlists.html` |
| Collect & Share | Lists, reminders & contacts | `everyday.html` |
| Collect & Share | Memories & scrapbooks | `memories.html` |
| Plan & Decide | Compare options together | `decide-together.html` |
| Plan & Decide | Trips & flights | `trips.html` |
| Plan & Decide | Occasions & gifts | `occasions.html` |
| Connect & Care | Love letters | `connect-care.html#letters` |
| Connect & Care | A little love | `connect-care.html#gestures` |
| Connect & Care | Daily check-ins | `connect-care.html#checkins` |
| Connect & Care | Feelings journal | `connect-care.html#journal` |

Keep **Why OneSpace** (competitive/workflow comparison) distinct from **Compare options together** (one of the app's core workflows).

## Home page: protected marketing experiences

Preserve the existing content and working UI:
1. Hero with original logo and official tagline, real screenshots and primary CTA.
2. Product differentiation: smart sharing, two-way editing, decisions and collaborative plans.
3. Existing app tour / recorded clips and screenshots.
4. One list per kind: multi-source sharing, one list for both partners.
5. Connect & Care showcase with real Letters and A Little Love images.
6. **Sound familiar?** examples and problem/solution stories.
7. Existing feature showcases (dates, places, gifts, memories and more).
8. Living together / living apart comparison.
9. Interactive five-tab demo and nine-theme selector; the theme gallery must remain functional.
10. Guides.
11. **AI-generated testing preview only** for testimonials, Google Play, App Store.
12. Realistic store availability and Founder signup.

The exact visual ordering may adapt for UX and performance; none of the protected interactive elements above should be removed.

## Footer (without a Join button)

| Column | Contents |
|---|---|
| Identity | Original official logo, readable OneSpace name, tagline, contact email |
| Product | Features, demo, tutorials, What's new, availability, Founding 500 |
| For couples | Living apart, living together |
| Help | Guides, FAQ, support, can't sign in, Share kit |
| Legal | Privacy policy, terms of use, delete account |

A page's own CTA and the sticky header CTA are sufficient. No duplicate footer Join button.

## Real screenshots and screenshot robot

The website already has real screenshot assets for `assets/app/en/letters.webp`, `assets/app/en/love.webp` and their Arabic equivalents. The new Connect & Care section uses those originals. The check-in and feelings journal sections currently use an existing *general Connect screen* or illustration; they are not passed off as dedicated captures of these features.

A real Android robot workflow exists at `.github/workflows/app-screens.yml` and requires manual GitHub Actions dispatch, access to the private mobile app and configured demo credentials. Once fresh check-in and journal screenshots exist, import them into `assets/app/en` and `assets/app/ar`; ensure captions accurately describe the captured screen. Do not publish screenshots of personal user information. This website iteration did not trigger a robot run.

## Test-only reviews, testimonials, and ratings

The home page has a clearly identified **AI-generated fictional design preview** (`#reviews-preview`). It includes hypothetical testimonial wording and placeholder panels for Google Play and App Store.

- Do not claim these quotes were written by users or infer reviewer names, ages or locations.
- Do not publish fictitious ratings, counts, store review links, verified-buyer badges, `AggregateRating` structured data or misleading star scores.
- Show the text **“TEST ONLY · AI-GENERATED PLACEHOLDERS · NOT REAL CUSTOMER REVIEWS OR RATINGS”** prominently.
- Generated section carries `data-nosnippet` to discourage use in search excerpts.
- Set `SHOW_AI_REVIEW_PREVIEW = False` in `build.py`, rebuild, and the full preview disappears after review.
- Replace content only with real verified user/store feedback and appropriate permissions.

## Localization and guardrails

Website language variants: **English, Arabic, Spanish, French, German**. All five share one canonical HTML structure and assets; native-quality copy is reviewed via `content/locale_editorial.py` and the existing localization system.

`tests/check_site.py` and `tests/check_megamenu.py` verify navigation, screenshots, preservation of the demo/theme selector, protected content, no footer Join button, three actual Smart Sharing steps, and safe AI-preview labels.

**Mobile app:** no Flutter release, APK or store submission is required for this website-focused iteration. Existing mobile Arabic translation remains under separate review.
