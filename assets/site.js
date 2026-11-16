// OneSpace website: English / Arabic and the support forms.
// The forms use the same support inbox as the app (Supabase RPC
// submit_public_support, readable only by the OneSpace team; rate-limited).
(function () {
  const SUPABASE = 'https://ugwrpeduzyzrujkizqfo.supabase.co';
  const KEY = 'sb_publishable_TtW_uUboFxD4adF5o7FSfA_cpjojMCe';
  const AR = window.ONESPACE_AR || {};

  function safeGet(k) { try { return localStorage.getItem(k); } catch (_) { return null; } }
  function safeSet(k, v) { try { localStorage.setItem(k, v); } catch (_) {} }

  const english = new Map();
  function apply(lang) {
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      const key = el.getAttribute('data-i18n');
      if (!english.has(el)) english.set(el, el.innerHTML);
      el.innerHTML = lang === 'ar' && AR[key] ? AR[key] : english.get(el);
    });
    document.querySelectorAll('[data-i18n-ph]').forEach(function (el) {
      const key = el.getAttribute('data-i18n-ph');
      if (!el.dataset.en) el.dataset.en = el.getAttribute('placeholder') || '';
      el.setAttribute('placeholder', lang === 'ar' && AR[key] ? AR[key] : el.dataset.en);
    });
    document.querySelectorAll('.lang').forEach(function (b) { b.textContent = lang === 'ar' ? 'English' : 'العربية'; });
    const t = document.querySelector('title');
    if (t && t.dataset.ar) { if (!t.dataset.en) t.dataset.en = t.textContent; t.textContent = lang === 'ar' ? t.dataset.ar : t.dataset.en; }
  }
  const params = new URLSearchParams(location.search);
  let lang = params.get('lang') || safeGet('onespace-lang') ||
    ((navigator.language || '').toLowerCase().startsWith('ar') ? 'ar' : 'en');
  if (lang !== 'ar') lang = 'en';
  apply(lang);
  document.querySelectorAll('.lang').forEach(function (b) {
    b.addEventListener('click', function () {
      lang = lang === 'ar' ? 'en' : 'ar';
      safeSet('onespace-lang', lang);
      apply(lang);
    });
  });
  const y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  // Support / account-deletion forms.
  document.querySelectorAll('form[data-support]').forEach(function (form) {
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      const status = form.querySelector('.status');
      const say = function (key, ok) {
        const en = { sending: 'Sending…', sent: 'Thank you — we got it and will reply by email.',
          missing: 'Please fill in your email and message.', email: 'Please check the email address.',
          busy: 'Too many messages from this email. Please try again in an hour.',
          failed: 'Could not send. Please check your connection and try again.' }[key];
        status.textContent = lang === 'ar' && AR['form.' + key] ? AR['form.' + key] : en;
        status.className = 'status ' + (ok === true ? 'ok' : ok === false ? 'err' : '');
      };
      if (form.querySelector('.hp input') && form.querySelector('.hp input').value) return; // bot
      const v = function (n) { const el = form.elements[n]; return el ? String(el.value || '').trim() : ''; };
      const email = v('email'), message = v('message');
      if (!email || !message) return say('missing', false);
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return say('email', false);
      const kind = form.dataset.support === 'account' ? 'account' : (v('topic') === 'issue' ? 'issue' : 'contact');
      const subject = (form.dataset.support === 'account' ? 'Delete my account' : (v('subject') || v('topic') || 'Website message')).slice(0, 160);
      const button = form.querySelector('button[type=submit]');
      button.disabled = true; say('sending');
      try {
        const res = await fetch(SUPABASE + '/rest/v1/rpc/submit_public_support', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', apikey: KEY, Authorization: 'Bearer ' + KEY },
          body: JSON.stringify({ p_kind: kind, p_subject: subject, p_message: message.slice(0, 4000),
            p_reply_email: email, p_app_version: 'website', p_platform: 'other', p_locale: lang,
            p_diagnostics: 'Sent from the OneSpace website: ' + location.pathname }),
        });
        if (res.ok) { form.reset(); say('sent', true); }
        else {
          const body = await res.text();
          say(body.indexOf('Too many') >= 0 ? 'busy' : 'failed', false);
        }
      } catch (_) { say('failed', false); }
      button.disabled = false;
    });
  });
})();
