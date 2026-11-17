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
  // Trim both sides: a pasted secret often carries a trailing space or newline. Any length is accepted.
  const want = (Deno.env.get('FOUNDER_ADMIN_KEY') ?? '').trim();
  if (!want) return json(req, { ok: false, error: 'key_not_set' }, 503);
  if (!(await same((req.headers.get('x-admin-key') ?? '').trim(), want))) {
    await new Promise((r) => setTimeout(r, 600));
    return json(req, { ok: false, error: 'unauthorized' }, 401);
  }
  try {
    if (req.method === 'POST') {
      const b = await req.json().catch(() => ({}));
      if (b.action === 'resend_pending') {
        const list: any[] = await rpc('founder_pending_to_resend', { p_limit: 50 });
        let sent = 0;
        for (const m of list) if (await send(m.member_id, 'confirm', m.email, mailConfirm(m.language, m.name, m.token, false), m.unsub)) sent++;
        return json(req, { ok: true, attempted: list.length, sent });
      }
      return json(req, { ok: false, error: 'unknown_action' }, 400);
    }
    const days = Math.max(7, Math.min(180, Number(new URL(req.url).searchParams.get('days') ?? 30)));
    const stats = await rpc('founder_stats', { p_days: days });
    stats.mail_key_set = Boolean(Deno.env.get('RESEND_API_KEY'));
    // Website traffic from GoatCounter (needs GOATCOUNTER_TOKEN, a read-only API key). Never fails the dashboard.
    const gc = Deno.env.get('GOATCOUNTER_TOKEN');
    stats.traffic_connected = Boolean(gc);
    if (gc) {
      // GoatCounter wants full RFC 3339 times, rounded to the hour.
      const start = new Date(Date.now() - days * 864e5).toISOString().slice(0, 10) + 'T00:00:00Z';
      const end = new Date(Date.now() + 36e5).toISOString().slice(0, 13) + ':00:00Z';
      const prevStart = new Date(Date.now() - 2 * days * 864e5).toISOString().slice(0, 10) + 'T00:00:00Z';
      const get = async (path: string, a = start, b = end) => {
        const r = await fetch(`https://onespace.goatcounter.com/api/v0/${path}${path.includes('?') ? '&' : '?'}start=${a}&end=${b}`,
          { headers: { Authorization: `Bearer ${gc}`, 'Content-Type': 'application/json' } });
        // GoatCounter answers 404 when a list has no rows yet (e.g. no referrers): treat that as empty.
        if (r.status === 404) return {};
        if (!r.ok) throw new Error(`goatcounter ${path.split('?')[0]}: ${r.status}`);
        return r.json();
      };
      // One failing source never hides the others.
      const safe = (path: string, a = start, b = end) => get(path, a, b).catch((e) => { (stats.traffic_warnings ??= []).push(String(e).slice(0, 120)); return {}; });
      const n = (x: any) => Number(x?.count ?? x?.count_unique ?? 0);
      try {
        const [total, hits, refs, locs, prevTotal, sizes, systems, langs, camps] = await Promise.all([get('stats/total'), safe('stats/hits?limit=100'),
          safe('stats/toprefs?limit=10'), safe('stats/locations?limit=100'), safe('stats/total', prevStart, start), safe('stats/sizes?limit=10'),
          safe('stats/systems?limit=8'), safe('stats/languages?limit=8'), safe('stats/campaigns?limit=10')]);
        // GoatCounter counts unique visitors (no cookies). `total` includes events; events are clicks, not people.
        stats.visitors = Math.max(0, Number(total.total ?? 0) - Number(total.total_events ?? 0));
        stats.prev_visitors = prevTotal.total == null ? null : Math.max(0, Number(prevTotal.total) - Number(prevTotal.total_events ?? 0));
        stats.visitors_daily = (total.stats ?? []).map((d: any) => ({ day: String(d.day).slice(0, 10), n: Number(d.daily ?? 0) }));
        const all: any[] = hits.hits ?? [];
        const pages = all.filter((h) => !h.event);
        stats.top_pages = pages.slice(0, 10).map((h) => ({ page: h.path, n: n(h) }));
        const pageViews = pages.reduce((a, h) => a + n(h), 0);
        stats.pages_per_visitor = stats.visitors ? Math.round(10 * pageViews / stats.visitors) / 10 : null;
        const arViews = pages.filter((h) => /^\/ar(\/|$)/.test(h.path)).reduce((a, h) => a + n(h), 0);
        stats.arabic_share = pageViews ? Math.round(100 * arViews / pageViews) : null;
        const ev: Record<string, number> = {};
        for (const h of all.filter((h) => h.event)) ev[h.path] = (ev[h.path] ?? 0) + n(h);
        const sum = (re: RegExp) => Object.entries(ev).filter(([k]) => re.test(k)).reduce((s, [, v]) => s + v, 0);
        // Time on page: one bucket per page visit, sent by the site when the visitor leaves (only visible time counts).
        const order = ['0-10s', '10-30s', '30-60s', '1-3m', '3-10m', '10m-plus'];
        const time = order.map((b) => ({ bucket: b, n: ev[`time/${b}`] ?? 0 }));
        const tTot = time.reduce((a, t) => a + t.n, 0);
        let acc = 0, median: string | null = null;
        for (const t of time) { acc += t.n; if (!median && tTot && acc >= tTot / 2) median = t.bucket; }
        stats.time = { buckets: time, measured: tTot, median, engaged_share: tTot ? Math.round(100 * time.slice(2).reduce((a, t) => a + t.n, 0) / tTot) : null,
          quick_exit_share: tTot ? Math.round(100 * time[0].n / tTot) : null };
        stats.read_to_end = sum(/^read\/end/);
        stats.funnel = [
          { step: 'Visitors', n: stats.visitors },
          { step: 'Clicked Join', n: sum(/^cta\/(join|hero_join|sticky_join)/) },
          { step: 'Started the form', n: sum(/^founders\/form-start/) },
          { step: 'Sent the form', n: sum(/^founders\/sent$/) },
          { step: 'Confirmed email', n: sum(/^founders\/confirmed$/) },
        ];
        stats.demo = { tour_finished: sum(/^demo\/tour-finished/), demo_clicks: sum(/^cta\/demo|^cta\/hero_demo/), theme_picks: sum(/^theme\//),
          outbound_store: sum(/^outbound\/(play\.google\.com|apps\.apple\.com)/), lang_switch: sum(/^lang\//) };
        stats.top_events = Object.entries(ev).filter(([k]) => !/^(time|read)\//.test(k)).sort((a, b) => b[1] - a[1]).slice(0, 12).map(([k, v]) => ({ event: k, n: v }));
        stats.referrers = (refs.stats ?? []).slice(0, 10).map((r: any) => ({ source: r.name || '(direct)', n: n(r) }));
        const countries = (locs.stats ?? []).map((r: any) => ({ source: r.name || r.id || '?', n: n(r) }));
        stats.countries = countries.slice(0, 10);
        stats.country_count = countries.filter((c: any) => c.n > 0 && c.source !== '(unknown)').length;
        // Screen sizes → phone / tablet / computer.
        const dev: Record<string, number> = {};
        for (const r of sizes.stats ?? []) {
          const id = String(r.id || r.name || '').toLowerCase();
          const k = /phone/.test(id) ? 'Phone' : /tablet/.test(id) ? 'Tablet' : /desktop|monitor|computer|laptop/.test(id) ? 'Computer' : 'Unknown';
          dev[k] = (dev[k] ?? 0) + n(r);
        }
        stats.devices = dev;
        stats.systems = (systems.stats ?? []).map((r: any) => ({ source: r.name || '?', n: n(r) }));
        stats.languages = (langs.stats ?? []).map((r: any) => ({ source: r.name || '?', n: n(r) }));
        stats.campaigns = (camps.stats ?? []).map((r: any) => ({ source: r.name || '?', n: n(r) }));
      } catch (e) {
        stats.traffic_error = String(e).slice(0, 160);
      }
    }
    return json(req, { ok: true, stats });
  } catch (e) {
    console.error(e);
    return json(req, { ok: false, error: 'server' }, 500);
  }
});
