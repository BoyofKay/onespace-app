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
  // English/Arabic share the full page tree. Spanish, French and German have
  // indexable localized landing pages; never navigate to a non-existent twin.
  var english = new WeakMap();
  var lang = /^(en|ar|es|fr|de)$/.test(root.lang) ? root.lang : 'en';
  function twin(to) {
    var p = location.pathname, rest = p.replace(/^\/(ar|es|fr|de)(?=\/|$)/, '') || '/';
    var dest = (to === 'en' ? rest : '/' + to + rest);
    return dest + location.search.replace(/[?&]lang=(en|ar|es|fr|de)/, '').replace(/^&/, '?') + location.hash;
  }
  var browserLang = (navigator.language || '').toLowerCase().slice(0, 2);
  var want = new URLSearchParams(location.search).get('lang') || get('os-lang') ||
    (!get('os-lang-seen') && /^(ar|es|fr|de)$/.test(browserLang) ? browserLang : null);
  put('os-lang-seen', '1');
  // An explicit localized URL must always win over saved/browser language.
  // Otherwise a returning Spanish visitor cannot directly open a German link.
  var routeLanguage = (location.pathname.match(/^\/(ar|es|fr|de)(?:\/|$)/) || [])[1];
  if (!routeLanguage && /^(en|ar|es|fr|de)$/.test(want || '') && want !== lang && location.protocol !== 'file:') {
    location.replace(twin(want)); return;
  }
  function tr(key, en) { var local = window.ONESPACE_SITE_STRINGS || {}; return local[key] || (lang === 'ar' && AR[key] ? AR[key] : en); }

  // Landing-page interest goes through one canonical Founder form at /join.html.
  // Keep the partner invite and campaign parameters in the destination URL.
  (function simplifyFounderSignup() {
    var homeForm = $('#founding form[data-form="join"]');
    if (homeForm) {
      var panel = homeForm.closest('.panel');
      var heading = homeForm.querySelector('h3');
      var submit = homeForm.querySelector('button[type="submit"]');
      var originalLabel = submit ? submit.textContent.trim() : 'Join the Founding 500';
      var intro = document.createElement('div');
      intro.className = 'join-entry';
      var symbol = document.createElement('span');
      symbol.className = 'join-entry-icon';
      symbol.setAttribute('aria-hidden', 'true');
      symbol.textContent = '♡';
      var title = document.createElement('h3');
      title.textContent = heading ? heading.textContent.trim() : originalLabel;
      var link = document.createElement('a');
      link.className = 'btn btn-primary';
      link.href = 'join.html' + location.search;
      link.setAttribute('data-track', 'founder_join_canonical');
      link.textContent = originalLabel;
      var assurance = document.createElement('p');
      var oldAssurance = homeForm.querySelector('.muted');
      assurance.textContent = oldAssurance ? oldAssurance.textContent.trim() : '';
      intro.appendChild(symbol);
      intro.appendChild(title);
      intro.appendChild(link);
      if (assurance.textContent) intro.appendChild(assurance);
      if (panel) panel.replaceChildren(intro);
    }
    // On the single signup page, keep the questions that actually register
    // a Founder visible. Secondary research questions are optional.
    var signup = $('form[data-form="join"]');
    if (signup && !homeForm) {
      var living = signup.querySelector('input[name="living"]');
      var group = living && living.closest('.radio-cards');
      var first = group && group.previousElementSibling;
      var before = signup.querySelector('input.hp');
      if (first && before && first.parentNode === before.parentNode) {
        var details = document.createElement('details');
        details.className = 'join-optional';
        var summary = document.createElement('summary');
        summary.textContent = ({
          en:'More about you (optional)',
          ar:'تفاصيل إضافية (اختياري)',
          es:'Más detalles (opcional)',
          fr:'Quelques précisions (facultatif)',
          de:'Weitere Angaben (optional)'
        })[lang] || 'More about you (optional)';
        details.appendChild(summary);
        var node = first;
        while (node && node !== before) {
          var next = node.nextSibling;
          details.appendChild(node);
          node = next;
        }
        signup.insertBefore(details, before);
      }
    }
  })();

  // Each legal document and translation has its own explicit published date
  // and revision number; never stamp all documents with today's visit date.
  (function displayLegalRevision() {
    var match = location.pathname.match(new RegExp('(?:^|/)(privacy|terms|delete-account)[.]html$'));
    if (!match) return;
    var doc = match[1];
    fetch('/assets/legal-revisions.json', {cache: 'no-cache'}).then(function (r) {
      if (!r.ok) throw Error('revision metadata unavailable');
      return r.json();
    }).then(function (records) {
      var entry = records[doc] && (records[doc][lang] || records[doc].en);
      if (!entry || !new RegExp('^[0-9]{4}-[0-9]{2}-[0-9]{2}$').test(entry.date)) return;
      var container = $('.legal');
      if (!container) return;
      var el = $('.legal > p.muted');
      if (!el) {
        el = document.createElement('p');
        container.insertBefore(el, container.firstChild);
      }
      el.className = 'legal-revision';
      var words = {
        en:['Last updated: ','Version '],
        ar:['آخر تحديث: ','الإصدار '],
        es:['Última actualización: ','Versión '],
        fr:['Dernière mise à jour : ','Version '],
        de:['Zuletzt aktualisiert: ','Version ']
      }[lang] || ['Last updated: ','Version '];
      var calendar = new Date(entry.date + 'T12:00:00Z');
      var formatted = new Intl.DateTimeFormat(lang, {day:'numeric', month:'long', year:'numeric', timeZone:'UTC'}).format(calendar);
      var time = document.createElement('time');
      time.dateTime = entry.date;
      time.textContent = formatted;
      el.replaceChildren(document.createTextNode(words[0]), time,
        document.createTextNode(' · ' + words[1] + entry.version));
    }).catch(function () { /* Static legal date remains available without JS/network. */ });
  })();
  function apply() {
    root.lang = lang; root.dir = lang === 'ar' ? 'rtl' : 'ltr';
    $$('[data-i18n]').forEach(function (el) {
      if (!english.has(el)) english.set(el, el.innerHTML);
      var k = el.getAttribute('data-i18n');
      el.innerHTML = lang === 'ar' && AR[k] ? AR[k] : english.get(el);
    });
    $$('[data-i18n-attr]').forEach(function (el) {
      el.getAttribute('data-i18n-attr').split(';').forEach(function (pair) {
        var p = pair.split(':'); var attr = p[0], k = p[1], store = 'data-en-' + attr;
        if (!el.hasAttribute(store)) el.setAttribute(store, el.getAttribute(attr) || '');
        el.setAttribute(attr, lang === 'ar' && AR[k] ? AR[k] : el.getAttribute(store));
      });
    });
    $$('[data-ar-src]').forEach(function (m) {
      var src = m.getAttribute(lang === 'ar' ? 'data-ar-src' : 'data-en-src');
      if (src && m.getAttribute('src') !== src) m.setAttribute('src', src);
      var poster = m.getAttribute(lang === 'ar' ? 'data-ar-poster' : 'data-en-poster');
      if (poster) m.setAttribute('poster', poster);
    });
    var t = document.querySelector('title');
    if (t && t.dataset.ar) { if (!t.dataset.en) t.dataset.en = t.textContent; t.textContent = lang === 'ar' ? t.dataset.ar : t.dataset.en; }
  }
  if (lang === 'ar') apply();
  $$('[data-language-switch]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      var to = link.getAttribute('data-language-switch');
      if (!/^(en|ar|es|fr|de)$/.test(to || '')) return;
      put('os-lang', to); track('lang/' + to);
      var target = new URL(link.href, location.href);
      // Campaign identifiers survive a language switch without adding personal tokens.
      ['utm_source','utm_medium','utm_campaign','utm_content','utm_term','ref'].forEach(function (k) {
        if (params.get(k) && !target.searchParams.has(k)) target.searchParams.set(k, params.get(k).slice(0, 80));
      });
      if (target.href !== link.href) { e.preventDefault(); location.href = target.href; }
    });
  });

  // ---------- Click-to-open full-width mega navigation (mobile: accordion) ----------
  var burger = $('.burger'), menu = $('.menu');
  var backdrop = document.createElement('div');
  backdrop.className = 'mega-backdrop'; backdrop.hidden = true;
  backdrop.setAttribute('aria-hidden', 'true');
  if (menu) document.body.appendChild(backdrop);
  var lastMenuTrigger = null;
  function syncBackdrop() {
    var expanded = $$('.drop.open', menu || document).length > 0;
    backdrop.hidden = !(expanded || (menu && menu.classList.contains('open')));
  }
  function closeMega(focusTrigger) {
    $$('.drop.open', menu || document).forEach(function (d) {
      d.classList.remove('open');
      var b = $('button[aria-expanded]', d);
      if (b) b.setAttribute('aria-expanded', 'false');
    });
    if (menu) menu.classList.remove('open');
    if (burger) burger.setAttribute('aria-expanded', 'false');
    syncBackdrop();
    if (focusTrigger && lastMenuTrigger && document.contains(lastMenuTrigger)) lastMenuTrigger.focus();
  }
  if (burger && menu) burger.addEventListener('click', function () {
    var wasOpen = menu.classList.contains('open');
    closeMega(false);
    if (!wasOpen) { menu.classList.add('open'); burger.setAttribute('aria-expanded', 'true'); }
    syncBackdrop();
  });
  $$('.drop > button').forEach(function (b) {
    b.addEventListener('click', function () {
      var drop = b.parentElement, wasOpen = drop.classList.contains('open');
      $$('.drop.open', menu || document).forEach(function (d) {
        d.classList.remove('open');
        var other = $('button[aria-expanded]', d);
        if (other) other.setAttribute('aria-expanded', 'false');
      });
      if (!wasOpen) {
        drop.classList.add('open'); b.setAttribute('aria-expanded', 'true');
        lastMenuTrigger = b;
      }
      syncBackdrop();
    });
  });
  if (menu) {
    menu.addEventListener('click', function (event) {
      if (event.target.closest('a')) closeMega(false);
    });
    backdrop.addEventListener('click', function () { closeMega(false); });
    document.addEventListener('click', function (event) {
      if (!event.target.closest('.top') && !event.target.closest('.mega-backdrop')) closeMega(false);
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && !backdrop.hidden) {
        event.preventDefault();
        closeMega(true);
      }
    });
    window.addEventListener('resize', function () { if (!backdrop.hidden) closeMega(false); });
  }
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
  $$('form[data-form="join"] select[name="language"]').forEach(function (sel) { sel.value = lang === 'ar' ? 'ar' : 'en'; });
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
        ts.render(box, { sitekey: TS_KEY, language: lang, theme: 'auto',
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
      function say(k, ok) { var local = window.ONESPACE_FORM_MESSAGES || {}; status.textContent = local[k] || (lang === 'ar' && msgsAr[k] ? msgsAr[k] : tr('form.' + k, msgs[k])); status.className = 'status ' + (ok === true ? 'ok' : ok === false ? 'err' : '');
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
            this.textContent = tr('founders.invite-copied', lang === 'ar' ? 'تم النسخ' : 'Copied'); track('founders/invite-copied');
          });
        }
        showState('ok');
      }).catch(function () { showState('invalid'); });
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
  var noBar = /\/(ar\/)?(join|confirm|unsubscribe)\.html$/.test(location.pathname);
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
    var l=show?tr('password.hide','Hide key'):tr('password.show','Show key'); b.setAttribute('aria-label',l); b.title=l; inp.focus();
  });
});
));
    if (!match) return;
    var doc = match[1];
    fetch('/assets/legal-revisions.json', {cache: 'no-cache'}).then(function (r) {
      if (!r.ok) throw Error('revision metadata unavailable');
      return r.json();
    }).then(function (records) {
      var entry = records[doc] && (records[doc][lang] || records[doc].en);
      if (!entry || !/^\\d{4}-\\d{2}-\\d{2}$/.test(entry.date)) return;
      var container = $('.legal');
      if (!container) return;
      var el = $('.legal > p.muted');
      if (!el) {
        el = document.createElement('p');
        container.insertBefore(el, container.firstChild);
      }
      el.className = 'legal-revision';
      var words = {
        en:['Last updated: ','Version '],
        ar:['آخر تحديث: ','الإصدار '],
        es:['Última actualización: ','Versión '],
        fr:['Dernière mise à jour : ','Version '],
        de:['Zuletzt aktualisiert: ','Version ']
      }[lang] || ['Last updated: ','Version '];
      var calendar = new Date(entry.date + 'T12:00:00Z');
      var formatted = new Intl.DateTimeFormat(lang, {day:'numeric', month:'long', year:'numeric', timeZone:'UTC'}).format(calendar);
      var time = document.createElement('time');
      time.dateTime = entry.date;
      time.textContent = formatted;
      el.replaceChildren(document.createTextNode(words[0]), time,
        document.createTextNode(' · ' + words[1] + entry.version));
    }).catch(function () { /* Static legal date remains available without JS/network. */ });
  })();
  function apply() {
    root.lang = lang; root.dir = lang === 'ar' ? 'rtl' : 'ltr';
    $$('[data-i18n]').forEach(function (el) {
      if (!english.has(el)) english.set(el, el.innerHTML);
      var k = el.getAttribute('data-i18n');
      el.innerHTML = lang === 'ar' && AR[k] ? AR[k] : english.get(el);
    });
    $$('[data-i18n-attr]').forEach(function (el) {
      el.getAttribute('data-i18n-attr').split(';').forEach(function (pair) {
        var p = pair.split(':'); var attr = p[0], k = p[1], store = 'data-en-' + attr;
        if (!el.hasAttribute(store)) el.setAttribute(store, el.getAttribute(attr) || '');
        el.setAttribute(attr, lang === 'ar' && AR[k] ? AR[k] : el.getAttribute(store));
      });
    });
    $$('[data-ar-src]').forEach(function (m) {
      var src = m.getAttribute(lang === 'ar' ? 'data-ar-src' : 'data-en-src');
      if (src && m.getAttribute('src') !== src) m.setAttribute('src', src);
      var poster = m.getAttribute(lang === 'ar' ? 'data-ar-poster' : 'data-en-poster');
      if (poster) m.setAttribute('poster', poster);
    });
    var t = document.querySelector('title');
    if (t && t.dataset.ar) { if (!t.dataset.en) t.dataset.en = t.textContent; t.textContent = lang === 'ar' ? t.dataset.ar : t.dataset.en; }
  }
  if (lang === 'ar') apply();
  $$('[data-language-switch]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      var to = link.getAttribute('data-language-switch');
      if (!/^(en|ar|es|fr|de)$/.test(to || '')) return;
      put('os-lang', to); track('lang/' + to);
      var target = new URL(link.href, location.href);
      // Campaign identifiers survive a language switch without adding personal tokens.
      ['utm_source','utm_medium','utm_campaign','utm_content','utm_term','ref'].forEach(function (k) {
        if (params.get(k) && !target.searchParams.has(k)) target.searchParams.set(k, params.get(k).slice(0, 80));
      });
      if (target.href !== link.href) { e.preventDefault(); location.href = target.href; }
    });
  });

  // ---------- Click-to-open full-width mega navigation (mobile: accordion) ----------
  var burger = $('.burger'), menu = $('.menu');
  var backdrop = document.createElement('div');
  backdrop.className = 'mega-backdrop'; backdrop.hidden = true;
  backdrop.setAttribute('aria-hidden', 'true');
  if (menu) document.body.appendChild(backdrop);
  var lastMenuTrigger = null;
  function syncBackdrop() {
    var expanded = $$('.drop.open', menu || document).length > 0;
    backdrop.hidden = !(expanded || (menu && menu.classList.contains('open')));
  }
  function closeMega(focusTrigger) {
    $$('.drop.open', menu || document).forEach(function (d) {
      d.classList.remove('open');
      var b = $('button[aria-expanded]', d);
      if (b) b.setAttribute('aria-expanded', 'false');
    });
    if (menu) menu.classList.remove('open');
    if (burger) burger.setAttribute('aria-expanded', 'false');
    syncBackdrop();
    if (focusTrigger && lastMenuTrigger && document.contains(lastMenuTrigger)) lastMenuTrigger.focus();
  }
  if (burger && menu) burger.addEventListener('click', function () {
    var wasOpen = menu.classList.contains('open');
    closeMega(false);
    if (!wasOpen) { menu.classList.add('open'); burger.setAttribute('aria-expanded', 'true'); }
    syncBackdrop();
  });
  $$('.drop > button').forEach(function (b) {
    b.addEventListener('click', function () {
      var drop = b.parentElement, wasOpen = drop.classList.contains('open');
      $$('.drop.open', menu || document).forEach(function (d) {
        d.classList.remove('open');
        var other = $('button[aria-expanded]', d);
        if (other) other.setAttribute('aria-expanded', 'false');
      });
      if (!wasOpen) {
        drop.classList.add('open'); b.setAttribute('aria-expanded', 'true');
        lastMenuTrigger = b;
      }
      syncBackdrop();
    });
  });
  if (menu) {
    menu.addEventListener('click', function (event) {
      if (event.target.closest('a')) closeMega(false);
    });
    backdrop.addEventListener('click', function () { closeMega(false); });
    document.addEventListener('click', function (event) {
      if (!event.target.closest('.top') && !event.target.closest('.mega-backdrop')) closeMega(false);
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && !backdrop.hidden) {
        event.preventDefault();
        closeMega(true);
      }
    });
    window.addEventListener('resize', function () { if (!backdrop.hidden) closeMega(false); });
  }
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
  $$('form[data-form="join"] select[name="language"]').forEach(function (sel) { sel.value = lang === 'ar' ? 'ar' : 'en'; });
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
        ts.render(box, { sitekey: TS_KEY, language: lang, theme: 'auto',
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
      function say(k, ok) { var local = window.ONESPACE_FORM_MESSAGES || {}; status.textContent = local[k] || (lang === 'ar' && msgsAr[k] ? msgsAr[k] : tr('form.' + k, msgs[k])); status.className = 'status ' + (ok === true ? 'ok' : ok === false ? 'err' : '');
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
            this.textContent = tr('founders.invite-copied', lang === 'ar' ? 'تم النسخ' : 'Copied'); track('founders/invite-copied');
          });
        }
        showState('ok');
      }).catch(function () { showState('invalid'); });
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
  var noBar = /\/(ar\/)?(join|confirm|unsubscribe)\.html$/.test(location.pathname);
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
    var l=show?tr('password.hide','Hide key'):tr('password.show','Show key'); b.setAttribute('aria-label',l); b.title=l; inp.focus();
  });
});
).test(entry.date)) return;
      var container = $('.legal');
      if (!container) return;
      var el = $('.legal > p.muted');
      if (!el) {
        el = document.createElement('p');
        container.insertBefore(el, container.firstChild);
      }
      el.className = 'legal-revision';
      var words = {
        en:['Last updated: ','Version '],
        ar:['آخر تحديث: ','الإصدار '],
        es:['Última actualización: ','Versión '],
        fr:['Dernière mise à jour : ','Version '],
        de:['Zuletzt aktualisiert: ','Version ']
      }[lang] || ['Last updated: ','Version '];
      var calendar = new Date(entry.date + 'T12:00:00Z');
      var formatted = new Intl.DateTimeFormat(lang, {day:'numeric', month:'long', year:'numeric', timeZone:'UTC'}).format(calendar);
      var time = document.createElement('time');
      time.dateTime = entry.date;
      time.textContent = formatted;
      el.replaceChildren(document.createTextNode(words[0]), time,
        document.createTextNode(' · ' + words[1] + entry.version));
    }).catch(function () { /* Static legal date remains available without JS/network. */ });
  })();
  function apply() {
    root.lang = lang; root.dir = lang === 'ar' ? 'rtl' : 'ltr';
    $$('[data-i18n]').forEach(function (el) {
      if (!english.has(el)) english.set(el, el.innerHTML);
      var k = el.getAttribute('data-i18n');
      el.innerHTML = lang === 'ar' && AR[k] ? AR[k] : english.get(el);
    });
    $$('[data-i18n-attr]').forEach(function (el) {
      el.getAttribute('data-i18n-attr').split(';').forEach(function (pair) {
        var p = pair.split(':'); var attr = p[0], k = p[1], store = 'data-en-' + attr;
        if (!el.hasAttribute(store)) el.setAttribute(store, el.getAttribute(attr) || '');
        el.setAttribute(attr, lang === 'ar' && AR[k] ? AR[k] : el.getAttribute(store));
      });
    });
    $$('[data-ar-src]').forEach(function (m) {
      var src = m.getAttribute(lang === 'ar' ? 'data-ar-src' : 'data-en-src');
      if (src && m.getAttribute('src') !== src) m.setAttribute('src', src);
      var poster = m.getAttribute(lang === 'ar' ? 'data-ar-poster' : 'data-en-poster');
      if (poster) m.setAttribute('poster', poster);
    });
    var t = document.querySelector('title');
    if (t && t.dataset.ar) { if (!t.dataset.en) t.dataset.en = t.textContent; t.textContent = lang === 'ar' ? t.dataset.ar : t.dataset.en; }
  }
  if (lang === 'ar') apply();
  $$('[data-language-switch]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      var to = link.getAttribute('data-language-switch');
      if (!/^(en|ar|es|fr|de)$/.test(to || '')) return;
      put('os-lang', to); track('lang/' + to);
      var target = new URL(link.href, location.href);
      // Campaign identifiers survive a language switch without adding personal tokens.
      ['utm_source','utm_medium','utm_campaign','utm_content','utm_term','ref'].forEach(function (k) {
        if (params.get(k) && !target.searchParams.has(k)) target.searchParams.set(k, params.get(k).slice(0, 80));
      });
      if (target.href !== link.href) { e.preventDefault(); location.href = target.href; }
    });
  });

  // ---------- Click-to-open full-width mega navigation (mobile: accordion) ----------
  var burger = $('.burger'), menu = $('.menu');
  var backdrop = document.createElement('div');
  backdrop.className = 'mega-backdrop'; backdrop.hidden = true;
  backdrop.setAttribute('aria-hidden', 'true');
  if (menu) document.body.appendChild(backdrop);
  var lastMenuTrigger = null;
  function syncBackdrop() {
    var expanded = $$('.drop.open', menu || document).length > 0;
    backdrop.hidden = !(expanded || (menu && menu.classList.contains('open')));
  }
  function closeMega(focusTrigger) {
    $$('.drop.open', menu || document).forEach(function (d) {
      d.classList.remove('open');
      var b = $('button[aria-expanded]', d);
      if (b) b.setAttribute('aria-expanded', 'false');
    });
    if (menu) menu.classList.remove('open');
    if (burger) burger.setAttribute('aria-expanded', 'false');
    syncBackdrop();
    if (focusTrigger && lastMenuTrigger && document.contains(lastMenuTrigger)) lastMenuTrigger.focus();
  }
  if (burger && menu) burger.addEventListener('click', function () {
    var wasOpen = menu.classList.contains('open');
    closeMega(false);
    if (!wasOpen) { menu.classList.add('open'); burger.setAttribute('aria-expanded', 'true'); }
    syncBackdrop();
  });
  $$('.drop > button').forEach(function (b) {
    b.addEventListener('click', function () {
      var drop = b.parentElement, wasOpen = drop.classList.contains('open');
      $$('.drop.open', menu || document).forEach(function (d) {
        d.classList.remove('open');
        var other = $('button[aria-expanded]', d);
        if (other) other.setAttribute('aria-expanded', 'false');
      });
      if (!wasOpen) {
        drop.classList.add('open'); b.setAttribute('aria-expanded', 'true');
        lastMenuTrigger = b;
      }
      syncBackdrop();
    });
  });
  if (menu) {
    menu.addEventListener('click', function (event) {
      if (event.target.closest('a')) closeMega(false);
    });
    backdrop.addEventListener('click', function () { closeMega(false); });
    document.addEventListener('click', function (event) {
      if (!event.target.closest('.top') && !event.target.closest('.mega-backdrop')) closeMega(false);
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && !backdrop.hidden) {
        event.preventDefault();
        closeMega(true);
      }
    });
    window.addEventListener('resize', function () { if (!backdrop.hidden) closeMega(false); });
  }
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
  $$('form[data-form="join"] select[name="language"]').forEach(function (sel) { sel.value = lang === 'ar' ? 'ar' : 'en'; });
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
        ts.render(box, { sitekey: TS_KEY, language: lang, theme: 'auto',
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
      function say(k, ok) { var local = window.ONESPACE_FORM_MESSAGES || {}; status.textContent = local[k] || (lang === 'ar' && msgsAr[k] ? msgsAr[k] : tr('form.' + k, msgs[k])); status.className = 'status ' + (ok === true ? 'ok' : ok === false ? 'err' : '');
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
            this.textContent = tr('founders.invite-copied', lang === 'ar' ? 'تم النسخ' : 'Copied'); track('founders/invite-copied');
          });
        }
        showState('ok');
      }).catch(function () { showState('invalid'); });
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
  var noBar = /\/(ar\/)?(join|confirm|unsubscribe)\.html$/.test(location.pathname);
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
    var l=show?tr('password.hide','Hide key'):tr('password.show','Show key'); b.setAttribute('aria-label',l); b.title=l; inp.focus();
  });
});
));
    if (!match) return;
    var doc = match[1];
    fetch('/assets/legal-revisions.json', {cache: 'no-cache'}).then(function (r) {
      if (!r.ok) throw Error('revision metadata unavailable');
      return r.json();
    }).then(function (records) {
      var entry = records[doc] && (records[doc][lang] || records[doc].en);
      if (!entry || !/^\\d{4}-\\d{2}-\\d{2}$/.test(entry.date)) return;
      var container = $('.legal');
      if (!container) return;
      var el = $('.legal > p.muted');
      if (!el) {
        el = document.createElement('p');
        container.insertBefore(el, container.firstChild);
      }
      el.className = 'legal-revision';
      var words = {
        en:['Last updated: ','Version '],
        ar:['آخر تحديث: ','الإصدار '],
        es:['Última actualización: ','Versión '],
        fr:['Dernière mise à jour : ','Version '],
        de:['Zuletzt aktualisiert: ','Version ']
      }[lang] || ['Last updated: ','Version '];
      var calendar = new Date(entry.date + 'T12:00:00Z');
      var formatted = new Intl.DateTimeFormat(lang, {day:'numeric', month:'long', year:'numeric', timeZone:'UTC'}).format(calendar);
      var time = document.createElement('time');
      time.dateTime = entry.date;
      time.textContent = formatted;
      el.replaceChildren(document.createTextNode(words[0]), time,
        document.createTextNode(' · ' + words[1] + entry.version));
    }).catch(function () { /* Static legal date remains available without JS/network. */ });
  })();
  function apply() {
    root.lang = lang; root.dir = lang === 'ar' ? 'rtl' : 'ltr';
    $$('[data-i18n]').forEach(function (el) {
      if (!english.has(el)) english.set(el, el.innerHTML);
      var k = el.getAttribute('data-i18n');
      el.innerHTML = lang === 'ar' && AR[k] ? AR[k] : english.get(el);
    });
    $$('[data-i18n-attr]').forEach(function (el) {
      el.getAttribute('data-i18n-attr').split(';').forEach(function (pair) {
        var p = pair.split(':'); var attr = p[0], k = p[1], store = 'data-en-' + attr;
        if (!el.hasAttribute(store)) el.setAttribute(store, el.getAttribute(attr) || '');
        el.setAttribute(attr, lang === 'ar' && AR[k] ? AR[k] : el.getAttribute(store));
      });
    });
    $$('[data-ar-src]').forEach(function (m) {
      var src = m.getAttribute(lang === 'ar' ? 'data-ar-src' : 'data-en-src');
      if (src && m.getAttribute('src') !== src) m.setAttribute('src', src);
      var poster = m.getAttribute(lang === 'ar' ? 'data-ar-poster' : 'data-en-poster');
      if (poster) m.setAttribute('poster', poster);
    });
    var t = document.querySelector('title');
    if (t && t.dataset.ar) { if (!t.dataset.en) t.dataset.en = t.textContent; t.textContent = lang === 'ar' ? t.dataset.ar : t.dataset.en; }
  }
  if (lang === 'ar') apply();
  $$('[data-language-switch]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      var to = link.getAttribute('data-language-switch');
      if (!/^(en|ar|es|fr|de)$/.test(to || '')) return;
      put('os-lang', to); track('lang/' + to);
      var target = new URL(link.href, location.href);
      // Campaign identifiers survive a language switch without adding personal tokens.
      ['utm_source','utm_medium','utm_campaign','utm_content','utm_term','ref'].forEach(function (k) {
        if (params.get(k) && !target.searchParams.has(k)) target.searchParams.set(k, params.get(k).slice(0, 80));
      });
      if (target.href !== link.href) { e.preventDefault(); location.href = target.href; }
    });
  });

  // ---------- Click-to-open full-width mega navigation (mobile: accordion) ----------
  var burger = $('.burger'), menu = $('.menu');
  var backdrop = document.createElement('div');
  backdrop.className = 'mega-backdrop'; backdrop.hidden = true;
  backdrop.setAttribute('aria-hidden', 'true');
  if (menu) document.body.appendChild(backdrop);
  var lastMenuTrigger = null;
  function syncBackdrop() {
    var expanded = $$('.drop.open', menu || document).length > 0;
    backdrop.hidden = !(expanded || (menu && menu.classList.contains('open')));
  }
  function closeMega(focusTrigger) {
    $$('.drop.open', menu || document).forEach(function (d) {
      d.classList.remove('open');
      var b = $('button[aria-expanded]', d);
      if (b) b.setAttribute('aria-expanded', 'false');
    });
    if (menu) menu.classList.remove('open');
    if (burger) burger.setAttribute('aria-expanded', 'false');
    syncBackdrop();
    if (focusTrigger && lastMenuTrigger && document.contains(lastMenuTrigger)) lastMenuTrigger.focus();
  }
  if (burger && menu) burger.addEventListener('click', function () {
    var wasOpen = menu.classList.contains('open');
    closeMega(false);
    if (!wasOpen) { menu.classList.add('open'); burger.setAttribute('aria-expanded', 'true'); }
    syncBackdrop();
  });
  $$('.drop > button').forEach(function (b) {
    b.addEventListener('click', function () {
      var drop = b.parentElement, wasOpen = drop.classList.contains('open');
      $$('.drop.open', menu || document).forEach(function (d) {
        d.classList.remove('open');
        var other = $('button[aria-expanded]', d);
        if (other) other.setAttribute('aria-expanded', 'false');
      });
      if (!wasOpen) {
        drop.classList.add('open'); b.setAttribute('aria-expanded', 'true');
        lastMenuTrigger = b;
      }
      syncBackdrop();
    });
  });
  if (menu) {
    menu.addEventListener('click', function (event) {
      if (event.target.closest('a')) closeMega(false);
    });
    backdrop.addEventListener('click', function () { closeMega(false); });
    document.addEventListener('click', function (event) {
      if (!event.target.closest('.top') && !event.target.closest('.mega-backdrop')) closeMega(false);
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && !backdrop.hidden) {
        event.preventDefault();
        closeMega(true);
      }
    });
    window.addEventListener('resize', function () { if (!backdrop.hidden) closeMega(false); });
  }
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
  $$('form[data-form="join"] select[name="language"]').forEach(function (sel) { sel.value = lang === 'ar' ? 'ar' : 'en'; });
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
        ts.render(box, { sitekey: TS_KEY, language: lang, theme: 'auto',
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
      function say(k, ok) { var local = window.ONESPACE_FORM_MESSAGES || {}; status.textContent = local[k] || (lang === 'ar' && msgsAr[k] ? msgsAr[k] : tr('form.' + k, msgs[k])); status.className = 'status ' + (ok === true ? 'ok' : ok === false ? 'err' : '');
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
            this.textContent = tr('founders.invite-copied', lang === 'ar' ? 'تم النسخ' : 'Copied'); track('founders/invite-copied');
          });
        }
        showState('ok');
      }).catch(function () { showState('invalid'); });
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
  var noBar = /\/(ar\/)?(join|confirm|unsubscribe)\.html$/.test(location.pathname);
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
    var l=show?tr('password.hide','Hide key'):tr('password.show','Show key'); b.setAttribute('aria-label',l); b.title=l; inp.focus();
  });
});
