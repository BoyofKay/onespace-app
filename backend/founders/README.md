# Founder Members waitlist — backend (website only)

Runs in the **OneSpace Production** Supabase project (`letcgxbnblohhfyeuigz`, Frankfurt — since 17 Nov 2026; the old project `ugwrpeduzyzrujkizqfo` is now the app's QA backend), isolated from the app: its own `private.founder_*` tables and
`public.founder_*` functions that only the service role can call. Nothing here touches app tables.

| Piece | What it does |
|---|---|
| `0134_founder_members.sql` | Tables (couples, members, email log, attempts) and functions: join, confirm, stats, email log, resend list |
| `functions/founder-join.ts` | `POST /functions/v1/founder-join` — form endpoint: spam traps, rate limits, consent, sends the confirmation email |
| `functions/founder-confirm.ts` | `POST /functions/v1/founder-confirm` — confirmation link; gives the Founder number, sends welcome / partner-joined emails |
| `functions/founder-admin.ts` | `GET/POST /functions/v1/founder-admin` — numbers for the Command Center Website tab (needs `x-admin-key`; the public admin page was retired 17 Nov 2026) |
| `functions/founder-unsubscribe.ts` | One-click unsubscribe (RFC 8058 POST from mail apps; GET redirects to `/unsubscribe.html`) |
| `functions/site-contact.ts` | Support and Delete-account forms: saves the request and emails it to support@ / privacy@ (Reply-To = visitor) |
| `0137_founder_spam_counts.sql` | Spam-protection counters per day (counts only) + `founder_spam_count` / `founder_spam_stats` |
| `0139_ops_secret_status.sql` | Production only: every 30 min stores true/false per Edge secret (from `secrets-check`) in `private.ops_secret_status` for the Command Center |
| `functions/secrets-check.ts` | Health check: which secrets exist (booleans), callable only with the Vault worker secret |
| `functions/_lib.ts` | Shared: Resend sending + delivery log, branded EN/AR email templates, spam protection (`guard`) |

Rules: one Founder number per couple, first 250 confirmed couples (500 people); number given only after the
email is confirmed; a partner joins through `https://onespace.live/join/?invite=<code>` and shares the number.

## Secrets (Supabase › Edge Functions › Secrets — never in the website or GitHub)
- `RESEND_API_KEY` — Resend API key with sending access (domain onespace.live verified in Resend).
- `FOUNDER_ADMIN_KEY` — password for the private dashboard (16+ characters).
- `TURNSTILE_SECRET_KEY` — Cloudflare Turnstile secret for the spam check (site key `0x4AAAAAAGFSBBh0y5giCOsV` is public, in `assets/os.js`).
  Required for website Founder and Support forms. If missing, verification fails closed and users see a retry message; never accept unchecked requests.
- `GOATCOUNTER_TOKEN` (optional) — read-only GoatCounter API key, adds visitors → sign-up rate to the dashboard.

To rotate a key: create the new one in Resend, replace the secret value, then revoke the old key. No redeploy needed.

## Deploy
Functions are deployed with `verify_jwt = false` (public form endpoints); `_lib.ts` is uploaded with each one as `lib.ts`.

## Spam protection
- Hidden `website` field filled (robots only) → answered OK, nothing saved, counted as `honeypot`.
- Every public Founder and Support form requires a fresh Cloudflare Turnstile token verified by Siteverify, including matching the onespace.live hostname.
  Valid token → accepted if database limits allow. Missing token → HTTP 428; invalid/reused/expired token or verification outage → request denied with a retry message. There is no client-timing bypass.
- Nothing is ever discarded silently except the robot field. Counts appear on the admin page and the Command Center Website tab.

## Clean website routes (19 November 2026)

The production confirmation, welcome and follow-up emails now use `/confirm/`, `/join/`, `/privacy/`, and `/unsubscribe/` (with existing token/query fragments preserved). The production `founder-join`, `founder-confirm`, and `founder-unsubscribe` functions were patched from their **current deployed versions** to change only URL targets, because the live function bundles were not identical to the repository source. Avoid overwriting the live bundles from GitHub without a reviewed security/diff reconciliation. The old `.html` links remain compatible through site redirects, so previously sent emails continue to work.
