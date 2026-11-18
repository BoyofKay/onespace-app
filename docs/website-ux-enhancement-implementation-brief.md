# OneSpace — Website UX Enhancement Implementation Brief

**Status:** Approved design direction, implementation specification for the next website iteration  
**Date:** 18 November 2026  
**Scope:** Marketing website only; **no Flutter release** or changes to the app's production data.  
**Source of truth:** \`build.py\`, \`assets/os.css\`, \`assets/os.js\`, existing screenshot assets, and the approved website sitemap.  
**Product identity:** **OneSpace · Two of Us. One Space.** Use the **original** symbol and wordmark artwork unchanged.

## 1. Objective and positioning

### Hero/value proposition

**Headline:** “Stay close. Build a life together.”  
**Subheadline:** “One private space for two people to share ideas, talk through options, make decisions, plan what’s next, and keep the little moments that matter.”  
**Supporting line:** “For couples living together or miles apart.”  
**Actions:** “Explore how it works” → \`how-it-works.html\`; “Join free” → \`join.html\`.

**Core differentiation:** Emotional-connection features are the foundation, not the unique selling point on their own. OneSpace goes **beyond letters, gestures, and check-ins** by connecting **smart share, unified collective lists, two-way editing, in-context discussion, side-by-side comparisons, decisions, follow-ups, trips, occasions and budgets**. Phrase competitive claims positively; do not assert other products lack capabilities without verified evidence.

**Signature line for the “Why OneSpace” section:**  
“More than staying connected. A shared life, organized together.”  
**Explainer:** “A love note brings you closer. OneSpace also gives you a place to save the link you found, compare your options, discuss the details, decide together, and turn that decision into a plan.”

### Non-negotiable preservation rules

Do **not** remove, replace, or reduce:
- Official OneSpace logo, brand identity, tagline, fonts already chosen and theme colors.
- Existing real app screenshots or phone-frame demonstrations.
- Recorded product tour, tutorial pages and their navigation.
- Interactive demo workflow and its existing step-specific real screenshots.
- Working nine-theme selector, five-tab interactive homepage, and theme showcases.
- “Sound familiar?” problem/solution examples.
- One-list-per-kind / Smart Share explainer and existing feature showcases.
- Responsive RTL Arabic and English, Spanish, French and German website copies.
- Founder signup flow, single canonical form, legal pages, SEO metadata, original app availability wording.

The new elements are **additions or refinements**, not grounds for redesigning everything else.

## 2. Navigation and sitemap (retain approved)

| Primary navigation | Content |
|---|---|
| **Features** | Three mega-menu groups: **Collect & Share**, **Plan & Decide**, **Connect & Care** |
| **Why OneSpace** | Competitive positioning and connected workflows (\`compare.html\`) |
| **For couples** | Living apart / Living together |
| **Demo** | Guided six-step product wizard (\`how-it-works.html\`) |
| **Learn** | Tutorials, guides, FAQ, updates |
| **Get the app** | Honest Google Play / App Store availability |
| **Join free** | Single Founder signup (\`join.html\`) |

**Features mega menu:**
- **Collect & Share:** Smart Sharing & Unified Lists; Watchlists & Music; Lists, Reminders & Contacts; Memories & Scrapbooks.
- **Plan & Decide:** Compare Options Together; Trips & Flights; Occasions & Gifts.
- **Connect & Care:** Love Letters; A Little Love; Daily Check-ins; Feelings Journal.

Add **Global Search** and **Notifications** prominently to the Features page as *cross-cutting product capabilities*, not cluttering the mega menu. Keep “Compare options together” distinct from the “Why OneSpace” competitive explanation.

## 3. Homepage — refined editorial sequence

Maintain **all existing showcase sections** while clarifying the visual hierarchy. Preferred storytelling sequence and exact copy:

| Block | Heading | Short supporting copy | Visual treatment |
|---|---|---|---|
| Hero | **Stay close. Build a life together.** | One private space for two people to share, discuss, decide, plan, and remember. | Existing official mark, actual app devices; no substituted assets |
| Differentiation | **More than staying connected. A shared life, organized together.** | What you find becomes a shared idea. What you discuss becomes a decision. What you decide becomes a plan. | Existing restrained editorial four-part layout |
| Smart Share | **Share from anywhere. Find it together.** | Turn scattered links, places, watchlists, and ideas into one shared destination for each kind of item. | Preserve existing one-list-per-kind demonstration |
| Planning/decisions | **From “what do you think?” to “we’ve decided.”** | Compare options side by side, add both perspectives, discuss with context and keep the decision linked to the next step. | Reuse activity/decision screenshot |
| Connect & Care | **A little love, and a lot of life together.** | Letters, gestures and daily check-ins keep you close. Shared plans, discussions and decisions carry you forward. | Retain genuine Letters / Love Gestures screenshots |
| “Sound familiar?” | **Love is easy. Logistics aren’t.** | Small everyday problems, solved without losing the conversation. | **Protect current cards/interaction** |
| Product showcase | **Familiar ideas, thoughtfully extended.** | The details work together: calendars, memories, trips, occasions, dates, lists. | **Protect current feature showcases** |
| Living arrangement | **Apart or together, OneSpace fits your life.** | The right information for where and how you live. | **Protect existing living-mode toggle** |
| Interactive preview | **Five tabs. Nine moods. One shared space.** | Explore the real product layout and switch its look. | **Protect existing five-tab & nine-theme experience** |
| Smart utilities | **Find it fast. Know what matters.** | Global search recovers the right detail; contextual notifications help you act on it. | Two editorial rows with real screens |
| Testimonials | **A glimpse of what couples might say.** | Illustrative quotes for layout review only. | 2.5-card swipe carousel, **fictional AI test data** |
| Store proof preview | **App ratings & reviews — layout preview.** | Example interface only; official store data isn't published here yet. | Google Play / App Store panels; no deceptive ratings |
| Store availability | **Your Space, soon on your phone.** | Android early access, iPhone planned; link only to real waitlist until stores go live. | **Protect existing logos/status text** |
| Founder signup | **Be among the first 250 couples.** | One Founder number for two people. | Existing single canonical form CTA |

Placement may vary if responsive constraints require, but the protected blocks must remain.

## 4. Demo page — six-step guided wizard

**Route:** \`how-it-works.html\`. Reuse all six existing views and existing real app screenshot switching; do not build a fake app simulator.

**Eyebrow:** “TRY ONESPACE TOGETHER”  
**H1:** “One idea. Two perspectives. One shared plan.”  
**Lead:** “Follow a real example, from something that needs attention to a decision and a small moment of affection. Explore at your own pace.”

**Desktop layout:** two columns, approximately **42% controls / 58% device preview**. Left side includes progress label, a **2 × 3 grid** of compact selectable step tabs (at widths ≥ 1080px) or a single-column vertical list if the available width would force text overflow. Right side holds one prominent phone and a short caption. This avoids the current six oversized stacked cards. Do **not** use side-by-side long explanations in every tab.

**At a glance:** “Step 2 of 6” with accessible \`<progress>\` or \`aria-valuenow/min/max\` status and a slim coral progress track.

**Exact six tab labels and descriptions:**

| Step | Tab label | Active detail |
|---|---|---|
| 1 | **Notice what matters** | “See what needs your attention in Today.” |
| 2 | **Save the idea** | “Capture the idea in a shared note so it doesn’t get lost.” |
| 3 | **Compare the options** | “Move into Coordinate and collect links, prices and possibilities.” |
| 4 | **Talk it through** | “Discuss the options right next to them, with both opinions in context.” |
| 5 | **Decide and follow up** | “Record your choice and keep next steps, reminders and dates linked.” |
| 6 | **Stay close** | “Finish with a thoughtful gesture, because planning isn’t all you share.” |

**Wizard behavior:** Select any step; it updates the selected style, title, detailed copy, progress, phone screenshot and URL hash (\`#step-1\` … \`#step-6\`) without reloading. Provide **Previous** and **Next** buttons. On step 1, Previous is disabled; on step 6, Next becomes **“Explore again”** and resets explicitly (no unexpected circular loop). Support arrow-key navigation, Enter/Space, clear focus, \`aria-selected\`, \`aria-controls\`, and accessible announcements when the displayed view changes.

**Theme selector:** clearly separate from navigation, under heading **“Make it yours”**, subtitle “Try a theme without changing the story.” Arrange all **nine existing themes** into equal-width chips (desktop 3 columns; tablet 3 columns; narrow mobile 2 columns). A swatch and label must not wrap awkwardly or change chip height. Selected theme has a visible ring plus \`aria-pressed\`; minimum touch target 44px. Keep all current theme keys, screenshot behavior, and theme-switching logic. Changing the theme must **not** reset wizard progress.

**Mobile:** single column; progress + active step first, phone second, navigation third. Step tabs may be a horizontal scrollable row with a clear active state rather than a cramped 2 × 3 grid. Ensure long German/French labels do not overflow.

**CTA:** after the demo, one restrained “Join early access” CTA; avoid stacking multiple Join buttons in the wizard itself.

## 5. Global Search and Notifications — new cross-feature showcase

**Section eyebrow:** “SMALL DETAILS, BIG DIFFERENCE”  
**H2:** “Find it fast. Know what matters.”  
**Lead:** “The important details shouldn’t disappear into long conversations.”

### Global Search

**Feature title:** “One search across your shared space.”  
**Copy:** “Remember the link, place, note or decision—but not where it was saved? Use OneSpace’s in-app global search to find what you need without hunting through every feature.”  
**Bullets:** “Search from one place”; “See results with their context”; “Open the original item directly.”

**Disclosure:** Search categories and permissions must be checked against the actual mobile build. Do not claim search covers letters, message bodies, attachments or every private field unless verified by app QA. Search results should respect **Shared / Only me** privacy. When confirmed, list actual indexed object types on the website.

**Screen:** Dedicated real \`global_search.webp\` screenshot still needs capturing. Use the current general search explanation with a neutral empty screenshot frame or omit the visual until captured; do not relabel a different screenshot as Search.

### Notifications

**Feature title:** “Notifications with context, not noise.”  
**Copy:** “Know who shared something, what changed and which decisions or reminders need your attention. Open the relevant item instead of searching for it later.”  
**Bullets:** “Who, what and when”; “Grouped updates”; “A direct path to what needs attention.”

**Screen:** Reuse existing real \`assets/app/en/notifications.webp\` (and Arabic if present) in the phone frame. Validate the explanation against the current notification center and only promise behavior actually implemented.

**Placement:** homepage editorial pair after the existing theme showcase, plus dedicated “Search & Notifications” section on \`features.html\`. Neither feature replaces the Today/Remember/Coordinate/Connect/Me stories.

## 6. Love-gesture popup and additional captures

**Existing genuine assets:** \`assets/app/en/letters.webp\`, \`assets/app/en/love.webp\`, \`assets/app/en/notifications.webp\`. Arabic counterparts must be checked before use.

**Capture required:** Love Gesture **popup/modal**, global search, and (if available) focused daily check-in + feelings journal screens.

**Required popup composition:** Keep the current real Love Gesture tab screenshot as the main device; show a **second, smaller real screenshot** of the gesture opened, overlaid/offset by about 16–24px. Label:
- “Choose a gesture” — the tab/gallery.
- “Make it personal” — popup with gesture text, optional message and send action, **only if those controls exist in the captured build**.

Do not recreate a screenshot with CSS or AI and present it as real.

**Robot:** Existing GitHub Actions screenshot workflow \`.github/workflows/app-screens.yml\` is **manual dispatch**. It builds the private Flutter app and runs a demo-couple emulator against \`integration_test/screenshots_test.dart\`, publishing outputs to the \`app-screens\` branch. Verify that the screenshot script actually supports the extra states; extend robot steps if needed, then run only with the fictional Omar/Lina demo environment. Never expose production accounts or private content. Import approved EN and AR captures through the existing importer; no mobile release is needed.

**Fallback:** If a capture cannot be produced, ship accurate text and existing screenshots, leaving a labeled image slot for later; do not delay the rest of the site iteration.

## 7. Testimonials — compact peek carousel

**Eyebrow:** “DESIGN PREVIEW · AI-GENERATED EXAMPLES”  
**H2:** “A glimpse of what couples might say.”  
**Subheading:** “Illustrative examples only. These are not real user testimonials.”

**Desktop behavior:** **2.5 cards visible** in the viewport (two whole cards, a third peeking in). Tablet: 1.6–2 cards. Mobile: 1.15 cards. Support drag/swipe, visible Previous/Next arrows, pagination dots, keyboard operation, and a progress indicator. No forced auto-rotation; respect reduced motion. Keep carousel height stable across quotes.

**Card:** short quote (≤ 25 words), context label (“Long-distance”, “Living together”, “Planning a trip”), and permanently visible **“AI-generated test example”** caption. Do not add invented human names, portraits, star ratings or “verified” badges.

**Exactly four sample quotes (fictional):**
1. “We kept sending each other links. Now our shortlist lives in one place.” — Long-distance.
2. “We can discuss different options and actually remember what we decided.” — Living together.
3. “Our trip ideas, packing list and decisions finally have a place together.” — Planning a trip.
4. “The sweet messages are still there, alongside everything we need to plan.” — Long-distance.

Use editorial cards and a subtle partial-card peek; avoid oversized testimonial blocks.

## 8. App reviews and ratings — responsible testing-only layout

**Eyebrow:** “TEST ONLY — AI-GENERATED DESIGN PREVIEW”  
**H2:** “App ratings & reviews.”  
**Subheading:** “This is a design prototype, not verified Google Play or App Store data.”

**Two side-by-side store panels** (stack on mobile), each containing:
- Official platform icon and correct store name.
- Overall score **out of 5**.
- Number of ratings/reviews.
- Downloads/installs if the platform provides trustworthy public data.
- **Five-row histogram** (5★ to 1★) with percentage or count labels.
- A short review excerpt region that can show an authentic review later.
- Optional “View on Google Play / App Store” link **only when a verified live store listing exists**.

**Before launch:** show \`—\` and **“Not available yet”** instead of fictional live metrics. Show gray empty histogram tracks with captions “Awaiting verified data.” Keep visual completeness through layout, not fabricated numeric scores.

**Optional internal prototype mode:** Simulated example metrics (such as “SAMPLE 4.8 / 5”, “SAMPLE 128 reviews”, “SAMPLE 10K downloads”, with 82/11/4/2/1 percentage bars) may be used only inside a **clearly watermarked test-only preview**, never as production store results. Label **every simulated number**, not just the section header. Do not publish fake \`AggregateRating\` or review schema data. For Apple, do not assume Apple publishes download counts; if unavailable, show \`—\` even after launch.

**Required permanent preview disclosure (all languages):**  
“**TEST ONLY — AI-GENERATED PLACEHOLDER CONTENT. THESE ARE NOT REAL CUSTOMER TESTIMONIALS, REVIEWS OR APP-STORE RATINGS.**”

**Gating:** Keep the existing \`SHOW_AI_REVIEW_PREVIEW\` toggle in \`build.py\`. This controls the whole review/testimonial section without deleting the component code; configure it off when design approval is finished. Do not use examples in SEO metadata, social preview snippets, search review snippets or paid marketing.

## 9. Footer — social media placeholders

Keep existing readable original OneSpace identity. Do **not** add another Join button.

**Footer columns:**
1. **Product:** Features, Demo, Tutorials, What’s new, Availability, Founding 500.
2. **For couples:** Living apart, Living together.
3. **Help & Resources:** Guides, FAQ, Contact & Support, Can’t sign in?, Share Kit.
4. **Legal:** Privacy, Terms, Delete Account.

**Social placeholder row:** Place compact official-style icons under the footer brand/email, in one line wrapping as needed: **Instagram, Facebook, YouTube, TikTok, LinkedIn**. Labels/hover or focus text: **“Coming soon”**. While URLs are unknown, render **non-interactive placeholders** with a disabled appearance and accessible text—not dead \`href="#"\` links, fabricated profile URLs or clickable inert controls. Once authentic channels exist, turn those placeholders into real links with \`rel="noopener noreferrer"\`.

## 10. Type scale and UI system

Use a single responsive typography hierarchy in \`assets/os.css\`, scoped consistently across marketing pages. Keep existing **Inter** for Latin and **IBM Plex Sans Arabic** for Arabic. Do not change the official logo or redesign the brand typeface.

| Token | Desktop | Tablet | Mobile | Recommended line-height |
|---|---:|---:|---:|---:|
| Display / Hero H1 | 56px | 46px | 34px | 1.10–1.18 |
| H2 / Section | 40px | 34px | 28px | 1.16–1.25 |
| H3 / Feature | 25px | 23px | 21px | 1.25–1.35 |
| H4 / Card | 19px | 18px | 18px | 1.3–1.4 |
| Lead copy | 19px | 18px | 17px | 1.55–1.7 |
| Body | 16px | 16px | 16px | 1.6–1.75 |
| Supporting text | 14px | 14px | 14px | 1.5–1.6 |
| Eyebrow/metadata | 12–13px | 12–13px | 12px | 1.45–1.6 |
| Button label | 15px | 15px | 15px | 1.3–1.45 |

Implement via CSS custom properties and \`clamp()\`, minimizing page-specific inline font declarations. For Arabic, use natural line heights (often 1.65+) and **no letter-spacing on Arabic text**. Nav dropdown labels must not exceed the size of top-level nav. Text buttons should grow modestly in width or wrap to two balanced lines—not become enormous blocks. Maintain accessible contrast, 44px touch targets, stable heights, real focus styles and consistent container radius.

## 11. Responsive, accessibility and UX tests

**Viewport targets:** 360, 390, 768, 1024 and 1440px; EN + Arabic RTL plus ES/FR/DE long labels.

**Functional checks:**
- Demo: exactly six distinct steps; Next/Previous; progress and phone change in sync; final state explicit; hash/deep link restores selection; no unexpected theme reset.
- Theme selector: exactly nine existing selectable themes, consistent grid/chip dimensions, all current theme assets preserved.
- Testimonials: 2.5 desktop cards (visible peek), swipe, arrows, dots and accessible keyboard navigation; no forced autoplay.
- Ratings: two separate platform panels, metric count fields and 5-row breakdown; no fabricated production values; visible AI/test disclaimer; no review schema.
- Global Search: screenshot verified as actual app screen; exact object coverage checked and no exposure of private entries.
- Notifications: original real screenshot reused; action labels and actual behavior verified.
- Love Gesture: existing gallery screenshot plus genuine popup screenshot, when captured, with truthful captions.
- Footer: real wordmark contrast on dark background, no footer Join button, social placeholders clearly unavailable, link categories correct.
- Home: original screenshot section, recorded clips, tutorials, interactive five-tab demo, all nine themes, Sound familiar?, and showcases remain accessible and functional.
- Translation: no missing EN/AR/ES/FR/DE strings; natural localization and RTL alignment. Localize all new labels and data disclaimers, not just headings.
- Quality: no horizontal overflow, clipped CTAs, giant translated buttons, inaccessible icons, broken links, broken image assets or console exceptions.

**Technical integration:** \`build.py\` (page generation), \`assets/os.js\` (wizard & carousel behavior), \`assets/os.css\` (type scale/layout), \`content/locale_editorial.py\` / existing translation catalogs, \`tests/check_site.py\` / \`tests/check_megamenu.py\`; existing screenshot workflow and importer.

## 12. Delivery sequence

**A. Protect and baseline:** Document all preserved screenshot URLs, sections and theme keys; run current site CI, no redesign of the mark.

**B. Demo + typography:** New guided wizard and aligned 9-theme grid; unified type scale; validate all five locales.

**C. Product storytelling:** Add Global Search and Notifications copy + real Notifications screenshot; keep existing Connect & Care; prepare love popup composition.

**D. Social proof preview:** Replace oversized testimonial block with 2.5-card carousel; add structured but explicitly fictional testing reviews with 5-row rating breakdown and honest empty metrics; include one central test toggle.

**E. Footer:** Add disabled/coming-soon social placeholders; keep correct link grouping.

**F. Capture and QA:** Extend/rerun screenshot robot as required for popup, search, check-in and journal; validate genuine captures; build/regenerate five locales, run automated and keyboard/responsive checks, deploy website only after tests pass.

**Definition of done:** All changes above pass checks, every protected section survives, screenshots used are genuine, store proof is clearly testing-only, no fake social accounts or ratings appear as live data, and no mobile app release is triggered.

---

**Important scope note:** This document is an implementation specification; writing or approving it does **not** mean the visual changes, screenshot robot runs or runtime QA described above have been performed yet.
