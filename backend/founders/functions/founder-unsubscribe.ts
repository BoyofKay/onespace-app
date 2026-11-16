import { SITE, cors, json, rpc } from './_lib.ts';

// Unsubscribe from Founder emails.
// POST (one-click from the mail app, RFC 8058, or from onespace.live/unsubscribe.html) → unsubscribes.
// GET (someone clicked the header link) → sends them to the page with a button, so link scanners can't unsubscribe people.
Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return json(req, {});
  const url = new URL(req.url);
  let token = url.searchParams.get('u') ?? '';
  if (req.method === 'GET') {
    return new Response(null, { status: 302, headers: { ...cors(req), Location: `${SITE}/unsubscribe.html#u=${encodeURIComponent(token)}` } });
  }
  if (!token) { try { token = String((await req.json()).u ?? ''); } catch { /* one-click form body */ } }
  try {
    const r = await rpc('founder_unsubscribe', { p_token: token });
    return json(req, { ok: r.status === 'unsubscribed', status: r.status }, r.status === 'unsubscribed' ? 200 : 400);
  } catch (e) {
    console.error(e);
    return json(req, { ok: false, status: 'server' }, 500);
  }
});
