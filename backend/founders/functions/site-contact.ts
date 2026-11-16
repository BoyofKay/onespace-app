import { json, rpc, sendInternal } from './_lib.ts';

// POST /site-contact — the Support and Delete-account forms on onespace.live.
// Saves the request (same table and limits as before) and emails it to support@ or privacy@,
// with Reply-To set to the visitor so we answer from Zoho.
Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return json(req, {});
  if (req.method !== 'POST') return json(req, { ok: false }, 405);
  let b: any;
  try { b = await req.json(); } catch { return json(req, { ok: false, error: 'bad_request' }, 400); }
  if (b.website || (typeof b.elapsed === 'number' && b.elapsed < 2500)) return json(req, { ok: true });
  const s = (v: unknown, n: number) => String(v ?? '').trim().slice(0, n);
  const email = s(b.email, 254);
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]{2,}$/.test(email)) return json(req, { ok: false, error: 'email' }, 422);
  const account = b.form === 'account';
  const topic = s(b.topic, 20);
  const kind = account ? 'account' : topic === 'issue' ? 'issue' : topic === 'signin' ? 'account' : 'contact';
  const subject = account ? 'Delete my account' : s((topic ? topic + ' · ' : '') + (s(b.subject, 120) || 'Website message'), 160);
  const message = s(b.message, 4000);
  if (!message) return json(req, { ok: false, error: 'missing' }, 422);
  const name = s(b.name, 60);
  try {
    await rpc('submit_public_support', { p_kind: kind, p_subject: subject, p_message: (name ? `Name: ${name}\n\n` : '') + message,
      p_reply_email: email, p_app_version: 'website', p_platform: 'other', p_locale: b.lang === 'ar' ? 'ar' : 'en',
      p_diagnostics: `Website · ${s(b.page, 120)} · ${s(b.src, 200)}` });
  } catch (e) {
    const busy = String(e).includes('Too many');
    return json(req, { ok: false, error: busy ? 'busy' : 'failed' }, busy ? 429 : 500);
  }
  const to = account ? 'privacy@onespace.live' : 'support@onespace.live';
  const text = [`From: ${name || '(no name)'} <${email}>`, `Topic: ${account ? 'account deletion request' : topic || '-'}`, `Page: ${s(b.page, 120)}`,
    `Language: ${b.lang === 'ar' ? 'Arabic' : 'English'}`, `Came from: ${s(b.src, 200) || '-'}`, '', message, '',
    '— Sent from the onespace.live form. Reply to this email to answer the visitor.'].join('\n');
  const sent = await sendInternal(to, email, `[Website] ${subject}`, text);
  if (!sent.ok) console.error('contact mail failed', sent.error);
  return json(req, { ok: true });
});
