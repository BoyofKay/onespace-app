import { SITE, json, mailPartnerJoined, mailWelcome, rpc, send } from './_lib.ts';

// POST /founder-confirm {token} — the link in the confirmation email. Founder status is given here,
// once the email is proven, and the welcome email goes out once.
Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return json(req, {});
  if (req.method !== 'POST') return json(req, { ok: false }, 405);
  let token = '';
  try { token = String((await req.json()).token ?? ''); } catch { /* empty */ }
  try {
    const r = await rpc('founder_confirm', { p_token: token });
    if (r.status === 'confirmed') {
      await send(r.member_id, 'welcome', r.email, mailWelcome(r.language, r, r.first_member?.name ?? ''), r.unsub);
      if (r.partner_joined && r.first_member && !r.first_member.unsubscribed) {
        await send(r.first_member.member_id, 'partner_joined', r.first_member.email,
          mailPartnerJoined(r.first_member.language, r.first_member.name, r.name), r.first_member.unsub);
      }
    }
    if (r.status !== 'confirmed' && r.status !== 'already') return json(req, { ok: false, status: r.status });
    const lang = r.language === 'ar' ? 'ar/' : '';
    // founder_number is only read by the confirm page before PR #48 (which stops showing it); remove after that merges.
    return json(req, { ok: true, status: r.status, founder_number: r.founder_number, couple_status: r.couple_status,
      role: r.role, couple_full: r.couple_full, invite_url: `${SITE}/${lang}join/?invite=${r.invite_code}` });
  } catch (e) {
    console.error(e);
    return json(req, { ok: false, status: 'server' }, 500);
  }
});
