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
      const get = async (path: string) => {
        const r = await fetch(`https://onespace.goatcounter.com/api/v0/${path}${path.includes('?') ? '&' : '?'}start=${start}&end=${end}`,
          { headers: { Authorization: `Bearer ${gc}`, 'Content-Type': 'application/json' } });
        // GoatCounter answers 404 when a list has no rows yet (e.g. no referrers): treat that as empty.
        if (r.status === 404) return {};
        if (!r.ok) throw new Error(`goatcounter ${path.split('?')[0]}: ${r.status}`);
        return r.json();
      };
      // One failing source never hides the others.
      const safe = (path: string) => get(path).catch((e) => { (stats.traffic_warnings ??= []).push(String(e).slice(0, 120)); return {}; });
      const n = (x: any) => Number(x?.count ?? x?.count_unique ?? 0);
      try {
        const [total, hits, refs, locs] = await Promise.all([get('stats/total'), safe('stats/hits?limit=100'), safe('stats/toprefs?limit=10'), safe('stats/locations?limit=8')]);
        // `total` counts visitors including events; events are clicks, not people.
        stats.visitors = Math.max(0, Number(total.total ?? 0) - Number(total.total_events ?? 0));
        const all: any[] = hits.hits ?? [];
        stats.top_pages = all.filter((h) => !h.event).slice(0, 10).map((h) => ({ page: h.path, n: n(h) }));
        const ev: Record<string, number> = {};
        for (const h of all.filter((h) => h.event)) ev[h.path] = (ev[h.path] ?? 0) + n(h);
        const sum = (re: RegExp) => Object.entries(ev).filter(([k]) => re.test(k)).reduce((s, [, v]) => s + v, 0);
        stats.funnel = [
          { step: 'Visitors', n: stats.visitors },
          { step: 'Clicked Join', n: sum(/^cta\/(join|hero_join|sticky_join)/) },
          { step: 'Started the form', n: sum(/^founders\/form-start/) },
          { step: 'Sent the form', n: sum(/^founders\/sent$/) },
          { step: 'Confirmed email', n: sum(/^founders\/confirmed$/) },
        ];
        stats.demo = { tour_finished: sum(/^demo\/tour-finished/), demo_clicks: sum(/^cta\/demo|^cta\/hero_demo/), theme_picks: sum(/^theme\//) };
        stats.top_events = Object.entries(ev).sort((a, b) => b[1] - a[1]).slice(0, 12).map(([k, v]) => ({ event: k, n: v }));
        stats.referrers = (refs.stats ?? []).slice(0, 10).map((r: any) => ({ source: r.name || '(direct)', n: n(r) }));
        stats.countries = (locs.stats ?? []).slice(0, 8).map((r: any) => ({ source: r.name || r.id || '?', n: n(r) }));
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
