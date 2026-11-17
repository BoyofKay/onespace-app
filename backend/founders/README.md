# Founder Members waitlist — backend (website only)

Runs in the **OneSpace Production** Supabase project (`letcgxbnblohhfyeuigz`, Frankfurt — since 17 Nov 2026; the old project `ugwrpeduzyzrujkizqfo` is now the app's QA backend), isolated from the app: its own `private.founder_*` tables and
`public.founder_*` functions that only the service role can call. Nothing here touches app tables.

| Piece | What it does |
|---|---|
| `0134_founder_members.sql` | Tables (couples, members, email log, attempts) and functions: join, confirm, stats, email log, resend list |
| `functions/founder-join.ts` | `POST /functions/v1/founder-join` — form endpoint: spam traps, rate limits, consent, sends the confirmation email |
| `functions/founder-confirm.ts` | `POST /functions/v1/founder-confirm` — confirmation link; gives the Founder number, sends welcome / partner-joined emails |
| `functions/founder-admin.ts` | `GET/POST /functions/v1/founder-admin` — numbers for `/founders-admin.html` (needs `x-admin-key`) |
| `functions/founder-unsubscribe.ts` | One-click unsubscribe (RFC 8058 POST from mail apps; GET redirects to `/unsubscribe.html`) |
| `functions/site-contact.ts` | Support and Delete-account forms: saves the request and emails it to support@ / privacy@ (Reply-To = visitor) |
| `functions/_lib.ts` | Shared: Resend sending + delivery log, branded EN/AR email templates |

Rules: one Founder number per couple, first 250 confirmed couples (500 people); number given only after the
email is confirmed; a partner joins through `join.html?invite=<code>` and shares the number.

## Secrets (Supabase › Edge Functions › Secrets — never in the website or GitHub)
- `RESEND_API_KEY` — Resend API key with sending access (domain onespace.live verified in Resend).
- `FOUNDER_ADMIN_KEY` — password for the private dashboard (16+ characters).
- `GOATCOUNTER_TOKEN` (optional) — read-only GoatCounter API key, adds visitors → sign-up rate to the dashboard.

To rotate a key: create the new one in Resend, replace the secret value, then revoke the old key. No redeploy needed.

## Deploy
Functions are deployed with `verify_jwt = false` (public form endpoints); `_lib.ts` is uploaded with each one as `lib.ts`.
