-- OneSpace website: spam-protection counters (website only; does not touch the app).
-- Counts what the form spam checks did, per day — numbers only, never an email, name or address.
--   form:   'join' (Founder form) or 'contact' (Support / Delete-account forms)
--   result: 'honeypot'    hidden robot field filled → silently dropped
--           'checked'     sent too fast → asked for the Cloudflare Turnstile check
--           'passed'      Turnstile check passed → accepted
--           'blocked'     Turnstile check failed → refused (the visitor sees a message)
--           'unavailable' the check could not load in the visitor's browser → accepted
--           'unverified'  Cloudflare could not be reached / secret missing → accepted
create table if not exists private.founder_spam_counts (
  day date not null default current_date,
  form text not null check (form in ('join', 'contact')),
  result text not null check (result in ('honeypot', 'checked', 'passed', 'blocked', 'unavailable', 'unverified')),
  n int not null default 0,
  primary key (day, form, result)
);
alter table private.founder_spam_counts enable row level security;

create or replace function public.founder_spam_count(p_form text, p_result text)
returns void language sql security definer set search_path = '' as $$
  insert into private.founder_spam_counts (day, form, result, n) values (current_date, p_form, p_result, 1)
  on conflict (day, form, result) do update set n = private.founder_spam_counts.n + 1;
$$;

create or replace function public.founder_spam_stats(p_days int default 30)
returns jsonb language sql security definer set search_path = '' as $$
  select coalesce(jsonb_object_agg(result, n), '{}'::jsonb) from (
    select result, sum(n)::int n from private.founder_spam_counts
    where day > current_date - greatest(1, least(p_days, 180)) group by result) t;
$$;

revoke all on function public.founder_spam_count(text, text) from public, anon, authenticated;
revoke all on function public.founder_spam_stats(int) from public, anon, authenticated;
grant execute on function public.founder_spam_count(text, text) to service_role;
grant execute on function public.founder_spam_stats(int) to service_role;
