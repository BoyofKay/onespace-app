# OneSpace website internationalization

## Full visual and functional parity
- English is the source layout. **Arabic, Spanish, French and German reuse the original website experience.** ES/FR/DE are generated from the complete English HTML DOM in `content/full_localization.py`, not simplified independent landing pages.
- The same app screenshots (currently English/Arabic images), phone frames, interactive walkthroughs, theme controls, comparison tables, guides, legal and support pages, Founder registration, privacy protections, and product sections are retained. **Do not invent translated app screenshots** when only English/Arabic screenshots exist.
- Every page in `PAGES` gets ES/FR/DE counterparts; confirm and unsubscribe pages also exist in all languages and stay `noindex`.
- Original `assets/os.js`, `assets/os.css`, GoatCounter and Founder Supabase functions are shared. Dynamic form and copy feedback is localized via `SITE_MESSAGES` and `FORM_MESSAGES`.

## Translation approach
- Committed language catalogs: `content/translations/es.json`, `fr.json`, `de.json`. Source inventory: `source_catalog.json`.
- English phrases are mapped to translated text nodes and user-facing attributes while preserving all HTML structure, links, event data attributes, media and forms.
- `content/locale_editorial.py` provides cumulative human-authored editorial corrections to high-visibility marketing, navigation, product benefits, support, privacy headlines and tutorials in each language. Review all additions before publishing. `GLOSSARY` handles core app terminology and privacy labels.
- New missing translations make the build **fail**; they do not silently fall back to English. Rebuilds do not call any translation service.
- For future source-copy changes: regenerate English source; run the one-time `scripts/translate_full_site.py` to populate **new** missing keys, review changed language strings, then build. This script translates *public marketing copy only* and is not used in production.
- Style: Spanish broadly understandable, warm and clear; French natural, conversational and polished; German friendly for product marketing, precise for support/privacy language.
- Review proper names, software terms, quantitative claims, privacy and legal wording before each release. English remains the original reference for interpretation of legal terms. Full long-form native-speaker proofreading (especially privacy and terms) is still an outstanding QA milestone; machine-assisted coverage alone must never be described as native-certified.

## SEO, analytics and Founder limitations
- Canonical URLs, reciprocal `hreflang` and XML sitemap cover every indexable page across en/ar/es/fr/de. `x-default` remains English. IndexNow and Google Search Console submissions use the same sitemap.
- GoatCounter continues tracking localized page paths; UTM source, medium and campaign are preserved when switching languages, without sending email/token query strings to GoatCounter.
- The Founder backend currently sends English/Arabic transactional emails only. Localized Founder forms disclose this rather than falsely promising translations of those emails. Email preference is set to English unless the user explicitly selects Arabic.
- Never claim store listings or automatic Counters updates that do not exist in the app.

## QA gate
```sh
python3 -m pip install beautifulsoup4==4.15.0
python3 build.py
python3 tests/check_site.py
node --check assets/os.js
node --check assets/ar.js
```
The site test checks localized links, anchors, metadata, sitemap, privacy and identical counts of screenshots, media, forms, theme selectors, interactive demo components and tracking markers for every translated page.

## Locale-specific UI and brand guidance
- Preserve the original OneSpace design and use compact, natural CTAs instead of stretching navigation for literal long translations. Mobile navigation begins at the language-safe responsive breakpoint.
- Horizontal screenshot/theme rails use OneSpace-colored accessible scrollbars. Do not replace the real app images with generated translations of screenshots.
- The Google Play and App Store cards are **availability previews**, not live download links. Their recognizable in-page platform marks are not official approved download badges. Replace with the officially supplied localized badges and verified store links only once the relevant store listing is available and brand terms permit use.
- Run Chromium browser responsive checks (script `scripts/check_locale_layout.mjs`) at phone, tablet and desktop sizes when adjusting navigation, language copy or store cards.
- For German marketing, address a couple as **ihr/euch** and an individual as **du/dein**; avoid unexplained switches to Sie. For French use **vous** consistently; for Spanish use broadly understood, natural language and distinguish singular visitor versus couple.
- Do not localize proper brand names such as OneSpace, App Store, Google Play, OpenStreetMap, or app navigation identifiers into unrelated words.
