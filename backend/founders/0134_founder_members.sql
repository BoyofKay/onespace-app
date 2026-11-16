-- 0134: Founder Members waitlist (website). One Founder number per COUPLE:
-- the first 250 confirmed couples (= 500 people) become Founder Members.
-- A sign-up counts as a couple of two even before the partner joins; a partner
-- joins the same couple through the invite link. Tables are private; only the
-- service role (website edge functions) can call the functions.

create table if not exists private.founder_couples (
  id uuid primary key default gen_random_uuid(),
  founder_number int unique,                       -- 1..250, given on the first confirmation
  status text not null default 'founder' check (status in ('founder', 'waitlist')),
  invite_code text not null unique,
  created_at timestamptz not null default now()
);

create table if not exists private.founder_members (
  id uuid primary key default gen_random_uuid(),
  couple_id uuid references private.founder_couples(id) on delete set null,
  role text not null default 'first' check (role in ('first', 'partner')),
  email text not null check (length(email) <= 254),
  email_norm text not null unique,
  name text not null default '' check (length(name) <= 80),
  platform text not null default 'unsure' check (platform in ('android', 'iphone', 'both', 'unsure')),
  living text not null default '' check (living in ('', 'together', 'apart', 'both', 'soon')),
  language text not null default 'en' check (language in ('en', 'ar')),
  source text not null default '' check (length(source) <= 80),
  landing text not null default '' check (length(landing) <= 200),
  referrer text not null default '' check (length(referrer) <= 200),
  utm jsonb not null default '{}'::jsonb,
  consent_launch boolean not null,
  consent_at timestamptz,
  invite_code_used text,
  token_hash text,
  token_expires_at timestamptz,
  confirmed_at timestamptz,
  ip_hash text not null default '',
  unsubscribed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists founder_members_couple on private.founder_members(couple_id);
create index if not exists founder_members_created on private.founder_members(created_at);
create index if not exists founder_members_token on private.founder_members(token_hash);

create table if not exists private.founder_email_log (
  id bigint generated always as identity primary key,
  member_id uuid references private.founder_members(id) on delete cascade,
  kind text not null,          -- confirm | already | welcome | partner_joined
  status text not null,        -- sent | failed | skipped
  provider_id text,
  error text,
  created_at timestamptz not null default now()
);
create index if not exists founder_email_log_member on private.founder_email_log(member_id, created_at);

create table if not exists private.founder_attempts (
  id bigint generated always as identity primary key,
  email_norm text not null,
  ip_hash text not null,
  created_at timestamptz not null default now()
);
create index if not exists founder_attempts_time on private.founder_attempts(created_at);

alter table private.founder_couples enable row level security;
alter table private.founder_members enable row level security;
alter table private.founder_email_log enable row level security;
alter table private.founder_attempts enable row level security;

-- ---------------------------------------------------------------- join
create or replace function public.founder_join(p jsonb)
returns jsonb language plpgsql security definer set search_path to '' as $$
declare
  v_email text := btrim(coalesce(p->>'email', ''));
  v_norm text := lower(v_email);
  v_ip text := left(coalesce(p->>'ip_hash', ''), 64);
  v_invite text := nullif(btrim(coalesce(p->>'invite', '')), '');
  v_platform text := case when p->>'platform' in ('android', 'iphone', 'both') then p->>'platform' else 'unsure' end;
  v_living text := case when p->>'living' in ('together', 'apart', 'soon') then p->>'living' else '' end;
  v_lang text := case when p->>'language' = 'ar' then 'ar' else 'en' end;
  m private.founder_members;
  c private.founder_couples;
  v_token text := encode(extensions.gen_random_bytes(24), 'hex');
  v_exists boolean;
begin
  if v_email !~ '^[^@\s]+@[^@\s]+\.[^@\s]{2,}$' or length(v_email) > 254 then
    return jsonb_build_object('status', 'invalid_email');
  end if;
  if coalesce((p->>'consent')::boolean, false) is not true then
    return jsonb_build_object('status', 'consent_required');
  end if;
  -- Rate limits: per email, per network, and for the whole site.
  if (select count(*) from private.founder_attempts where email_norm = v_norm and created_at > now() - interval '1 hour') >= 3
     or (v_ip <> '' and (select count(*) from private.founder_attempts where ip_hash = v_ip and created_at > now() - interval '1 hour') >= 8)
     or (select count(*) from private.founder_attempts where created_at > now() - interval '1 hour') >= 300 then
    return jsonb_build_object('status', 'rate_limited');
  end if;
  insert into private.founder_attempts(email_norm, ip_hash) values (v_norm, v_ip);
  delete from private.founder_attempts where created_at < now() - interval '2 days';

  select * into m from private.founder_members where email_norm = v_norm;
  v_exists := found;
  if v_exists and m.confirmed_at is not null then
    select * into c from private.founder_couples where id = m.couple_id;
    return jsonb_build_object('status', 'already', 'member_id', m.id, 'email', m.email, 'name', m.name, 'language', m.language,
      'founder_number', c.founder_number, 'couple_status', c.status, 'invite_code', c.invite_code, 'role', m.role);
  end if;
  if v_invite is not null and not exists (select 1 from private.founder_couples where invite_code = v_invite) then
    v_invite := null;
  end if;
  if v_exists then
    update private.founder_members set
      name = left(btrim(coalesce(p->>'name', name)), 80), platform = v_platform, living = v_living, language = v_lang,
      invite_code_used = coalesce(v_invite, invite_code_used), consent_launch = true, consent_at = now(),
      token_hash = encode(extensions.digest(v_token, 'sha256'), 'hex'), token_expires_at = now() + interval '7 days', updated_at = now()
    where id = m.id returning * into m;
  else
    insert into private.founder_members(email, email_norm, name, platform, living, language, source, landing, referrer, utm,
      consent_launch, consent_at, invite_code_used, token_hash, token_expires_at, ip_hash)
    values (v_email, v_norm, left(btrim(coalesce(p->>'name', '')), 80), v_platform, v_living, v_lang,
      left(coalesce(p->>'source', ''), 80), left(coalesce(p->>'landing', ''), 200), left(coalesce(p->>'referrer', ''), 200),
      coalesce(p->'utm', '{}'::jsonb), true, now(), v_invite, encode(extensions.digest(v_token, 'sha256'), 'hex'),
      now() + interval '7 days', v_ip)
    returning * into m;
  end if;
  return jsonb_build_object('status', 'pending', 'member_id', m.id, 'email', m.email, 'name', m.name, 'language', m.language,
    'token', v_token, 'partner_invite', v_invite is not null);
end $$;

-- ---------------------------------------------------------------- confirm
create or replace function public.founder_confirm(p_token text)
returns jsonb language plpgsql security definer set search_path to '' as $$
declare
  m private.founder_members;
  c private.founder_couples;
  first_m private.founder_members;
  v_new boolean := false;
  v_num int;
  v_partner_joined boolean := false;
begin
  if coalesce(p_token, '') !~ '^[0-9a-f]{48}$' then return jsonb_build_object('status', 'invalid'); end if;
  select * into m from private.founder_members where token_hash = encode(extensions.digest(p_token, 'sha256'), 'hex');
  if not found then return jsonb_build_object('status', 'invalid'); end if;
  if m.confirmed_at is null then
    if m.token_expires_at < now() then return jsonb_build_object('status', 'expired', 'language', m.language); end if;
    perform pg_advisory_xact_lock(hashtext('onespace_founder_number'));
    -- A partner joins the couple behind the invite, if that couple has room.
    if m.invite_code_used is not null then
      select * into c from private.founder_couples where invite_code = m.invite_code_used;
      if found and (select count(*) from private.founder_members where couple_id = c.id and confirmed_at is not null) < 2 then
        update private.founder_members set couple_id = c.id, role = 'partner', confirmed_at = now(), updated_at = now()
          where id = m.id returning * into m;
        v_partner_joined := true;
      else
        c := null;
      end if;
    end if;
    if m.confirmed_at is null then
      select coalesce(max(founder_number), 0) into v_num from private.founder_couples;
      insert into private.founder_couples(founder_number, status, invite_code)
        values (case when v_num < 250 then v_num + 1 end, case when v_num < 250 then 'founder' else 'waitlist' end,
                encode(extensions.gen_random_bytes(6), 'hex'))
        returning * into c;
      update private.founder_members set couple_id = c.id, role = 'first', confirmed_at = now(), updated_at = now()
        where id = m.id returning * into m;
    end if;
    v_new := true;
  else
    select * into c from private.founder_couples where id = m.couple_id;
  end if;
  if v_partner_joined then
    select * into first_m from private.founder_members where couple_id = c.id and role = 'first' and confirmed_at is not null limit 1;
  end if;
  return jsonb_build_object('status', case when v_new then 'confirmed' else 'already' end,
    'member_id', m.id, 'email', m.email, 'name', m.name, 'language', m.language, 'role', m.role,
    'founder_number', c.founder_number, 'couple_status', c.status, 'invite_code', c.invite_code,
    'couple_full', (select count(*) from private.founder_members where couple_id = c.id and confirmed_at is not null) >= 2,
    'partner_joined', v_partner_joined,
    'first_member', case when first_m.id is null then null else jsonb_build_object('member_id', first_m.id, 'email', first_m.email,
       'name', first_m.name, 'language', first_m.language) end,
    'platform', m.platform);
end $$;

-- ---------------------------------------------------------------- email log + resend list
create or replace function public.founder_log_email(p_member uuid, p_kind text, p_status text, p_provider_id text, p_error text)
returns void language sql security definer set search_path to '' as $$
  insert into private.founder_email_log(member_id, kind, status, provider_id, error)
  values (p_member, left(p_kind, 40), left(p_status, 20), left(p_provider_id, 120), left(p_error, 500));
$$;

-- Pending members whose confirmation email never went out (e.g. before the mail key existed): new token each.
create or replace function public.founder_pending_to_resend(p_limit int default 50)
returns jsonb language plpgsql security definer set search_path to '' as $$
declare r record; out jsonb := '[]'::jsonb; t text;
begin
  for r in select m.* from private.founder_members m
           where m.confirmed_at is null and m.unsubscribed_at is null
             and not exists (select 1 from private.founder_email_log l where l.member_id = m.id and l.kind = 'confirm' and l.status = 'sent')
           order by m.created_at limit greatest(1, least(p_limit, 200)) loop
    t := encode(extensions.gen_random_bytes(24), 'hex');
    update private.founder_members set token_hash = encode(extensions.digest(t, 'sha256'), 'hex'), token_expires_at = now() + interval '7 days'
      where id = r.id;
    out := out || jsonb_build_object('member_id', r.id, 'email', r.email, 'name', r.name, 'language', r.language, 'token', t);
  end loop;
  return out;
end $$;

-- ---------------------------------------------------------------- stats (aggregates only, no emails)
create or replace function public.founder_stats(p_days int default 30)
returns jsonb language sql security definer set search_path to '' as $$
  with m as (select * from private.founder_members),
       c as (select * from private.founder_couples)
  select jsonb_build_object(
    'generated_at', now(),
    'capacity_couples', 250,
    'founder_couples', (select count(*) from c where status = 'founder'),
    'waitlist_couples', (select count(*) from c where status = 'waitlist'),
    'founder_people', (select count(*) from c where status = 'founder') * 2,
    'signups_total', (select count(*) from m),
    'confirmed', (select count(*) from m where confirmed_at is not null),
    'pending', (select count(*) from m where confirmed_at is null),
    'partners_joined', (select count(*) from m where role = 'partner' and confirmed_at is not null),
    'couples_complete', (select count(*) from c where (select count(*) from m where m.couple_id = c.id and m.confirmed_at is not null) >= 2),
    'confirm_rate', (select case when count(*) = 0 then null else round(100.0 * count(*) filter (where confirmed_at is not null) / count(*), 1) end from m),
    'platform', (select coalesce(jsonb_object_agg(platform, n), '{}'::jsonb) from (select platform, count(*) n from m where confirmed_at is not null group by 1) x),
    'platform_all', (select coalesce(jsonb_object_agg(platform, n), '{}'::jsonb) from (select platform, count(*) n from m group by 1) x),
    'living', (select coalesce(jsonb_object_agg(coalesce(nullif(living, ''), 'unknown'), n), '{}'::jsonb) from (select living, count(*) n from m where confirmed_at is not null group by 1) x),
    'language', (select coalesce(jsonb_object_agg(language, n), '{}'::jsonb) from (select language, count(*) n from m group by 1) x),
    'sources', (select coalesce(jsonb_agg(jsonb_build_object('source', s, 'n', n) order by n desc), '[]'::jsonb) from
                 (select coalesce(nullif(utm->>'utm_source', ''), nullif(split_part(referrer, '/', 3), ''), nullif(source, ''), 'direct') s, count(*) n
                  from m group by 1 order by 2 desc limit 12) x),
    'landing', (select coalesce(jsonb_agg(jsonb_build_object('page', pg, 'n', n) order by n desc), '[]'::jsonb) from
                 (select coalesce(nullif(landing, ''), '/') pg, count(*) n from m group by 1 order by 2 desc limit 12) x),
    'daily', (select coalesce(jsonb_agg(jsonb_build_object('day', d, 'signups', s, 'confirmed', cf) order by d), '[]'::jsonb) from
               (select g::date d,
                  (select count(*) from m where created_at::date = g::date) s,
                  (select count(*) from m where confirmed_at::date = g::date) cf
                from generate_series(current_date - (greatest(1, least(p_days, 180)) - 1), current_date, interval '1 day') g) x),
    'emails', (select coalesce(jsonb_object_agg(k, n), '{}'::jsonb) from (select kind || ':' || status k, count(*) n from private.founder_email_log group by 1) x)
  );
$$;

revoke all on function public.founder_join(jsonb) from public, anon, authenticated;
revoke all on function public.founder_confirm(text) from public, anon, authenticated;
revoke all on function public.founder_log_email(uuid, text, text, text, text) from public, anon, authenticated;
revoke all on function public.founder_pending_to_resend(int) from public, anon, authenticated;
revoke all on function public.founder_stats(int) from public, anon, authenticated;
grant execute on function public.founder_join(jsonb), public.founder_confirm(text), public.founder_log_email(uuid, text, text, text, text),
  public.founder_pending_to_resend(int), public.founder_stats(int) to service_role;

-- Applied the same day: free-text note from the form, 'both' living option,
-- no repeated confirmation emails (10 minutes / 3 a day) and the 'already' reminder at most daily —
-- see the live definitions of founder_join / founder_stats in the database.
alter table private.founder_members add column if not exists note text not null default '' check (length(note) <= 1500);
