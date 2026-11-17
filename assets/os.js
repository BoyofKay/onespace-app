// OneSpace website behaviour (no dependencies).
(function () {
  'use strict';
  var SUPABASE = 'https://letcgxbnblohhfyeuigz.supabase.co'; // OneSpace Production (D77)
  var KEY = 'sb_publishable_eAeTViXIscberKyVhCQiWg_h3rivqwo';
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
    try { var u = {}; ['utm_source', 'utm_medium', 'utm_campaign'].forEach(function (k) { if (params.get(k)) u[k] = params.get(k).slice(0, 60); });
      sessionStorage.setItem('os-utm', JSON.stringify(u)); sessionStorage.setItem('os-landing', location.pathname); sessionStorage.setItem('os-ref', ref); } catch (_) {}
  }
  // ---------- Analytics (GoatCounter, cookieless) ----------
  // Events are fixed names only — never form values, emails or tokens. Queued until count.js has loaded.
  var gcQueue = [];
  function flush() {
    var gc = window.goatcounter;
    if (!(gc && gc.count)) return false;
    while (gcQueue.length) { var n = gcQueue.shift(); gc.count({ path: n, title: n, event: true }); }
    return true;
  }
  function track(name) {
    if (/founders-admin/.test(location.pathname)) return; // the private admin page is never counted
    name = String(name).replace(/[^\w\/@.\-]/g, '-').slice(0, 120);
    gcQueue.push(name);
    if (!flush()) { var tries = 0, t = setInterval(function () { if (flush() || ++tries > 40) clearInterval(t); }, 250); }
  }
  window.osTrack = track;
  // Engagement, measured without cookies or IDs: one time bucket per page visit (only while the tab is visible),
  // and one event when a visitor reaches the end of a page.
  (function () {
    var active = 0, since = document.visibilityState === 'visible' ? Date.now() : 0, sent = false, read = false;
    var add = function () { if (since) { active += Date.now() - since; since = 0; } };
    var bucket = function (ms) { var s = ms / 1000; return s < 10 ? '0-10s' : s < 30 ? '10-30s' : s < 60 ? '30-60s' : s < 180 ? '1-3m' : s < 600 ? '3-10m' : '10m-plus'; };
    var send = function () { add(); if (sent || active < 500) return; sent = true; track('time/' + bucket(active)); };
    document.addEventListener('visibilitychange', function () { if (document.visibilityState === 'hidden') send(); else if (!sent) since = Date.now(); });
    window.addEventListener('pagehide', send);
    window.addEventListener('scroll', function () {
      if (read) return; var h = document.documentElement, max = h.scrollHeight - h.clientHeight;
      if (max > 400 && (h.scrollTop || window.scrollY) / max > 0.9) { read = true; track('read/end@' + location.pathname.replace(/^\/ar\//, '/')); }
    }, { passive: true });
  })();
  var here = '@' + location.pathname.replace(/^\/ar\//, '/');
  // Conversion clicks, named by where they happened: cta/join@/watchlists.html, outbound/play.google.com …
  document.addEventListener('click', function (e) {
    var t = e.target.closest && e.target.closest('[data-track],[data-theme-pick],[data-view],[data-next],a[href]');
    if (!t) return;
    if (t.hasAttribute('data-track')) return track('cta/' + t.getAttribute('data-track') + here);
    if (t.hasAttribute('data-theme-pick')) return track('theme/' + t.getAttribute('data-theme-pick'));
    if (t.hasAttribute('data-view')) {
      if (!e.isTrusted) return;  // 'Next step' clicks the tab itself; counted once as -next
      var g = t.closest('[data-views]');
      return track('demo/' + (g ? g.getAttribute('data-views') : 'view') + '-' + t.getAttribute('data-view'));
    }
    if (t.hasAttribute('data-next')) return track('demo/' + t.getAttribute('data-next') + '-next');
    var h = t.getAttribute('href') || '';
    if (/join\.html|#founding/.test(h)) track('cta/join' + here);
    else if (/how-it-works\.html|#tour/.test(h)) track('cta/demo' + here);
    else if (/^mailto:/.test(h)) track('email/' + h.slice(7).split('@')[0].replace(/[^a-z]/gi, '') + here);
    else if (/^https?:/.test(h) && t.host !== location.host) track('outbound/' + t.host);
  }, true);

  // ---------- Language ----------
  var english = new WeakMap();
  // Each language has its own address: /page.html (English) and /ar/page.html (Arabic).
  var lang = root.getAttribute('lang') === 'ar' ? 'ar' : 'en';
  function twin(to) {
    var p = location.pathname, isAr = p.indexOf('/ar/') === 0 || p === '/ar';
    var rest = isAr ? p.replace(/^\/ar\/?/, '/') : p;
    return (to === 'ar' ? '/ar' + rest : rest) + location.search.replace(/[?&]lang=(ar|en)/, '').replace(/^&/, '?') + location.hash;
  }
  var want = new URLSearchParams(location.search).get('lang') || get('os-lang') ||
    (!get('os-lang-seen') && (navigator.language || '').toLowerCase().indexOf('ar') === 0 ? 'ar' : null);
  put('os-lang-seen', '1');
  if ((want === 'ar' || want === 'en') && want !== lang && location.protocol !== 'file:') { location.replace(twin(want)); return; }
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
  if (lang === 'ar') apply();  // already rendered in Arabic on the server; this only fills script-made text
  $$('.lang').forEach(function (b) { b.addEventListener('click', function () { var to = lang === 'ar' ? 'en' : 'ar'; put('os-lang', to); track('lang/' + to); location.href = twin(to); }); });

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
      var pal = b.getAttribute('data-palette');
      if (pal) $$('img[data-theme-img]', scope).forEach(function (img) {
        ['en', 'ar'].forEach(function (l) {
          var cur = img.getAttribute('data-' + l + '-src') || '';
          img.setAttribute('data-' + l + '-src', cur.replace(/_[A-Za-z]+\.webp$/, '_' + pal + '.webp'));
        });
        img.setAttribute('src', img.getAttribute(lang === 'ar' ? 'data-ar-src' : 'data-en-src'));
      });
    });
  });

  // ---------- Segmented views (apart/together, tour) ----------
  $$('[data-views]').forEach(function (group) {
    var name = group.getAttribute('data-views');
    var buttons = $$('[data-view]', group);
    function show(v) {
      buttons.forEach(function (b) { b.setAttribute('aria-selected', b.getAttribute('data-view') === v ? 'true' : 'false'); });
      if (buttons.length > 2 && buttons[buttons.length - 1].getAttribute('data-view') === v && !group.dataset.finished) { group.dataset.finished = '1'; track('demo/' + name + '-finished'); }
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
  var FN = SUPABASE + '/functions/v1/';
  var loadedAt = Date.now();
  // A partner's invite link (?invite=…) is kept for the visit and shown on the form.
  var invite = (params.get('invite') || sget('os-invite') || '').replace(/[^a-f0-9]/g, '').slice(0, 20);
  if (invite) { try { sessionStorage.setItem('os-invite', invite); } catch (_) {}
    if (params.get('invite')) track('founders/invite-landing');
    $$('form[data-form="join"]').forEach(function (f) { if (f.elements.invite) f.elements.invite.value = invite; var n = $('.invite-note', f); if (n) n.hidden = false; }); }
  $$('form[data-form="join"] select[name="language"]').forEach(function (sel) { sel.value = lang; });
  var msgs = { sending: 'Sending…', missing: 'Please fill in the fields marked *.', email: 'Please check the email address.',
    consent: 'Please tick the box so we may email you.', busy: 'Too many tries. Please wait a few minutes and try again.',
    failed: 'Could not send. Please check your connection and try again.', sent: 'Thank you — we got it and will reply by email.',
    verify: 'That was quick! One short check that you’re human, then we’ll send it.', verify_failed: 'We couldn’t complete the check. Please reload the page and try again.' };
  var msgsAr = { verify: 'كان ذلك سريعًا! تحقّق قصير من أنك إنسان، ثم نرسل النموذج.', verify_failed: 'تعذّر إكمال التحقق. أعد تحميل الصفحة وحاول مرة أخرى.' };

  // ---------- Spam check (Cloudflare Turnstile) ----------
  // Shown only when the server asks for it (the form was sent within 2.5 s of the page opening — robots
  // do that, but so can a person using autofill). If the check cannot load, the form is sent anyway:
  // the email confirmation step is what really stops fake sign-ups.
  var TS_KEY = '0x4AAAAAAGFSBBh0y5giCOsV', tsWait = [];
  function loadTurnstile(cb) {
    if (window.turnstile) return cb(window.turnstile);
    tsWait.push(cb);
    if (tsWait.length > 1) return;
    var settle = function (t) { var w = tsWait; tsWait = []; w.forEach(function (f) { f(t); }); };
    window.osTurnstileReady = function () { settle(window.turnstile); };
    var sc = document.createElement('script');
    sc.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&onload=osTurnstileReady';
    sc.async = true; sc.onerror = function () { settle(null); };
    document.head.appendChild(sc);
    setTimeout(function () { if (!window.turnstile && tsWait.length) settle(null); }, 10000);
  }
  function guardedPost(form, btn, say, fn, payload, onOk, onErr, name) {
    var send = function (extra) {
      var body = {}; Object.keys(payload).forEach(function (k) { body[k] = payload[k]; });
      Object.keys(extra || {}).forEach(function (k) { body[k] = extra[k]; });
      fetch(FN + fn, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
        .then(function (res) { return res.json().catch(function () { return {}; }).then(function (b) { return { res: res, b: b }; }); })
        .then(function (x) {
          if (x.res.ok && x.b.ok) return onOk();
          if (x.b.error === 'verify' && !(extra && (extra.turnstile || extra.turnstile_unavailable))) return check();
          onErr(x.b.error);
        }).catch(function () { onErr('failed'); });
    };
    var check = function () {
      say('verify'); track(name + '/check-shown');
      var box = $('.ts-box', form);
      if (!box) { box = document.createElement('div'); box.className = 'ts-box'; btn.parentNode.insertBefore(box, btn); }
      box.hidden = false; box.innerHTML = '';
      loadTurnstile(function (ts) {
        if (!ts) { box.hidden = true; say('sending'); return send({ turnstile_unavailable: true }); }
        ts.render(box, { sitekey: TS_KEY, language: lang === 'ar' ? 'ar' : 'en', theme: 'auto',
          callback: function (token) { track(name + '/check-passed'); box.hidden = true; say('sending'); send({ turnstile: token }); },
          'error-callback': function () { box.hidden = true; say('sending'); send({ turnstile_unavailable: true }); return true; } });
      });
    };
    send();
  }
  $$('form[data-form]').forEach(function (form) {
    var fname = form.getAttribute('data-form') === 'join' ? 'founders' : form.getAttribute('data-form');
    form.addEventListener('focusin', function () { if (!form.dataset.started) { form.dataset.started = '1'; track(fname + '/form-start' + here); } });
    var topic = new URLSearchParams(location.search).get('topic');
    if (topic && form.elements.topic) form.elements.topic.value = topic;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var status = $('.status', form);
      function say(k, ok) { status.textContent = lang === 'ar' && msgsAr[k] ? msgsAr[k] : tr('form.' + k, msgs[k]); status.className = 'status ' + (ok === true ? 'ok' : ok === false ? 'err' : '');
        if (ok === false) track(fname + '/error-' + k); }
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
        var t = v('topic'); kind = t === 'issue' ? 'issue' : t === 'signin' ? 'account' : t === 'complaint' ? 'complaint' : 'contact';
        subject = ((t ? t + ' · ' : '') + (v('subject') || 'Website message')).slice(0, 160);
        if (v('name')) message = 'Name: ' + v('name') + '\n\n' + message;
      }
      var btn = $('button[type=submit]', form); btn.disabled = true; say('sending');
      var finish = function () { btn.disabled = false; };
      var done = function () {
        form.reset();
        var box = form.getAttribute('data-done') && document.getElementById(form.getAttribute('data-done'));
        if (box) { form.hidden = true; box.classList.add('show'); box.focus(); } else say('sent', true);
      };
      if (kindForm === 'join') {
        var sj = function (k) { try { return sessionStorage.getItem(k) || ''; } catch (_) { return ''; } };
        var utm = {}; try { utm = JSON.parse(sj('os-utm') || '{}'); } catch (_) {}
        var language = v('language'); if (language !== 'ar' && language !== 'en') language = lang;
        guardedPost(form, btn, say, 'founder-join', { email: email, name: v('name'), platform: v('platform'), living: v('living'), language: language,
            source: v('source'), note: v('message'), consent: true, website: v('website'), elapsed: Date.now() - loadedAt,
            invite: v('invite') || invite, landing: sj('os-landing'), referrer: sj('os-ref'), utm: utm },
          function () {
            track('founders/sent');
            var pl = v('platform'); if (pl) track('founders/platform-' + pl);
            if (v('invite') || invite) track('founders/sent-partner');
            done(); finish();
          },
          function (err) { say(err === 'rate_limited' ? 'busy' : err === 'invalid_email' ? 'email' : err === 'consent_required' ? 'consent' : err === 'verify_failed' ? 'verify_failed' : 'failed', false); finish(); }, fname);
        return;
      }
      guardedPost(form, btn, say, 'site-contact', { form: kindForm, topic: v('topic'), name: v('name'), email: email, subject: v('subject'), message: message,
          website: v('website'), elapsed: Date.now() - loadedAt, page: location.pathname, lang: lang, src: sget('os-src') || '' },
        function () { track(kindForm + '/sent'); done(); finish(); },
        function (err) { say(err === 'busy' ? 'busy' : err === 'email' ? 'email' : err === 'missing' ? 'missing' : err === 'verify_failed' ? 'verify_failed' : 'failed', false); finish(); }, kindForm);
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

  // ---------- Founder confirmation page ----------
  var cf = $('[data-confirm]');
  if (cf) {
    var tok = (location.hash.match(/t=([0-9a-f]{48})/) || [])[1] || '';
    if (location.hash) history.replaceState(null, '', location.pathname);  // keep the token out of history and analytics
    var showState = function (st) { $$('.cf-state', cf).forEach(function (el) { el.hidden = el.getAttribute('data-state') !== st; }); };
    if (!tok) showState('invalid');
    else fetch(FN + 'founder-confirm', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ token: tok }) })
      .then(function (r) { return r.json(); }).then(function (b) {
        if (!b.ok) { track('founders/confirm-' + (b.status === 'expired' ? 'expired' : 'invalid')); return showState(b.status === 'expired' ? 'expired' : 'invalid'); }
        if (b.couple_status !== 'founder') { track('founders/confirmed-waitlist'); return showState('waitlist'); }
        if (b.status === 'confirmed') track(b.role === 'partner' ? 'founders/confirmed-partner' : 'founders/confirmed');
        $('[data-number]', cf).textContent = '#' + b.founder_number;
        $('[data-role-first]', cf).hidden = b.role === 'partner';
        $('[data-role-partner]', cf).hidden = b.role !== 'partner';
        if (b.role !== 'partner' && !b.couple_full && b.invite_url) {
          var box = $('[data-invite]', cf), url = b.invite_url;
          box.hidden = false; $('[data-invite-url]', box).value = url;
          var msg = (lang === 'ar' ? 'انضم إليّ في OneSpace — رقمنا كزوجين مؤسسين: ' : 'Join me on OneSpace — we are a Founder Couple: ') + url;
          $('[data-invite-wa]', box).href = 'https://wa.me/?text=' + encodeURIComponent(msg);
          $('[data-invite-wa]', box).addEventListener('click', function () { track('founders/invite-whatsapp'); });
          $('[data-invite-copy]', box).addEventListener('click', function () {
            var i = $('[data-invite-url]', box); i.select();
            (navigator.clipboard ? navigator.clipboard.writeText(url) : Promise.resolve(document.execCommand('copy'))).then(function () {});
            this.textContent = lang === 'ar' ? 'تم النسخ' : 'Copied'; track('founders/invite-copied');
          });
        }
        showState('ok');
      }).catch(function () { showState('invalid'); });
  }

  // ---------- Private admin dashboard ----------
  var adm = $('[data-admin]');
  if (adm) {
    var key = sget('os-admin') || '', days = 30;
    var esc = function (t) { return String(t == null ? '' : t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
    var num = function (n) { return (n == null ? '—' : Number(n).toLocaleString('en')); };
    var pct = function (a, b) { if (!b) return null; var v = 100 * a / b; return v >= 10 || v === 0 ? Math.round(v) : Math.round(v * 10) / 10; };
    var NAMES = {
      android: 'Android', ios: 'iPhone', both: 'One Android, one iPhone', unknown: 'Not given',
      honeypot: 'Robot field filled — dropped', checked: 'Too fast — asked for the check', passed: 'Passed the check — accepted',
      blocked: 'Failed the check — refused', unavailable: 'Check could not load — accepted', unverified: 'Cloudflare not reachable — accepted',
      apart: 'Living apart', together: 'Living together', en: 'English', ar: 'Arabic',
      friend: 'A friend told them', direct: 'Came straight to the site', search: 'Search', social: 'Social media', other: 'Other',
      'confirm:sent': 'Confirm-your-email · sent', 'welcome:sent': 'Welcome + Founder number · sent', 'already:sent': '“You’re already in” reminder · sent',
      'partner_joined:sent': 'Your partner joined · sent', 'confirm:failed': 'Confirm-your-email · FAILED', 'welcome:failed': 'Welcome · FAILED', 'confirm:skipped': 'Confirm-your-email · not sent'
    };
    var label = function (k) { return NAMES[k] || k; };
    var pageName = function (p) {
      if (!p) return '?'; var ar = /^\/ar(\/|$)/.test(p), q = p.replace(/^\/ar/, '').replace(/^\//, '').replace(/\.html$/, '');
      var nice = { '': 'Home', join: 'Join — Founding 500', 'how-it-works': 'Interactive demo', features: 'Features', faq: 'FAQ', tutorials: 'Tutorials',
        'living-apart': 'Living apart', 'living-together': 'Living together', 'share-kit': 'Share kit', support: 'Support', confirm: 'Email confirmed page', 'whats-new': 'What’s new' }[q];
      return (nice || q.replace(/-/g, ' ').replace(/^./, function (c) { return c.toUpperCase(); })) + (ar ? ' (Arabic)' : '');
    };
    var trend = function (cur, prev, noun) {
      if (prev == null || cur == null) return '';
      if (!prev && !cur) return '<span class="tr flat">Same as the previous ' + days + ' days</span>';
      if (!prev) return '<span class="tr up">▲ None in the previous ' + days + ' days</span>';
      var d = Math.round(100 * (cur - prev) / prev);
      if (!d) return '<span class="tr flat">Same as the previous ' + days + ' days</span>';
      return '<span class="tr ' + (d > 0 ? 'up' : 'down') + '">' + (d > 0 ? '▲ ' + d + '% more ' : '▼ ' + Math.abs(d) + '% fewer ') + noun + ' than the previous ' + days + ' days</span>';
    };
    var evName = function (k) {
      var parts = String(k).split('@'), e = parts[0], where = parts[1] ? ' (' + pageName('/' + parts[1].replace(/^\//, '') + (/\.html$|^$/.test(parts[1]) ? '' : '.html')) + ')' : '';
      var pre = { cta: 'Button', founders: 'Join form', demo: 'Demo', theme: 'Theme', lang: 'Language switch', outbound: 'Left to', email: 'Email link' }, i = e.indexOf('/');
      var head = i > 0 ? pre[e.slice(0, i)] || e.slice(0, i) : '', rest = (i > 0 ? e.slice(i + 1) : e).replace(/[-_\/]+/g, ' ');
      return (head ? head + ': ' : '') + rest + where;
    };
    var bars = function (obj, f, keep) { var tot = 0, k; for (k in obj) tot += obj[k]; if (!tot) return '<p class="muted">No data yet</p>';
      var ks = Object.keys(obj); if (!keep) ks.sort(function (a, b) { return obj[b] - obj[a]; });
      return ks.map(function (k) { var pc = Math.round(100 * obj[k] / tot);
        return '<div class="adm-bar"><span>' + esc((f || label)(k)) + '</span><i style="width:' + pc + '%"></i><b>' + obj[k] + ' · ' + pc + '%</b></div>'; }).join(''); };
    // GoatCounter breakdowns (sources, countries, devices, systems) also count clicks, so only their shares are meaningful.
    var shares = function (obj, f) { var tot = 0, k; for (k in obj) tot += obj[k]; if (!tot) return '<p class="muted">No data yet</p>';
      return Object.keys(obj).sort(function (a, b) { return obj[b] - obj[a]; }).map(function (k) { var pc = Math.round(100 * obj[k] / tot);
        return '<div class="adm-bar"><span>' + esc((f || label)(k)) + '</span><i style="width:' + pc + '%"></i><b>' + pc + '%</b></div>'; }).join(''); };
    var srows = function (list, k, f) { var obj = {}; (list || []).forEach(function (r) { if (r[k] !== '(unknown)') obj[r[k]] = (obj[r[k]] || 0) + r.n; }); return shares(obj, f); };
    var rows = function (list, k, f) { var obj = {}; (list || []).forEach(function (r) { obj[r[k]] = (obj[r[k]] || 0) + r.n; }); return bars(obj, f); };
    var card = function (o) {
      return '<div class="kpi' + (o.tone ? ' ' + o.tone : '') + '"><h3>' + o.title + '</h3><b>' + o.big + '</b>' + (o.bar != null ? '<div class="kpi-bar"><i style="width:' + Math.max(o.bar, o.bar ? 1 : 0) + '%"></i></div>' : '') +
        '<p>' + o.sub + '</p>' + (o.trend || '') + '<small>' + o.help + '</small></div>';
    };
    var load = function () {
      fetch(FN + 'founder-admin?days=' + days, { headers: { 'x-admin-key': key } }).then(function (r) { return r.json().then(function (b) { return { r: r, b: b }; }); })
      .then(function (x) {
        var st = $('[data-admin-login] .status');
        if (!x.r.ok) { try { sessionStorage.removeItem('os-admin'); } catch (_) {} st.textContent = x.b && x.b.error === 'key_not_set' ? 'FOUNDER_ADMIN_KEY is not set in Supabase › Edge Functions › Secrets.' : x.r.status === 401 ? 'That key does not match FOUNDER_ADMIN_KEY in Supabase.' : 'Could not load (' + x.r.status + ').'; return; }
        var s = x.b.stats, P = s.period || {}, cap = s.capacity_couples || 250, fc = s.founder_couples || 0, left = Math.max(0, cap - fc);
        var traffic = s.traffic_connected && !s.traffic_error && s.visitors != null;
        $('[data-admin-login]').hidden = true; $('[data-admin-body]').hidden = false;
        $('[data-updated]').textContent = 'Updated ' + new Date(s.generated_at).toLocaleString();

        // 1. Headline KPIs
        var pace = P.new_founder_couples >= 3 ? Math.ceil(left / (P.new_founder_couples / days)) : null;
        var conv = traffic ? pct(P.signups || 0, s.visitors) : null;
        var both = pct(s.couples_complete || 0, fc);
        $('[data-kpis]').innerHTML = [
          card({ title: 'Founder places taken', big: num(fc) + ' <em>of ' + cap + '</em>', bar: 100 * fc / cap,
            sub: left ? '<strong>' + num(left) + '</strong> places left' : '<strong>Full</strong> — new couples go to the waitlist (' + num(s.waitlist_couples) + ')',
            trend: P.new_founder_couples != null ? '<span class="tr ' + (P.new_founder_couples ? 'up' : 'flat') + '">+' + P.new_founder_couples + ' couples in the last ' + days + ' days</span>' : '',
            help: pace ? (pace > 365 ? 'At this pace it would take over a year to fill — more sharing needed.' : 'At this pace, all places are taken in about ' + num(pace) + ' days.') : 'A couple takes a place when the first partner confirms their email.' }),
          card({ title: 'New sign-ups', big: num(P.signups), sub: num(P.confirmed) + ' confirmed their email', trend: trend(P.signups, P.prev_signups, 'sign-ups'),
            help: 'People (not couples) who sent the Join form in the last ' + days + ' days.' }),
          card({ title: 'Visitors who sign up', big: conv == null ? '—' : conv + '%', tone: traffic ? '' : 'muted',
            sub: traffic ? num(P.signups) + ' sign-ups from ' + num(s.visitors) + ' page visits' + (P.signups ? ' · about 1 in ' + Math.max(1, Math.round(s.visitors / P.signups)) : '') : 'Needs the GoatCounter connection',
            trend: traffic ? trend(s.visitors, s.prev_visitors, 'page visits') : '',
            help: 'Your main website number: sign-ups compared with page visits.' }),
          card({ title: 'Couples with both partners', big: both == null ? '—' : both + '%', bar: both,
            sub: num(s.couples_complete) + ' complete · ' + num(s.couples_waiting_partner) + ' waiting for a partner',
            help: 'OneSpace needs two people. Every waiting couple is one invite away from complete.' })
        ].join('');

        // 2. Attention list
        var todo = [];
        if (s.turnstile_key_set === false) todo.push(['bad', 'The spam check can’t verify people: <code>TURNSTILE_SECRET_KEY</code> is missing in Supabase secrets, so fast sign-ups are accepted unchecked.']);
        if (!s.mail_key_set) todo.push(['bad', 'Emails are not being sent: <code>RESEND_API_KEY</code> is missing in Supabase secrets.']);
        if ((s.email_failures || []).length) todo.push(['bad', s.email_failures.length + ' email' + (s.email_failures.length > 1 ? 's' : '') + ' failed recently. Details under “Emails we sent”, or in <a href="https://resend.com/emails" target="_blank" rel="noopener">Resend</a>.']);
        if (s.pending_stale) todo.push(['warn', num(s.pending_stale) + ' ' + (s.pending_stale > 1 ? 'people' : 'person') + ' signed up over a day ago but never confirmed. <button class="btn btn-ghost btn-sm" type="button" data-resend>Send the confirmation email again</button> <span class="status" data-resend-status></span>']);
        if (s.couples_waiting_partner) todo.push(['info', num(s.couples_waiting_partner) + ' Founder couple' + (s.couples_waiting_partner > 1 ? 's have' : ' has') + ' only one partner so far. Their welcome email has an invite link — a reminder from the Command Center would help.']);
        if (!s.traffic_connected) todo.push(['info', 'Connect GoatCounter to see visitors here: GoatCounter → your name → API → new key with only “Read statistics”, then add it in Supabase secrets as <code>GOATCOUNTER_TOKEN</code>.']);
        if (s.traffic_error) todo.push(['warn', 'GoatCounter did not answer: ' + esc(s.traffic_error)]);
        if ((s.traffic_warnings || []).length) todo.push(['info', 'Some traffic lists could not load this time: ' + esc(s.traffic_warnings.map(function (w) { return w.replace(/^Error: /, ''); }).filter(function (w, i, a) { return a.indexOf(w) === i; }).join(' · ')) + '. Reload in a minute.']);
        $('[data-attention]').innerHTML = todo.length ? '<ul class="adm-todo">' + todo.map(function (t) { return '<li class="' + t[0] + '">' + t[1] + '</li>'; }).join('') + '</ul>'
          : '<ul class="adm-todo"><li class="ok">Nothing needs your attention. Emails are sending and nobody is stuck.</li></ul>';
        var rb = $('[data-resend]');
        if (rb) rb.addEventListener('click', function () {
          var out = $('[data-resend-status]'); out.textContent = 'Sending…'; rb.disabled = true;
          fetch(FN + 'founder-admin', { method: 'POST', headers: { 'x-admin-key': key, 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'resend_pending' }) })
            .then(function (r) { return r.json(); }).then(function (b) { out.textContent = b.ok ? 'Sent ' + b.sent + ' of ' + b.attempted + '.' : 'Failed.'; });
        });

        // 3. Funnel
        var tr = $('[data-traffic]');
        if (!traffic) tr.innerHTML = '<div class="panel adm-note">Visitor numbers appear here once GoatCounter is connected (see above). Meanwhile: <a href="https://onespace.goatcounter.com" target="_blank" rel="noopener">open GoatCounter</a>.</div>';
        else {
          var f = (s.funnel || []).slice(), top = Math.max(1, (f[0] || {}).n || 1), worst = null;
          f.forEach(function (st, i) { if (i && f[i - 1].n) { var lost = f[i - 1].n - st.n, r = lost / f[i - 1].n; if (lost > 0 && (!worst || r > worst.r)) worst = { r: r, from: f[i - 1].step, to: st.step, lost: lost }; } });
          var steps = f.map(function (st, i) {
            var w = Math.max(100 * st.n / top, st.n ? 2 : 0), kept = i && f[i - 1].n ? pct(st.n, f[i - 1].n) : null;
            return '<div class="fn-step"><div class="fn-head"><span>' + (i + 1) + '. ' + esc(st.step === 'Visitors' ? 'Page visits' : st.step) + '</span><b>' + num(st.n) + '</b></div><div class="fn-bar"><i style="width:' + w + '%"></i></div>' +
              (i ? '<small>' + (kept == null ? '—' : kept + '% continued from the step before') + '</small>' : '<small>pages opened (each page counted once per visit)</small>') + '</div>'; }).join('');
          var d = s.demo || {}, T = s.time || {}, TL = { '0-10s': 'under 10 sec', '10-30s': '10–30 sec', '30-60s': '30–60 sec', '1-3m': '1–3 min', '3-10m': '3–10 min', '10m-plus': 'over 10 min' };
          var dv = s.devices || {}, dvT = 0, k; for (k in dv) if (k !== 'Unknown') dvT += dv[k];
          var phone = dvT ? Math.round(100 * (dv.Phone || 0) / dvT) : null, c0 = (s.countries || [])[0], cTot = (s.countries || []).reduce(function (a, c) { return a + c.n; }, 0);
          var mini = function (o) { return '<div class="kpi kpi-s"><h3>' + o.t + '</h3><b>' + o.b + '</b><p>' + o.p + '</p>' + (o.tr || '') + '<small>' + o.h + '</small></div>'; };
          var glance = '<div class="kpi-grid kpi-6">' + [
            mini({ t: 'Page visits', b: num(s.visitors), p: (s.arabic_share != null ? s.arabic_share + '% of them in Arabic' : 'in the last ' + days + ' days'), tr: trend(s.visitors, s.prev_visitors, 'page visits'),
              h: 'Each page counted once per person per visit, without cookies. One person reading 3 pages = 3. Exact people can’t be counted without tracking.' }),
            mini({ t: 'Clicked Join', b: s.visitors ? pct((s.funnel || [])[1] ? s.funnel[1].n : 0, s.visitors) + '%' : '—', p: num((s.funnel || [])[1] ? s.funnel[1].n : 0) + ' clicks on a Join button',
              h: 'How often a page visit leads to a Join click. Low means the pages don’t make people want to join yet.' }),
            mini({ t: 'Time on a page', b: T.median ? TL[T.median] : '—', p: T.measured ? T.engaged_share + '% stayed 30 sec or more · ' + T.quick_exit_share + '% left within 10 sec' : 'Measuring started today — check back tomorrow',
              h: 'Typical (median) time a visitor actively looks at a page; only time with the tab visible counts.' }),
            mini({ t: 'Countries', b: num(s.country_count), p: c0 ? 'Top: ' + esc(c0.source) + ' · ' + Math.round(100 * c0.n / Math.max(1, cTot)) + '% of visits' : 'No data yet',
              h: 'Countries with at least one visitor, from the visitor’s network — no exact location is ever stored.' }),
            mini({ t: 'On a phone', b: phone == null ? '—' : phone + '%', p: dvT ? Math.round(100 * (dv.Computer || 0) / dvT) + '% on a computer · ' + Math.round(100 * (dv.Tablet || 0) / dvT) + '% on a tablet' : 'No data yet',
              h: 'Share of visitors on phone-sized screens. Your Join page must work perfectly on a phone.' }),
            mini({ t: 'Read to the end', b: s.visitors ? pct(s.read_to_end || 0, s.visitors) + '%' : '—', p: num(s.read_to_end) + ' page visits scrolled to the bottom',
              h: 'A sign of real interest. Measuring started today.' })
          ].join('') + '</div>';
          var vd = s.visitors_daily || [], vmx = Math.max.apply(null, vd.map(function (x) { return x.n; }).concat([1])), every2 = vd.length > 40 ? 10 : vd.length > 14 ? 5 : 1;
          var vchart = vd.length ? '<div class="panel"><h3>Page visits per day</h3><div class="adm-chart">' + '<div class="adm-y"><span>' + vmx + '</span><span>0</span></div>' + vd.map(function (x, i) {
            var lbl = (i % every2 === 0 || i === vd.length - 1) ? new Date(x.day + 'T12:00:00').toLocaleDateString('en', { month: 'short', day: 'numeric' }) : '';
            return '<div class="adm-col" title="' + x.day + ': ' + x.n + ' page visits"><i class="v" style="height:' + (100 * x.n / vmx) + '%"></i><span>' + lbl + '</span></div>'; }).join('') + '</div></div>' : '';
          var timeObj = {}; (T.buckets || []).forEach(function (b) { if (b.n) timeObj[TL[b.bucket]] = b.n; });
          tr.innerHTML = glance + '<div class="adm-row">' + vchart + '</div>' +
            '<div class="adm-row adm-2"><div class="panel"><h3>The path to joining</h3>' + steps +
            (worst ? '<p class="adm-insight">Biggest drop: <strong>' + esc(worst.from) + ' → ' + esc(worst.to) + '</strong> — ' + Math.round(100 * worst.r) + '% stop here (' + num(worst.lost) + ' people). This is the step to improve first.</p>' : '') +
            '<p class="muted" style="font-size:12px">Steps 2–5 are counted as clicks, so one person can count more than once. Confirmed Founders below come from the database.</p></div>' +
            '<div class="panel"><h3>Interest in the product</h3><div class="mini-grid">' +
            '<div><b>' + num(d.demo_clicks) + '</b><span>opened the demo from a button</span></div><div><b>' + num(d.tour_finished) + '</b><span>finished the guided demo tour</span></div>' +
            '<div><b>' + num(d.theme_picks) + '</b><span>tried a colour theme</span></div><div><b>' + num(d.outbound_store) + '</b><span>went to Google Play / App Store</span></div></div>' +
            '<h3 style="margin-top:18px">Time on a page</h3>' + bars(timeObj, String, true) + '</div></div>' +
            '<div class="adm-row adm-3"><div class="panel"><h3>Where visitors come from</h3>' + srows(s.referrers, 'source', function (k) { return k === '(direct)' ? 'Typed the address / bookmark / app' : k; }) +
            ((s.campaigns || []).length ? '<h3 style="margin-top:18px">Campaign links (utm)</h3>' + rows(s.campaigns, 'source', String) : '') + '</div>' +
            '<div class="panel"><h3>Countries</h3>' + srows(s.countries, 'source', String) + '</div>' +
            '<div class="panel"><h3>Devices</h3>' + shares((function () { var o = {}; for (var k in dv) if (k !== 'Unknown' && dv[k]) o[k] = dv[k]; return o; })(), String) + '<h3 style="margin-top:18px">Phone / computer system</h3>' + srows(s.systems, 'source', String) +
            ((s.languages || []).some(function (r) { return r.source !== '(unknown)'; }) ? '<h3 style="margin-top:18px">Browser language</h3>' + srows(s.languages, 'source', String) : '') + '</div></div>' +
            '<div class="adm-row adm-2"><div class="panel"><h3>Most-viewed pages</h3>' + rows(s.top_pages, 'page', pageName) + '</div>' +
            '<div class="panel"><h3>Most-clicked buttons and actions</h3>' + rows(s.top_events, 'event', evName) + '</div></div>';
        }

        // 4. Sign-ups chart
        var dl = s.daily || [], mx = Math.max.apply(null, dl.map(function (d) { return d.signups; }).concat([1]));
        var tS = dl.reduce(function (a, d) { return a + d.signups; }, 0), tC = dl.reduce(function (a, d) { return a + d.confirmed; }, 0);
        var best = dl.reduce(function (a, d) { return d.signups > (a ? a.signups : 0) ? d : a; }, null);
        $('[data-chart-sum]').innerHTML = '<strong>' + num(tS) + '</strong> signed up and <strong>' + num(tC) + '</strong> confirmed in the last ' + days + ' days' +
          (best ? ' · best day: ' + new Date(best.day + 'T12:00:00').toLocaleDateString('en', { month: 'short', day: 'numeric' }) + ' (' + best.signups + ')' : '') + '.';
        var every = dl.length > 40 ? 10 : dl.length > 14 ? 5 : 1;
        $('[data-chart]').innerHTML = '<div class="adm-y"><span>' + mx + '</span><span>0</span></div>' + dl.map(function (d, i) {
          var lbl = (i % every === 0 || i === dl.length - 1) ? new Date(d.day + 'T12:00:00').toLocaleDateString('en', { month: 'short', day: 'numeric' }) : '';
          return '<div class="adm-col" title="' + d.day + ': ' + d.signups + ' signed up, ' + d.confirmed + ' confirmed"><i style="height:' + (100 * d.signups / mx) + '%"></i><i class="c" style="height:' + (100 * d.confirmed / mx) + '%"></i><span>' + lbl + '</span></div>'; }).join('');

        // 5. Who
        $('[data-bars="platform"]').innerHTML = bars(s.platform || {});
        $('[data-bars="living"]').innerHTML = bars(s.living || {});
        $('[data-bars="language"]').innerHTML = bars(s.language || {});
        $('[data-bars="emails"]').innerHTML = bars(s.emails || {});
        var spamEl = $('[data-bars="spam"]');
        if (spamEl) spamEl.innerHTML = s.spam && Object.keys(s.spam).length ? bars(s.spam) : '<p class="muted">No spam checks in this period.</p>';
        $('[data-list="sources"]').innerHTML = rows(s.sources, 'source');
        $('[data-list="landing"]').innerHTML = rows(s.landing, 'page', pageName);
        $('[data-failures]').innerHTML = (s.email_failures || []).slice(0, 5).map(function (f) { return '<p class="muted" style="font-size:12px">⚠ ' + esc(f.at.slice(0, 16).replace('T', ' ') + ' · ' + label(f.kind) + ' · ' + (f.error || '')) + '</p>'; }).join('');
      }).catch(function () { $('[data-admin-login] .status').textContent = 'Could not load.'; });
    };
    $$('[data-days]').forEach(function (b) { b.addEventListener('click', function () { days = +b.getAttribute('data-days');
      $$('[data-days]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); }); load(); }); });
    $('[data-admin-login]').addEventListener('submit', function (e) { e.preventDefault(); key = $('#ak').value.trim(); try { sessionStorage.setItem('os-admin', key); } catch (_) {} load(); });
    if (key) load();
  }

  // ---------- Unsubscribe page ----------
  var us = $('[data-unsub]');
  if (us) {
    var ut = (location.hash.match(/u=([0-9a-f]{32})/) || [])[1] || '';
    if (location.hash) history.replaceState(null, '', location.pathname);
    var ushow = function (st) { $$('.cf-state', us).forEach(function (el) { el.hidden = el.getAttribute('data-state') !== st; }); };
    if (!ut) ushow('invalid');
    $('[data-unsub-go]', us).addEventListener('click', function () {
      this.disabled = true;
      fetch(FN + 'founder-unsubscribe', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ u: ut }) })
        .then(function (r) { return r.json(); }).then(function (b) { if (b.ok) { track('founders/unsubscribed'); ushow('done'); } else ushow('invalid'); })
        .catch(function () { ushow('invalid'); });
    });
  }

  // ---------- Clips: play only while on screen ----------
  var clips = $$('video[data-autoplay]');
  if (clips.length) {
    if ('IntersectionObserver' in window && !reduce) {
      var vio = new IntersectionObserver(function (es) { es.forEach(function (e) {
        var v = e.target;
        if (e.isIntersecting) { if (v.preload === 'none') v.preload = 'auto'; var pr = v.play(); if (pr && pr.catch) pr.catch(function () {}); }
        else v.pause();
      }); }, { threshold: 0.35 });
      clips.forEach(function (v) { vio.observe(v); });
    } else clips.forEach(function (v) { v.controls = true; });
  }

  // ---------- Mobile: a Join bar once you scroll, hidden near any join form ----------
  var bar = $('[data-sticky-cta]');
  var noBar = /\/(ar\/)?(join|confirm|unsubscribe|founders-admin)\.html$/.test(location.pathname);
  if (bar && !noBar && 'IntersectionObserver' in window) {
    var forms = $$('form[data-form="join"], #founding, footer');
    if ($('#founding')) $('a', bar).setAttribute('href', '#founding');
    var scrolled = false;
    var upd = function () { bar.hidden = !(scrolled && !forms.some(function (x) { return x._in; })) || (menu && menu.classList.contains('open')); };
    if (burger) burger.addEventListener('click', function () { setTimeout(upd, 0); });
    forms.forEach(function (f) {
      new IntersectionObserver(function (es) { es.forEach(function (e) { f._in = e.isIntersecting; }); upd(); }).observe(f);
    });
    window.addEventListener('scroll', function () { var s = window.scrollY > 700; if (s !== scrolled) { scrolled = s; upd(); } }, { passive: true });
  }
})();
/* Show / hide a password field */
document.querySelectorAll('[data-pw-toggle]').forEach(function(b){
  var inp=document.getElementById(b.getAttribute('aria-controls')); if(!inp) return;
  b.addEventListener('click',function(){
    var show=inp.type==='password'; inp.type=show?'text':'password';
    b.setAttribute('aria-pressed',show?'true':'false');
    var l=show?'Hide key':'Show key'; b.setAttribute('aria-label',l); b.title=l; inp.focus();
  });
});
