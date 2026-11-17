-- OneSpace website: Founder dashboard KPIs per period (website only; does not touch the app).
-- Adds a `period` block (this period and the one before it, same length) and couple-completeness numbers,
-- so rates are never computed from all-time counts against period visitors.
create or replace function public.founder_stats(p_days int default 30)
returns jsonb language sql security definer set search_path = '' as $$
  with m as (select * from private.founder_members),
       c as (select * from private.founder_couples),
       d as (select greatest(1, least(p_days, 180)) n),
       cur as (select now() - make_interval(days => (select n from d)) a, now() b),
       prev as (select now() - make_interval(days => 2 * (select n from d)) a, now() - make_interval(days => (select n from d)) b),
       cm as (select couple_id, count(*) filter (where confirmed_at is not null) k, min(confirmed_at) first_conf from m group by 1)
  select jsonb_build_object(
    'generated_at', now(),
    'days', (select n from d),
    'capacity_couples', 250,
    'founder_couples', (select count(*) from c where status = 'founder'),
    'waitlist_couples', (select count(*) from c where status = 'waitlist'),
    'couples_complete', (select count(*) from cm join c on c.id = cm.couple_id where cm.k >= 2 and c.status = 'founder'),
    'couples_waiting_partner', (select count(*) from cm join c on c.id = cm.couple_id where cm.k = 1 and c.status = 'founder'),
    'signups_total', (select count(*) from m),
    'confirmed', (select count(*) from m where confirmed_at is not null),
    'pending', (select count(*) from m where confirmed_at is null),
    'pending_stale', (select count(*) from m where confirmed_at is null and unsubscribed_at is null and created_at < now() - interval '24 hours'),
    'partners_joined', (select count(*) from m where role = 'partner' and confirmed_at is not null),
    'confirm_rate', (select case when count(*) = 0 then null else round(100.0 * count(*) filter (where confirmed_at is not null) / count(*), 1) end from m),
    'period', jsonb_build_object(
      'signups', (select count(*) from m, cur where m.created_at >= cur.a),
      'confirmed', (select count(*) from m, cur where m.confirmed_at >= cur.a),
      'new_founder_couples', (select count(*) from cm join c on c.id = cm.couple_id, cur where c.status = 'founder' and cm.first_conf >= cur.a),
      'prev_signups', (select count(*) from m, prev where m.created_at >= prev.a and m.created_at < prev.b),
      'prev_confirmed', (select count(*) from m, prev where m.confirmed_at >= prev.a and m.confirmed_at < prev.b),
      'prev_new_founder_couples', (select count(*) from cm join c on c.id = cm.couple_id, prev where c.status = 'founder' and cm.first_conf >= prev.a and cm.first_conf < prev.b)),
    'platform', (select coalesce(jsonb_object_agg(platform, n), '{}'::jsonb) from (select platform, count(*) n from m where confirmed_at is not null group by 1) x),
    'platform_all', (select coalesce(jsonb_object_agg(platform, n), '{}'::jsonb) from (select platform, count(*) n from m group by 1) x),
    'living', (select coalesce(jsonb_object_agg(coalesce(nullif(living, ''), 'unknown'), n), '{}'::jsonb) from (select living, count(*) n from m where confirmed_at is not null group by 1) x),
    'language', (select coalesce(jsonb_object_agg(language, n), '{}'::jsonb) from (select language, count(*) n from m group by 1) x),
    'sources', (select coalesce(jsonb_agg(jsonb_build_object('source', s, 'n', n) order by n desc), '[]'::jsonb) from
                 (select coalesce(nullif(utm->>'utm_source', ''), nullif(split_part(referrer, '/', 3), ''), nullif(source, ''), 'direct') s, count(*) n
                  from m group by 1 order by 2 desc limit 12) x),
    'landing', (select coalesce(jsonb_agg(jsonb_build_object('page', pg, 'n', n) order by n desc), '[]'::jsonb) from
                 (select coalesce(nullif(landing, ''), '/') pg, count(*) n from m group by 1 order by 2 desc limit 12) x),
    'daily', (select coalesce(jsonb_agg(jsonb_build_object('day', dd, 'signups', s, 'confirmed', cf) order by dd), '[]'::jsonb) from
               (select g::date dd,
                  (select count(*) from m where created_at::date = g::date) s,
                  (select count(*) from m where confirmed_at::date = g::date) cf
                from generate_series(current_date - ((select n from d) - 1), current_date, interval '1 day') g) x),
    'emails', (select coalesce(jsonb_object_agg(k, n), '{}'::jsonb) from (select kind || ':' || status k, count(*) n from private.founder_email_log group by 1) x),
    'email_failures', (select coalesce(jsonb_agg(jsonb_build_object('at', created_at, 'kind', kind, 'error', error) order by created_at desc), '[]'::jsonb)
                       from (select * from private.founder_email_log where status <> 'sent' order by created_at desc limit 20) f)
  );
$$;
revoke all on function public.founder_stats(int) from public, anon, authenticated;
grant execute on function public.founder_stats(int) to service_role;
