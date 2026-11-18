# Production Supabase security advisory triage — 2026-11-18
Project: `letcgxbnblohhfyeuigz` (OneSpace production). **Audit only: no destructive database changes.**

## Latest observations (from live advisor / schema introspection)
- 2 WARN — `anon_security_definer_function_executable`: `log_client_error` and `submit_public_support`. Both are deliberately callable before sign-in for error reporting and support; removing access now would break those flows. Both are `SECURITY DEFINER` with `search_path = ''`. They need targeted abuse testing and rate-limit review, not dismissal.
- 20 WARN — `authenticated_security_definer_function_executable`, 18 distinct authenticated-only routines plus the 2 public routines also callable while signed in. Every signed-in routine exposed by the advisor was found to have an `auth.uid()` reference **except** `submit_public_support`, which is intentionally public. However, a textual check does not prove correct per-resource authorization, so individual IDOR/RLS tests remain necessary.
- 11 INFO — `rls_enabled_no_policy`: 9 internal `private` tables plus `public.client_errors` and `public.public_support_requests`. Verified for each one: RLS enabled, **anon and authenticated have neither SELECT nor INSERT table grants**. No direct browser table access, by design. These are not missing public-read policies to add; adding one would weaken security.
- Website CI: CSP/referrer protections, no privileged frontend API keys, safe external links, five-language link tests, server-side Cloudflare Turnstile fail-closed, Turnstile expected host binding and no bypass flags. Edge source and deployed functions both show the fail-closed guard. This is not a penetration test.

## Immediate risk priorities
1. Review public `submit_public_support`: accepts free-text inputs via a definer RPC with global 30/hour and per-email 3/hour guard. The global guard can be an availability bottleneck during abuse; add independent IP/device and product-level protection before advertising high volumes. Ensure maximum subject/message/diagnostics lengths and stored PII minimization. Keep unauthenticated help available.
2. Review public `log_client_error`: globally throttled to 500/hour and per-user to 40/hour; anonymous users share the global limit. Rate-limit by source if safe and remove unnecessary sensitive data from stack traces.
3. Test all 18 signed-in definer RPCs with two distinct accounts, crossing ownership boundaries. Particular priority: `create_scrapbook`, `invite_scrapbook_partner`, `remove_scrapbook_page`, `record_activity_decision`, `create_trip_preparation_checklist`, `register_push_device`, `respond_to_reminder`, and `export_my_data`.
4. Preserve intended APIs. Do **not** revoke all execute privileges, remove RLS, or grant broad table policies merely to clear linter messages.
5. Re-run Supabase security advisors and app regression tests after any database change; document whether remaining warnings are accepted by design.

## Why the warnings remain
The linter identifies the risk category of an exposed elevated-privilege function, not proof that an unauthorized database row is accessible. Testing authorization for each callable function and its arguments requires a deliberate acceptance suite. Unverified warnings are therefore **open for review**; not reported as closed.

Supabase references:
- https://supabase.com/docs/guides/database/database-linter?lint=0028_anon_security_definer_function_executable
- https://supabase.com/docs/guides/database/database-linter?lint=0029_authenticated_security_definer_function_executable
- https://supabase.com/docs/guides/database/database-linter?lint=0008_rls_enabled_no_policy
