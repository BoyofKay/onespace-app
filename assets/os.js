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
    name = String(name).replace(/[^\w\/@.\-]/g, '-').slice(0, 120);
    gcQueue.push(name);
    if (!flush()) { var tries = 0, t = setInterval(function () { if (flush() || ++tries > 40) clearInterval(t); }, 250); }
  }
  window.osTrack = track;
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
    failed: 'Could not send. Please check your connection and try again.', sent: 'Thank you — we got it and will reply by email.' };
  $$('form[data-form]').forEach(function (form) {
    var fname = form.getAttribute('data-form') === 'join' ? 'founders' : form.getAttribute('data-form');
    form.addEventListener('focusin', function () { if (!form.dataset.started) { form.dataset.started = '1'; track(fname + '/form-start' + here); } });
    var topic = new URLSearchParams(location.search).get('topic');
    if (topic && form.elements.topic) form.elements.topic.value = topic;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var status = $('.status', form);
      function say(k, ok) { status.textContent = tr('form.' + k, msgs[k]); status.className = 'status ' + (ok === true ? 'ok' : ok === false ? 'err' : '');
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
        var t = v('topic'); kind = t === 'issue' ? 'issue' : (t === 'signin' ? 'account' : 'contact');
        subject = ((t ? t + ' · ' : '') + (v('subject') || 'Website message')).slice(0, 160);
        if (v('name')) message = 'Name: ' + v('name') + '\n\n' + message;
      }
      var btn = $('button[type=submit]', form); btn.disabled = true; say('sending');
      if (kindForm === 'join') {
        var sj = function (k) { try { return sessionStorage.getItem(k) || ''; } catch (_) { return ''; } };
        var utm = {}; try { utm = JSON.parse(sj('os-utm') || '{}'); } catch (_) {}
        var language = v('language'); if (language !== 'ar' && language !== 'en') language = lang;
        fetch(FN + 'founder-join', { method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: email, name: v('name'), platform: v('platform'), living: v('living'), language: language,
            source: v('source'), note: v('message'), consent: true, website: v('website'), elapsed: Date.now() - loadedAt,
            invite: v('invite') || invite, landing: sj('os-landing'), referrer: sj('os-ref'), utm: utm }) })
        .then(function (res) { return res.json().catch(function () { return {}; }).then(function (b) { return { res: res, b: b }; }); })
        .then(function (x) {
          if (x.res.ok && x.b.ok) {
            track('founders/sent');
            var pl = v('platform'); if (pl) track('founders/platform-' + pl);
            if (v('invite') || invite) track('founders/sent-partner');
            form.reset();
            var done = form.getAttribute('data-done') && document.getElementById(form.getAttribute('data-done'));
            if (done) { form.hidden = true; done.classList.add('show'); done.focus(); } else say('sent', true);
          } else say(x.b.error === 'rate_limited' ? 'busy' : x.b.error === 'invalid_email' ? 'email' : x.b.error === 'consent_required' ? 'consent' : 'failed', false);
        }).catch(function () { say('failed', false); }).then(function () { btn.disabled = false; });
        return;
      }
      fetch(FN + 'site-contact', { method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ form: kindForm, topic: v('topic'), name: v('name'), email: email, subject: v('subject'), message: message,
          website: v('website'), elapsed: Date.now() - loadedAt, page: location.pathname, lang: lang, src: sget('os-src') || '' }) })
      .then(function (res) { return res.json().catch(function () { return {}; }).then(function (b) { return { res: res, b: b }; }); })
      .then(function (x) {
        if (x.res.ok && x.b.ok) {
          track(kindForm + '/sent');
          form.reset();
          var done = form.getAttribute('data-done') && document.getElementById(form.getAttribute('data-done'));
          if (done) { form.hidden = true; done.classList.add('show'); done.focus(); } else say('sent', true);
        } else say(x.b.error === 'busy' ? 'busy' : x.b.error === 'email' ? 'email' : x.b.error === 'missing' ? 'missing' : 'failed', false);
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

  // ---------- Private waitlist dashboard ----------
  var adm = $('[data-admin]');
  if (adm) {
    var key = sget('os-admin') || '', days = 30;
    var esc = function (t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
    var bars = function (obj) { var tot = 0, k; for (k in obj) tot += obj[k]; if (!tot) return '<p class="muted">No data yet</p>';
      return Object.keys(obj).sort(function (a, b) { return obj[b] - obj[a]; }).map(function (k) { var pc = Math.round(100 * obj[k] / tot);
        return '<div class="adm-bar"><span>' + esc(k) + '</span><i style="width:' + pc + '%"></i><b>' + obj[k] + ' · ' + pc + '%</b></div>'; }).join(''); };
    var load = function () {
      fetch(FN + 'founder-admin?days=' + days, { headers: { 'x-admin-key': key } }).then(function (r) { return r.json().then(function (b) { return { r: r, b: b }; }); })
      .then(function (x) {
        var st = $('[data-admin-login] .status');
        if (!x.r.ok) { try { sessionStorage.removeItem('os-admin'); } catch (_) {} st.textContent = 'Wrong key.'; return; }
        var s = x.b.stats;
        $('[data-admin-login]').hidden = true; $('[data-admin-body]').hidden = false;
        var tiles = [['Founder couples', s.founder_couples + ' / ' + s.capacity_couples], ['Founder places left', s.capacity_couples - s.founder_couples],
          ['Sign-ups', s.signups_total], ['Confirmed', s.confirmed], ['Waiting to confirm', s.pending], ['Confirm rate', s.confirm_rate == null ? '—' : s.confirm_rate + '%'],
          ['Partners joined', s.partners_joined], ['Waitlist couples', s.waitlist_couples]];
        if (s.visitors != null) tiles.push(['Visitors → sign-up', s.visitors ? (100 * s.signups_total / s.visitors).toFixed(1) + '% of ' + s.visitors : '—']);
        if (!s.mail_key_set) tiles.push(['Email', '⚠ RESEND_API_KEY missing']);
        $('[data-tiles]').innerHTML = tiles.map(function (t) { return '<div class="adm-tile"><span>' + t[0] + '</span><b>' + esc(t[1]) + '</b></div>'; }).join('');
        var max = Math.max.apply(null, s.daily.map(function (d) { return d.signups; }).concat([1]));
        $('[data-chart]').innerHTML = s.daily.map(function (d) {
          return '<div class="adm-col" title="' + d.day + ': ' + d.signups + ' signed up, ' + d.confirmed + ' confirmed"><i style="height:' + (100 * d.signups / max) + '%"></i><i class="c" style="height:' + (100 * d.confirmed / max) + '%"></i><span>' + d.day.slice(8) + '</span></div>'; }).join('');
        ['platform', 'living', 'language', 'emails'].forEach(function (k) { $('[data-bars="' + k + '"]').innerHTML = bars(s[k] || {}); });
        ['sources', 'landing'].forEach(function (k) { $('[data-list="' + k + '"]').innerHTML = (s[k] || []).map(function (r) { return '<div class="adm-bar"><span>' + esc(r.source || r.page) + '</span><b>' + r.n + '</b></div>'; }).join('') || '<p class="muted">No data yet</p>'; });
        $('[data-failures]').innerHTML = (s.email_failures || []).slice(0, 5).map(function (f) { return '<p class="muted" style="font-size:12px">⚠ ' + esc(f.at.slice(0, 16).replace('T', ' ') + ' · ' + f.kind + ' · ' + (f.error || '')) + '</p>'; }).join('');
        $('[data-updated]').textContent = 'Updated ' + new Date(s.generated_at).toLocaleString();
        var tr = $('[data-traffic]');
        if (!s.traffic_connected) tr.innerHTML = '<div class="panel adm-note"><b>Connect GoatCounter to see traffic here.</b> In GoatCounter: your name (top right) → API → New API key, tick only “Read statistics”. Then in Supabase › Edge Functions › Secrets add <code>GOATCOUNTER_TOKEN</code>. Until then, open <a href="https://onespace.goatcounter.com" target="_blank" rel="noopener">onespace.goatcounter.com</a>.</div>';
        else if (s.traffic_error) tr.innerHTML = '<div class="panel adm-note">GoatCounter did not answer: ' + esc(s.traffic_error) + '</div>';
        else {
          var f = s.funnel || [], top = Math.max(1, (f[0] || {}).n || 1);
          var funnel = f.map(function (st, i) { var pc = i === 0 ? 100 : Math.round(100 * st.n / top); var step = i > 0 && f[i - 1].n ? Math.round(100 * st.n / f[i - 1].n) + '% of previous' : '';
            return '<div class="adm-funnel"><span>' + esc(st.step) + '</span><i style="width:' + Math.max(pc, 1) + '%"></i><b>' + st.n + '</b><small>' + (i ? pc + '% of visitors · ' + step : '') + '</small></div>'; }).join('');
          var list = function (rows, k) { return (rows || []).map(function (r) { return '<div class="adm-bar"><span>' + esc(r[k]) + '</span><b>' + r.n + '</b></div>'; }).join('') || '<p class="muted">No data yet</p>'; };
          var d = s.demo || {};
          tr.innerHTML = '<div class="adm-row"><div class="panel"><h3>Funnel</h3>' + funnel + '<p class="muted" style="font-size:12px">Clicks and form steps are counted as events; confirmed sign-ups below come from the database.</p></div></div>' +
            '<div class="adm-grid"><div class="adm-tile"><span>Visitors</span><b>' + s.visitors + '</b></div><div class="adm-tile"><span>Visitor → confirmed</span><b>' + (s.visitors ? (100 * s.confirmed / s.visitors).toFixed(1) + '%' : '—') + '</b></div>' +
            '<div class="adm-tile"><span>Demo tours finished</span><b>' + (d.tour_finished || 0) + '</b></div><div class="adm-tile"><span>Theme picks</span><b>' + (d.theme_picks || 0) + '</b></div></div>' +
            '<div class="adm-row adm-3"><div class="panel"><h3>Top pages</h3>' + list(s.top_pages, 'page') + '</div><div class="panel"><h3>Where visitors came from</h3>' + list(s.referrers, 'source') + '</div><div class="panel"><h3>Countries</h3>' + list(s.countries, 'source') + '</div></div>' +
            '<div class="adm-row"><div class="panel"><h3>Top events</h3>' + list(s.top_events, 'event') + '</div></div>';
        }
      }).catch(function () { $('[data-admin-login] .status').textContent = 'Could not load.'; });
    };
    $$('[data-days]').forEach(function (b) { b.addEventListener('click', function () { days = +b.getAttribute('data-days');
      $$('[data-days]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); }); load(); }); });
    $('[data-admin-login]').addEventListener('submit', function (e) { e.preventDefault(); key = $('#ak').value.trim(); try { sessionStorage.setItem('os-admin', key); } catch (_) {} load(); });
    $('[data-resend]').addEventListener('click', function () {
      var out = $('[data-resend-status]'); out.textContent = 'Sending…';
      fetch(FN + 'founder-admin', { method: 'POST', headers: { 'x-admin-key': key, 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'resend_pending' }) })
        .then(function (r) { return r.json(); }).then(function (b) { out.textContent = b.ok ? 'Sent ' + b.sent + ' of ' + b.attempted + '.' : 'Failed.'; load(); });
    });
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
