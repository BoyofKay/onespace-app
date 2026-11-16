import { json, mailConfirm, rpc, send } from './_lib.ts';

// GET  /founder-admin            → waitlist numbers (no email addresses)
// POST /founder-admin {action:'resend_pending'} → send confirmation emails that never went out
// Both need the header x-admin-key = FOUNDER_ADMIN_KEY.
async function same(a: string, b: string): Promise<boolean> {
  const e = new TextEncoder();
  const [x, y] = await Promise.all([crypto.subtle.digest('SHA-256', e.encode(a)), crypto.subtle.digest('SHA-256', e.encode(b))]);
  const u = new Uint8Array(x), v = new Uint8Array(y);
  let d = 0; for (let i = 0; i < u.length; i++) d |= u[i] ^ v[i];
  return d === 0;
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return json(req, {});
  const want = Deno.env.get('FOUNDER_ADMIN_KEY') ?? '';
  if (want.length < 16 || !(await same(req.headers.get('x-admin-key') ?? '', want))) {
    await new Promise((r) => setTimeout(r, 600));
    return json(req, { ok: false, error: 'unauthorized' }, 401);
  }
  try {
    if (req.method === 'POST') {
      const b = await req.json().catch(() => ({}));
      if (b.action === 'resend_pending') {
        const list: any[] = await rpc('founder_pending_to_resend', { p_limit: 50 });
        let sent = 0;
        for (const m of list) if (await send(m.member_id, 'confirm', m.email, mailConfirm(m.language, m.name, m.token, false))) sent++;
        return json(req, { ok: true, attempted: list.length, sent });
      }
      return json(req, { ok: false, error: 'unknown_action' }, 400);
    }
    const days = Math.max(7, Math.min(180, Number(new URL(req.url).searchParams.get('days') ?? 30)));
    const stats = await rpc('founder_stats', { p_days: days });
    stats.mail_key_set = Boolean(Deno.env.get('RESEND_API_KEY'));
    // Optional: visitors from GoatCounter (set GOATCOUNTER_TOKEN, a read-only API key) for a visitors → sign-ups rate.
    const gc = Deno.env.get('GOATCOUNTER_TOKEN');
    if (gc) {
      try {
        const start = new Date(Date.now() - days * 864e5).toISOString().slice(0, 10);
        const r = await fetch(`https://onespace.goatcounter.com/api/v0/stats/total?start=${start}`, { headers: { Authorization: `Bearer ${gc}` } });
        if (r.ok) { const t = await r.json(); stats.visitors = t.total_utc ?? t.total ?? null; }
      } catch { /* optional */ }
    }
    return json(req, { ok: true, stats });
  } catch (e) {
    console.error(e);
    return json(req, { ok: false, error: 'server' }, 500);
  }
});
