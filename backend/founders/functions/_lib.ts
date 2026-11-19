// Shared helpers for the OneSpace Founder Members waitlist (website only).
// Secrets live in Supabase › Edge Functions › Secrets: RESEND_API_KEY, FOUNDER_ADMIN_KEY (and the built-in SUPABASE_*).
export const SITE = 'https://onespace.live';
const ALLOWED = new Set([SITE, 'https://www.onespace.live', 'http://localhost:8765']);
const FROM = 'OneSpace Founders <founders@onespace.live>';
const REPLY_TO = 'founders@onespace.live';

export function cors(req: Request): Record<string, string> {
  const o = req.headers.get('origin') ?? '';
  return {
    'Access-Control-Allow-Origin': ALLOWED.has(o) ? o : SITE,
    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
    'Access-Control-Allow-Headers': 'content-type, x-admin-key',
    'Vary': 'Origin',
  };
}

export function json(req: Request, body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { ...cors(req), 'Content-Type': 'application/json', 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer' } });
}

export async function rpc(fn: string, args: Record<string, unknown>): Promise<any> {
  const url = Deno.env.get('SUPABASE_URL')!;
  const key = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
  const r = await fetch(`${url}/rest/v1/rpc/${fn}`, {
    method: 'POST',
    headers: { apikey: key, Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(args),
  });
  if (!r.ok) throw new Error(`${fn}: ${r.status} ${(await r.text()).slice(0, 300)}`);
  const t = await r.text();
  return t ? JSON.parse(t) : null;
}

// ------------------------------------------------------------------ spam protection
// Robots fill a hidden `website` field: dropped silently (people never see that field).
// All public website form submissions require a fresh Cloudflare Turnstile token
// validated server-side. Client-supplied elapsed time or "Turnstile unavailable"
// flags must NEVER bypass verification. Existing database rate limits still apply.
// When Turnstile is unavailable, fail closed and ask the visitor to retry.
export type Guard = 'ok' | 'drop' | 'verify' | 'blocked';

async function spamCount(form: string, result: string) {
  try { await rpc('founder_spam_count', { p_form: form, p_result: result }); } catch (e) { console.error('spam count', e); }
}

async function turnstileOk(token: string, req: Request): Promise<boolean | null> {
  const secret = Deno.env.get('TURNSTILE_SECRET_KEY');
  if (!secret) return null;
  const body = new FormData();
  body.set('secret', secret);
  body.set('response', token.slice(0, 2048));
  const ip = (req.headers.get('x-forwarded-for') ?? '').split(',')[0].trim();
  if (ip) body.set('remoteip', ip);
  try {
    const r = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', { method: 'POST', body, signal: AbortSignal.timeout(6000) });
    if (!r.ok) return null;
    const j = await r.json();
    return j.success === true && (j.hostname === 'onespace.live' || j.hostname === 'www.onespace.live');
  } catch { return null; }
}

export async function guard(req: Request, b: any, form: 'join' | 'contact'): Promise<Guard> {
  if (!b || typeof b !== 'object') return 'blocked';
  if (b.website) { await spamCount(form, 'honeypot'); return 'drop'; }
  if (typeof b.turnstile !== 'string' || !b.turnstile) {
    await spamCount(form, 'challenge_required');
    return 'verify';
  }
  const ok = await turnstileOk(b.turnstile, req);
  await spamCount(form, ok === true ? 'passed' : 'blocked');
  return ok === true ? 'ok' : 'blocked';
}

// Answer for a guard result that is not 'ok' (the form shows the check, or a "couldn't verify" message).
export function guardReply(req: Request, g: Guard): Response {
  if (g === 'drop') return json(req, { ok: true });
  if (g === 'verify') return json(req, { ok: false, error: 'verify' }, 428);
  return json(req, { ok: false, error: 'verify_failed' }, 403);
}

export async function sha256(s: string): Promise<string> {
  const d = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));
  return Array.from(new Uint8Array(d)).map((b) => b.toString(16).padStart(2, '0')).join('');
}

// The network address is only kept as a salted hash, for rate limiting.
export async function ipHash(req: Request): Promise<string> {
  const ip = (req.headers.get('x-forwarded-for') ?? '').split(',')[0].trim() || req.headers.get('cf-connecting-ip') || '';
  if (!ip) return '';
  const pepper = (Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? '').slice(-16);
  return (await sha256(`onespace-founders|${pepper}|${ip}`)).slice(0, 32);
}

const esc = (s: string) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]!));
const page = (lang: string, path: string) => `${SITE}${lang === 'ar' ? '/ar/' : '/'}${path.replace(/\.html$/, '/')}`;

// ------------------------------------------------------------------ templates
type Mail = { subject: string; html: string; text: string };

function shell(lang: string, preheader: string, title: string, body: string, button?: { label: string; href: string }): string {
  const rtl = lang === 'ar';
  const font = rtl ? "'IBM Plex Sans Arabic', Tahoma, Arial, sans-serif" : "'Plus Jakarta Sans', 'Segoe UI', Helvetica, Arial, sans-serif";
  const foot = rtl
    ? `وصلتك هذه الرسالة لأنك سجّلت في <a href="${SITE}/ar/" style="color:#1F6E78">onespace.live</a>. لأي سؤال، ردّ على هذه الرسالة.<br><a href="${SITE}/ar/privacy/" style="color:#8A8FA3">الخصوصية</a> · <a href="{{UNSUB_AR}}" style="color:#8A8FA3">إلغاء الاشتراك</a>`
    : `You received this because you signed up at <a href="${SITE}/" style="color:#1F6E78">onespace.live</a>. Questions? Just reply to this email.<br><a href="${SITE}/privacy/" style="color:#8A8FA3">Privacy</a> · <a href="{{UNSUB_EN}}" style="color:#8A8FA3">Unsubscribe</a>`;
  const btn = button ? `<tr><td style="padding:8px 0 4px"><a href="${button.href}" style="display:inline-block;background:#E8735A;color:#ffffff;text-decoration:none;font-weight:700;font-size:16px;padding:14px 26px;border-radius:999px">${esc(button.label)}</a></td></tr>` : '';
  return `<!doctype html><html lang="${lang}" dir="${rtl ? 'rtl' : 'ltr'}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>${esc(title)}</title></head>
<body style="margin:0;padding:0;background:#F5F6FA;font-family:${font};color:#1D2030">
<span style="display:none;max-height:0;overflow:hidden;opacity:0">${esc(preheader)}</span>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#F5F6FA"><tr><td align="center" style="padding:28px 14px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#ffffff;border-radius:22px;overflow:hidden;border:1px solid #E7E8EF">
<tr><td style="background:linear-gradient(135deg,#FFF1EC,#EAF6F7);padding:22px 28px;text-align:${rtl ? 'right' : 'left'}">
<img src="${SITE}/assets/icon-512.png" width="40" height="40" alt="" style="vertical-align:middle;border-radius:10px"> <span style="font-size:20px;font-weight:700;vertical-align:middle;color:#14213D">&nbsp;OneSpace</span>
<div style="font-size:12px;letter-spacing:.06em;color:#1F6E78;font-weight:700;margin-top:6px">${rtl ? 'نحن الاثنان. مساحة واحدة.' : 'TWO OF US. ONE SPACE.'}</div></td></tr>
<tr><td style="padding:26px 28px 8px;text-align:${rtl ? 'right' : 'left'}">
<h1 style="font-size:24px;line-height:1.3;margin:0 0 14px;color:#14213D">${title}</h1>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="font-size:16px;line-height:1.65;color:#3B4055">${body}${btn}</table>
</td></tr>
<tr><td style="padding:18px 28px 26px;font-size:12.5px;line-height:1.6;color:#8A8FA3;text-align:${rtl ? 'right' : 'left'};border-top:1px solid #F0F1F5">${foot}</td></tr>
</table></td></tr></table></body></html>`;
}
const p = (s: string) => `<tr><td style="padding:0 0 12px">${s}</td></tr>`;
const big = (n: string) => `<tr><td style="padding:4px 0 16px"><div style="display:inline-block;background:#14213D;color:#fff;border-radius:16px;padding:14px 22px;font-size:30px;font-weight:700">${n}</div></td></tr>`;

export function mailConfirm(lang: string, name: string, token: string, partnerInvite: boolean): Mail {
  const href = `${page(lang, 'confirm.html')}#t=${token}`;
  if (lang === 'ar') {
    const hi = name ? `أهلًا ${esc(name)}،` : 'أهلًا،';
    return {
      subject: 'أكّد بريدك لتحصل على مكانك كعضو مؤسس في OneSpace',
      text: `${hi}\nأكّد بريدك لتحصل على مكانك كعضو مؤسس:\n${href}\nينتهي الرابط خلال 7 أيام. إن لم تسجّل، تجاهل هذه الرسالة.`,
      html: shell('ar', 'خطوة أخيرة لتحصل على رقمك كمؤسس.', 'خطوة أخيرة لتأكيد مكانك', p(hi) +
        p(partnerInvite ? 'شكرًا لانضمامك إلى عضوية شريكك كمؤسس. أكّد بريدك لنربط حسابيكما.' : 'شكرًا لتسجيلك في OneSpace. أكّد بريدك وسنمنحكما رقمكما كزوجين مؤسسين — أول 250 زوجًا فقط.') +
        p('<span style="color:#8A8FA3;font-size:14px">ينتهي الرابط خلال 7 أيام. إن لم تسجّل أنت، تجاهل هذه الرسالة ولن نراسلك مجددًا.</span>'),
        { label: 'أكّد بريدي', href }),
    };
  }
  const hi = name ? `Hi ${esc(name)},` : 'Hi there,';
  return {
    subject: 'Confirm your email to claim your OneSpace Founder place',
    text: `${hi}\nConfirm your email to claim your Founder place:\n${href}\nThe link expires in 7 days. If you didn't sign up, ignore this email.`,
    html: shell('en', 'One last step to get your Founder number.', 'One last step to claim your place', p(hi) +
      p(partnerInvite ? 'Thanks for joining your partner’s Founder membership. Confirm your email and we’ll link the two of you.'
        : 'Thanks for signing up for OneSpace. Confirm your email and we’ll give the two of you your Founder couple number — only the first 250 couples get one.') +
      p('<span style="color:#8A8FA3;font-size:14px">The link expires in 7 days. If you didn’t sign up, ignore this email and we won’t write again.</span>'),
      { label: 'Confirm my email', href }),
  };
}

export function mailWelcome(lang: string, r: any, firstName = ''): Mail {
  const num = r.founder_number ? `#${r.founder_number}` : '';
  const invite = `${page(lang, 'join.html')}?invite=${r.invite_code}`;
  const waitlist = r.couple_status !== 'founder';
  const partner = r.role === 'partner';
  if (lang === 'ar') {
    const hi = r.name ? `أهلًا ${esc(r.name)}،` : 'أهلًا،';
    const title = waitlist ? 'أنتما على قائمة الانتظار' : partner ? `انضممت إلى الزوجين المؤسسين ${num}` : `أنتما الزوجان المؤسسان ${num}`;
    const body = p(hi) + (waitlist
      ? p('شكرًا لتأكيد بريدك. اكتملت أماكن المؤسسين الـ250، وأنتما الآن على قائمة الانتظار — سنرسل لكما الدعوة فور فتح أماكن جديدة.')
      : big(num) + p(partner ? `انضممت إلى ${esc(firstName) || 'شريكك'} — أنتما الآن الزوجان المؤسسان ${num}. سيصلكما التطبيق معًا.`
        : `مرحبًا بكما في OneSpace! رقمكما كزوجين مؤسسين هو ${num}. سنعلن مزايا المؤسسين قبل تقديم أي أسعار، وOneSpace مجاني خلال الوصول المبكر.`)) +
      (partner || r.couple_full ? '' : p('OneSpace لشخصين. أرسل هذا الرابط لشريكك لينضم إلى رقمكما نفسه:') + p(`<a href="${invite}" style="color:#1F6E78;word-break:break-all">${invite}</a>`));
    return { subject: waitlist ? 'أنتما على قائمة انتظار OneSpace' : `أهلًا بكما — أنتما الزوجان المؤسسان ${num} في OneSpace`, html: shell('ar', title, title, body,
      partner || r.couple_full ? { label: 'جرّب العرض', href: page('ar', 'how-it-works.html') } : { label: 'ادعُ شريكك', href: invite }),
      text: `${hi}\n${title}\n${partner || r.couple_full ? '' : 'رابط دعوة شريكك: ' + invite}` };
  }
  const hi = r.name ? `Hi ${esc(r.name)},` : 'Hi there,';
  const title = waitlist ? 'You’re on the waitlist' : partner ? `You’ve joined Founder Couple ${num}` : `You’re Founder Couple ${num}`;
  const body = p(hi) + (waitlist
    ? p('Thanks for confirming. All 250 Founder places are taken, so the two of you are on the waitlist — we’ll invite you as soon as more places open.')
    : big(num) + p(partner ? `You’ve joined ${esc(firstName) || 'your partner'} — together you are Founder Couple ${num}. You’ll get the app together.`
      : `Welcome to OneSpace! Your Founder couple number is ${num}. Founder benefits will be announced before any pricing, and OneSpace is free during early access.`)) +
    (partner || r.couple_full ? '' : p('OneSpace is for two. Send your partner this link so they join under the same number:') + p(`<a href="${invite}" style="color:#1F6E78;word-break:break-all">${invite}</a>`));
  return { subject: waitlist ? 'You’re on the OneSpace waitlist' : `Welcome — you’re OneSpace Founder Couple ${num}`, html: shell('en', title, title, body,
    partner || r.couple_full ? { label: 'Try the demo', href: page('en', 'how-it-works.html') } : { label: 'Invite your partner', href: invite }),
    text: `${hi}\n${title}\n${partner || r.couple_full ? '' : 'Invite your partner: ' + invite}` };
}

export function mailPartnerJoined(lang: string, firstName: string, partnerName: string, num: number | null): Mail {
  const n = num ? `#${num}` : '';
  if (lang === 'ar') {
    const t = `${esc(partnerName) || 'شريكك'} انضم إليك`;
    return { subject: `${partnerName || 'شريكك'} انضم إلى OneSpace — اكتمل زوجكما المؤسس ${n}`, text: `${t}. اكتمل زوجكما المؤسس ${n}.`,
      html: shell('ar', t, t, p(firstName ? `أهلًا ${esc(firstName)}،` : 'أهلًا،') + p(`أكّد شريكك بريده. أنتما الآن الزوجان المؤسسان ${n} — اكتمل زوجكما.`),
        { label: 'جرّب العرض معًا', href: page('ar', 'how-it-works.html') }) };
  }
  const t = `${esc(partnerName) || 'Your partner'} joined you`;
  return { subject: `${partnerName || 'Your partner'} joined OneSpace — Founder Couple ${n} is complete`, text: `${t}. Founder Couple ${n} is complete.`,
    html: shell('en', t, t, p(firstName ? `Hi ${esc(firstName)},` : 'Hi there,') + p(`Your partner confirmed their email. You are now Founder Couple ${n} — both of you.`),
      { label: 'Try the demo together', href: page('en', 'how-it-works.html') }) };
}

export function mailAlready(lang: string, r: any): Mail {
  const num = r.founder_number ? `#${r.founder_number}` : '';
  const invite = `${page(lang, 'join.html')}?invite=${r.invite_code}`;
  if (lang === 'ar') {
    const t = r.couple_status === 'founder' ? `أنتما بالفعل الزوجان المؤسسان ${num}` : 'أنتما بالفعل على قائمة الانتظار';
    return { subject: t, text: `${t}.`, html: shell('ar', t, t, p('حاول أحدهم التسجيل بهذا البريد مجددًا. لا داعي لفعل شيء — مكانكما محفوظ.') +
      (r.role === 'first' ? p(`رابط دعوة شريكك: <a href="${invite}" style="color:#1F6E78;word-break:break-all">${invite}</a>`) : '')) };
  }
  const t = r.couple_status === 'founder' ? `You’re already Founder Couple ${num}` : 'You’re already on the waitlist';
  return { subject: t, text: `${t}.`, html: shell('en', t, t, p('Someone tried to sign up with this email again. Nothing to do — your place is safe.') +
    (r.role === 'first' ? p(`Your partner’s invite link: <a href="${invite}" style="color:#1F6E78;word-break:break-all">${invite}</a>`) : '')) };
}

// ------------------------------------------------------------------ sending
const FN_URL = `${Deno.env.get('SUPABASE_URL') ?? ''}/functions/v1`;
export const unsubPage = (lang: string, token?: string) => token ? `${SITE}${lang === 'ar' ? '/ar/' : '/'}unsubscribe/#u=${token}` : `mailto:founders@onespace.live?subject=unsubscribe`;

export async function send(memberId: string, kind: string, to: string, m: Mail, unsub?: string): Promise<boolean> {
  m = { ...m, html: m.html.replace('{{UNSUB_EN}}', unsubPage('en', unsub)).replace('{{UNSUB_AR}}', unsubPage('ar', unsub)) };
  const listUnsub = (unsub ? `<${FN_URL}/founder-unsubscribe?u=${unsub}>, ` : '') + '<mailto:founders@onespace.live?subject=unsubscribe>';
  const key = Deno.env.get('RESEND_API_KEY');
  if (!key) {
    await rpc('founder_log_email', { p_member: memberId, p_kind: kind, p_status: 'skipped', p_provider_id: null, p_error: 'RESEND_API_KEY is not set' });
    return false;
  }
  try {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${key}`, 'Content-Type': 'application/json',
        // The same message is never sent twice, even if a request is retried.
        'Idempotency-Key': `${memberId}-${kind}-${(await sha256(m.subject + m.text)).slice(0, 16)}`,
      },
      body: JSON.stringify({ from: FROM, to: [to], reply_to: REPLY_TO, subject: m.subject, html: m.html, text: m.text,
        headers: unsub ? { 'List-Unsubscribe': listUnsub, 'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click' } : { 'List-Unsubscribe': listUnsub },
        tags: [{ name: 'type', value: kind }] }),
    });
    const body = await r.json().catch(() => ({}));
    if (r.ok) {
      await rpc('founder_log_email', { p_member: memberId, p_kind: kind, p_status: 'sent', p_provider_id: body.id ?? null, p_error: null });
      return true;
    }
    await rpc('founder_log_email', { p_member: memberId, p_kind: kind, p_status: 'failed', p_provider_id: null,
      p_error: `${r.status} ${body.name ?? ''} ${body.message ?? ''}`.trim() });
  } catch (e) {
    await rpc('founder_log_email', { p_member: memberId, p_kind: kind, p_status: 'failed', p_provider_id: null, p_error: String(e).slice(0, 400) });
  }
  return false;
}

// Website contact / account requests → our own inboxes (support@ or privacy@), reply goes straight to the visitor.
export async function sendInternal(to: string, replyTo: string, subject: string, text: string): Promise<{ ok: boolean; id?: string; error?: string }> {
  const key = Deno.env.get('RESEND_API_KEY');
  if (!key) return { ok: false, error: 'RESEND_API_KEY is not set' };
  const r = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json', 'Idempotency-Key': (await sha256(to + subject + text)).slice(0, 32) },
    body: JSON.stringify({ from: 'OneSpace Website <website@onespace.live>', to: [to], reply_to: replyTo, subject, text, tags: [{ name: 'type', value: 'site_contact' }] }),
  });
  const b = await r.json().catch(() => ({}));
  return r.ok ? { ok: true, id: b.id } : { ok: false, error: `${r.status} ${b.message ?? ''}` };
}
