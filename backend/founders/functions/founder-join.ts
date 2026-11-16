import { json, ipHash, mailAlready, mailConfirm, rpc, send } from './_lib.ts';

// POST /founder-join — the Founder Members form. Answers the same way whether or not the email is
// already registered, so the form can't be used to find out who has signed up.
Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return json(req, {});
  if (req.method !== 'POST') return json(req, { ok: false, error: 'method' }, 405);
  let b: any;
  try { b = await req.json(); } catch { return json(req, { ok: false, error: 'bad_request' }, 400); }
  // Spam traps: a hidden field people never see, and forms sent faster than a person can type.
  if (b.website || (typeof b.elapsed === 'number' && b.elapsed < 2500)) return json(req, { ok: true });
  const s = (v: unknown, n: number) => String(v ?? '').slice(0, n);
  const utm: Record<string, string> = {};
  for (const k of ['utm_source', 'utm_medium', 'utm_campaign']) if (b.utm?.[k]) utm[k] = s(b.utm[k], 60);
  try {
    const r = await rpc('founder_join', { p: {
      email: s(b.email, 254), name: s(b.name, 60), platform: s(b.platform, 10), living: s(b.living, 10),
      language: b.language === 'ar' ? 'ar' : 'en', source: s(b.source, 40), note: s(b.note, 1500),
      landing: s(b.landing, 200), referrer: s(b.referrer, 200), utm, invite: s(b.invite, 20),
      consent: b.consent === true, ip_hash: await ipHash(req),
    } });
    switch (r.status) {
      case 'pending':
        await send(r.member_id, 'confirm', r.email, mailConfirm(r.language, r.name, r.token, r.partner_invite), r.unsub);
        return json(req, { ok: true });
      case 'already':
        if (r.send && !r.unsubscribed) await send(r.member_id, 'already', r.email, mailAlready(r.language, r), r.unsub);
        return json(req, { ok: true });
      case 'pending_recent':
        return json(req, { ok: true });
      default: // invalid_email, consent_required, rate_limited
        return json(req, { ok: false, error: r.status }, r.status === 'rate_limited' ? 429 : 422);
    }
  } catch (e) {
    console.error(e);
    return json(req, { ok: false, error: 'server' }, 500);
  }
});
