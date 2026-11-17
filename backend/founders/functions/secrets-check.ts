// Health check (deployed to OneSpace Production): reports only WHETHER expected secrets exist (true/false),
// never their values, and with ?admin=1 the same numbers the admin page shows.
// Callable only with the Vault worker secret, i.e. from SQL:
//   select net.http_post('https://letcgxbnblohhfyeuigz.supabase.co/functions/v1/secrets-check', '{}'::jsonb, '{}'::jsonb,
//     jsonb_build_object('x-onespace-push-secret', (select decrypted_secret from vault.decrypted_secrets where name='onespace_push_worker_secret')));
const env = (k: string) => (Deno.env.get(k) ?? '').trim();
const NAMES = ['RESEND_API_KEY', 'FOUNDER_ADMIN_KEY', 'GOATCOUNTER_TOKEN', 'ONESPACE_FIREBASE_SERVICE_ACCOUNT_JSON'];
Deno.serve(async (req) => {
  const url = env('SUPABASE_URL'), key = env('SUPABASE_SERVICE_ROLE_KEY');
  const r = await fetch(`${url}/rest/v1/rpc/push_worker_secret`, { method: 'POST', headers: { apikey: key, Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' }, body: '{}' });
  const secret = r.ok ? String(await r.json()).trim() : '';
  if (!secret || req.headers.get('x-onespace-push-secret') !== secret) return new Response('{"error":"unauthorized"}', { status: 401 });
  const q = new URL(req.url).searchParams;
  if (q.get('admin')) {
    const a = await fetch(`${url}/functions/v1/founder-admin?days=${q.get('days') ?? 30}`, { headers: { 'x-admin-key': env('FOUNDER_ADMIN_KEY'), origin: 'https://onespace.live' } });
    return new Response(await a.text(), { status: a.status, headers: { 'Content-Type': 'application/json' } });
  }
  const out: Record<string, unknown> = {};
  for (const n of NAMES) out[n] = Boolean(env(n));
  return new Response(JSON.stringify(out), { headers: { 'Content-Type': 'application/json' } });
});
