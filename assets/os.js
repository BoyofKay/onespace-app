// OneSpace website behaviour (no dependencies).
(function () {
  'use strict';
  var SUPABASE = 'https://ugwrpeduzyzrujkizqfo.supabase.co';
  var KEY = 'sb_publishable_TtW_uUboFxD4adF5o7FSfA_cpjojMCe';
  var AR = window.ONESPACE_AR || {};
  var root = document.documentElement;
  function get(k) { try { return localStorage.getItem(k); } catch (_) { return null; } }
  function put(k, v) { try { localStorage.setItem(k, v); } catch (_) {} }
  function $(s, el) { return (el || document).querySelector(s); }
  function $$(s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); }

  // ---------- Where visitors came from (kept for this visit only) ----------
  var params = new URLSearchParams(location.search);
  function sget(k) { try { return sessionStorage.getItem(k); } catch (_) { return null; } }
  if (!sget('os-src')) {
    var src = ['utm_source', 'utm_medium', 'utm_campaign', 'ref'].map(function (k) { return params.get(k) ? k + '=' + params.get(k).slice(0, 40) : ''; }).filter(Boolean).join('&');
    var ref = ''; try { ref = document.referrer ? new URL(document.referrer).hostname : ''; } catch (_) {}
    if (ref === location.hostname) ref = '';
    try { sessionStorage.setItem('os-src', (src || 'direct') + (ref ? ' via ' + ref : '') + ' · landed ' + location.pathname); } catch (_) {}
  }
  // Optional privacy-friendly analytics: set GOATCOUNTER in build.py to enable.
  function track(name) { var gc = window.goatcounter; if (gc && gc.count) gc.count({ path: 'event/' + name, title: name, event: true }); }
  document.addEventListener('click', function (e) { var t = e.target.closest && e.target.closest('[data-track],[data-theme-pick],[data-view]'); if (!t) return;
    track(t.getAttribute('data-track') || (t.hasAttribute('data-theme-pick') ? 'theme_' + t.getAttribute('data-theme-pick') : 'view_' + t.getAttribute('data-view'))); });

  // ---------- Language ----------
  var english = new WeakMap();
  var lang = new URLSearchParams(location.search).get('lang') || get('os-lang') ||
    ((navigator.language || '').toLowerCase().indexOf('ar') === 0 ? 'ar' : 'en');
  if (lang !== 'ar') lang = 'en';
  function tr(key, en) { return lang === 'ar' && AR[key] ? AR[key] : en; }
  function apply() {
    root.lang = lang; root.dir = lang === 'ar' ? 'rtl' : 'ltr';
    $$('[data-i18n]').forEach(function (el) {
      if (!english.has(el)) english.set(el, el.innerHTML);
      var k = el.getAttribute('data-i18n');
      el.innerHTML = lang === 'ar' && AR[k] ? AR[k] : english.get(el);
    });
    $$('[data-i18n-attr]').forEach(function (el) {
      el.getAttribute('data-i18n-attr').split(';').forEach(function (pair) {
        var p = pair.split(':'); var attr = p[0], k = p[1];
        var store = 'data-en-' + attr;
        if (!el.hasAttribute(store)) el.setAttribute(store, el.getAttribute(attr) || '');
        el.setAttribute(attr, lang === 'ar' && AR[k] ? AR[k] : el.getAttribute(store));
      });
    });
    $$('.lang').forEach(function (b) { b.textContent = lang === 'ar' ? 'English' : 'العربية';
      b.setAttribute('aria-label', lang === 'ar' ? 'Switch to English' : 'التبديل إلى العربية'); });
    $$('[data-ar-src]').forEach(function (m) {
      var src = m.getAttribute(lang === 'ar' ? 'data-ar-src' : 'data-en-src');
      if (src && m.getAttribute('src') !== src) m.setAttribute('src', src);
      var poster = m.getAttribute(lang === 'ar' ? 'data-ar-poster' : 'data-en-poster');
      if (poster) m.setAttribute('poster', poster);
    });
    var t = document.querySelector('title');
    if (t && t.dataset.ar) { if (!t.dataset.en) t.dataset.en = t.textContent; t.textContent = lang === 'ar' ? t.dataset.ar : t.dataset.en; }
  }
  apply();
  $$('.lang').forEach(function (b) { b.addEventListener('click', function () { lang = lang === 'ar' ? 'en' : 'ar'; put('os-lang', lang); apply(); }); });

  // ---------- Menu ----------
  var burger = $('.burger'), menu = $('.menu');
  if (burger && menu) burger.addEventListener('click', function () {
    var open = menu.classList.toggle('open'); burger.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  $$('.drop > button').forEach(function (b) { b.addEventListener('click', function () {
    var d = b.parentElement; var open = d.classList.toggle('open'); b.setAttribute('aria-expanded', open ? 'true' : 'false'); }); });
  var y = $('#year'); if (y) y.textContent = new Date().getFullYear();

  // ---------- Theme switcher (phones) ----------
  $$('[data-theme-pick]').forEach(function (b) {
    b.addEventListener('click', function () {
      var theme = b.getAttribute('data-theme-pick');
      var scope = b.closest('[data-theme-scope]') || document;
      $$('.phone[data-themable]', scope).forEach(function (p) { p.setAttribute('data-theme', theme); });
      $$('[data-theme-pick]', scope).forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      $$('.playground', scope).forEach(function (p) { p.setAttribute('data-pg', theme); });
    });
  });

  // ---------- Segmented views (apart/together, tour) ----------
  $$('[data-views]').forEach(function (group) {
    var name = group.getAttribute('data-views');
    var buttons = $$('[data-view]', group);
    function show(v) {
      buttons.forEach(function (b) { b.setAttribute('aria-selected', b.getAttribute('data-view') === v ? 'true' : 'false'); });
      $$('[data-view-of="' + name + '"]').forEach(function (el) { el.hidden = el.getAttribute('data-view-name') !== v; });
    }
    buttons.forEach(function (b) { b.addEventListener('click', function () { show(b.getAttribute('data-view')); }); });
    var next = $('[data-next="' + name + '"]');
    if (next) next.addEventListener('click', function () {
      var i = buttons.findIndex(function (b) { return b.getAttribute('aria-selected') === 'true'; });
      buttons[(i + 1) % buttons.length].click();
      buttons[(i + 1) % buttons.length].focus();
    });
  });

  // ---------- Hero: rotating words and live notifications ----------
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  $$('.rotator').forEach(function (r) {
    var items = $$('span', r); var i = 0; if (reduce || items.length < 2) return;
    setInterval(function () { items[i].classList.remove('on'); i = (i + 1) % items.length; items[i].classList.add('on'); }, 2400);
  });
  var slot = $('[data-toast-slot]'), tpls = $$('template[data-toast]');
  if (slot && tpls.length) {
    var ti = 0; var showT = function () { slot.innerHTML = tpls[ti].innerHTML; apply(); slot.classList.remove('out'); };
    showT();
    if (!reduce) setInterval(function () { slot.classList.add('out'); setTimeout(function () { ti = (ti + 1) % tpls.length; showT(); }, 500); }, 3600);
  }

  // ---------- Reveal on scroll ----------
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }); }, { rootMargin: '0px 0px -8% 0px' });
    $$('.reveal').forEach(function (el) { io.observe(el); });
  } else { $$('.reveal').forEach(function (el) { el.classList.add('in'); }); }

  // ---------- FAQ search ----------
  var search = $('#faq-search');
  if (search) search.addEventListener('input', function () {
    var q = search.value.trim().toLowerCase(); var shown = 0;
    $$('details[data-faq]').forEach(function (d) {
      var hit = !q || d.textContent.toLowerCase().indexOf(q) >= 0;
      d.hidden = !hit; if (hit) shown++; if (q && hit) d.open = true;
    });
    $$('.faq-group').forEach(function (h) {
      var list = h.nextElementSibling; var any = list && $$('details[data-faq]', list).some(function (d) { return !d.hidden; });
      h.hidden = !any;
    });
    var empty = $('#faq-empty'); if (empty) empty.hidden = shown > 0;
  });

  // ---------- Copy buttons ----------
  $$('[data-copy]').forEach(function (b) {
    b.addEventListener('click', function () {
      var src = document.getElementById(b.getAttribute('data-copy'));
      var text = src ? src.innerText : '';
      var done = function () { var old = b.textContent; b.textContent = tr('kit.copied', 'Copied'); setTimeout(function () { b.textContent = old; }, 1500); };
      if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, function () {});
    });
  });

  // ---------- Forms (same support inbox as the app) ----------
  var msgs = { sending: 'Sending…', missing: 'Please fill in the fields marked *.', email: 'Please check the email address.',
    consent: 'Please tick the box so we may email you.', busy: 'Too many messages from this email. Please try again in an hour.',
    failed: 'Could not send. Please check your connection and try again.', sent: 'Thank you — we got it and will reply by email.' };
  $$('form[data-form]').forEach(function (form) {
    var topic = new URLSearchParams(location.search).get('topic');
    if (topic && form.elements.topic) form.elements.topic.value = topic;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var status = $('.status', form);
      function say(k, ok) { status.textContent = tr('form.' + k, msgs[k]); status.className = 'status ' + (ok === true ? 'ok' : ok === false ? 'err' : ''); }
      if (form.elements.website && form.elements.website.value) return;
      function v(n) { var el = form.elements[n]; if (!el) return ''; if (el.length && !el.tagName) { var c = Array.prototype.find.call(el, function (x) { return x.checked; }); return c ? c.value : ''; } return String(el.value || '').trim(); }
      var kindForm = form.getAttribute('data-form');
      var email = v('email');
      if (!email || (kindForm !== 'join' && !v('message'))) return say('missing', false);
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return say('email', false);
      if (form.elements.consent && !form.elements.consent.checked) return say('consent', false);
      var kind = 'contact', subject = 'Website message', message = v('message');
      if (kindForm === 'join') {
        subject = 'Founding 500 · ' + (v('platform') || 'unknown') + (v('living') ? ' · ' + v('living') : '');
        message = ['Founding 500 sign-up from the website.', 'Name: ' + (v('name') || '-'), 'Phone: ' + (v('platform') || '-'),
          'How we live: ' + (v('living') || '-'), 'Language: ' + (v('language') || lang), 'Heard about us: ' + (v('source') || '-'),
          'Came from: ' + (sget('os-src') || '-'), 'Signed up: ' + new Date().toISOString(), 'Note: ' + (v('message') || '-')].join('\n');
      } else if (kindForm === 'account') {
        kind = 'account'; subject = 'Delete my account';
      } else {
        var t = v('topic'); kind = t === 'issue' ? 'issue' : (t === 'signin' ? 'account' : 'contact');
        subject = ((t ? t + ' · ' : '') + (v('subject') || 'Website message')).slice(0, 160);
        if (v('name')) message = 'Name: ' + v('name') + '\n\n' + message;
      }
      var btn = $('button[type=submit]', form); btn.disabled = true; say('sending');
      fetch(SUPABASE + '/rest/v1/rpc/submit_public_support', {
        method: 'POST', headers: { 'Content-Type': 'application/json', apikey: KEY, Authorization: 'Bearer ' + KEY },
        body: JSON.stringify({ p_kind: kind, p_subject: subject.slice(0, 160), p_message: (message || subject).slice(0, 4000),
          p_reply_email: email, p_app_version: 'website', p_platform: 'other', p_locale: lang,
          p_diagnostics: 'Website · ' + location.pathname + ' · ' + (sget('os-src') || '-') })
      }).then(function (res) {
        if (res.ok) {
          track(kindForm + '_sent');
          form.reset();
          var done = form.getAttribute('data-done') && document.getElementById(form.getAttribute('data-done'));
          if (done) { form.hidden = true; done.classList.add('show'); done.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
          else say('sent', true);
        } else return res.text().then(function (b) { say(b.indexOf('Too many') >= 0 ? 'busy' : 'failed', false); });
      }).catch(function () { say('failed', false); }).then(function () { btn.disabled = false; });
    });
  });

  // ---------- Share with your partner ----------
  $$('[data-share]').forEach(function (a) {
    var url = location.origin + location.pathname.replace(/[^/]*$/, '') + 'join.html';
    var text = tr('share.text', 'I want us to try OneSpace — a private app just for the two of us: plans, little gestures and memories in one place.') + ' ' + url;
    var kind = a.getAttribute('data-share');
    if (kind === 'whatsapp') a.href = 'https://wa.me/?text=' + encodeURIComponent(text);
    if (kind === 'email') a.href = 'mailto:?subject=' + encodeURIComponent('OneSpace') + '&body=' + encodeURIComponent(text);
    if (kind === 'native') a.addEventListener('click', function (e) {
      e.preventDefault();
      if (navigator.share) navigator.share({ title: 'OneSpace', text: text }).catch(function () {});
      else if (navigator.clipboard) navigator.clipboard.writeText(text).then(function () { a.textContent = tr('kit.copied', 'Copied'); });
    });
  });
})();
