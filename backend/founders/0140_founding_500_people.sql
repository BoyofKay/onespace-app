-- Founding 500 = the first 500 PEOPLE who confirm their email, on their own or as a couple (Amr, 22 Nov 2026).
-- * Founder numbers are never shown or sent. founder_couples.founder_number stays as an internal sequence only;
--   the real order of people is members.confirmed_at.
-- * A partner who confirms through a Founder's invitation is a Founder Member too.
-- * The sign-up form gains "On my own" (living = 'solo').
-- Applied to Production (letcgxbnblohhfyeuigz) on 22 Nov 2026 with Amr's approval.

create or replace function public.founder_confirm(p_token text)
 returns jsonb
 language plpgsql
 security definer
 set search_path to ''
as $function$
declare
  m private.founder_members;
  c private.founder_couples;
  first_m private.founder_members;
  v_new boolean := false;
  v_num int;
  v_people int;
  v_partner_joined boolean := false;
begin
  if coalesce(p_token, '') !~ '^[0-9a-f]{48}$' then return jsonb_build_object('status', 'invalid'); end if;
  select * into m from private.founder_members where token_hash = encode(extensions.digest(p_token, 'sha256'), 'hex');
  if not found then return jsonb_build_object('status', 'invalid'); end if;
  if m.confirmed_at is null then
    if m.token_expires_at < now() then return jsonb_build_object('status', 'expired', 'language', m.language); end if;
    perform pg_advisory_xact_lock(hashtext('onespace_founder_number'));
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
      -- Founder status: fewer than 500 people have confirmed before this person.
      select count(*) into v_people from private.founder_members where confirmed_at is not null;
      select coalesce(max(founder_number), 0) into v_num from private.founder_couples;
      insert into private.founder_couples(founder_number, status, invite_code)
        values (case when v_people < 500 then v_num + 1 end, case when v_people < 500 then 'founder' else 'waitlist' end,
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
    'member_id', m.id, 'email', m.email, 'name', m.name, 'language', m.language, 'role', m.role, 'unsub', m.unsub_token,
    'founder_number', c.founder_number,  -- internal only; never shown or emailed
    'couple_status', c.status, 'invite_code', c.invite_code,
    'couple_full', (select count(*) from private.founder_members where couple_id = c.id and confirmed_at is not null) >= 2,
    'partner_joined', v_partner_joined,
    'first_member', case when first_m.id is null then null else jsonb_build_object('member_id', first_m.id, 'email', first_m.email,
       'name', first_m.name, 'language', first_m.language, 'unsub', first_m.unsub_token, 'unsubscribed', first_m.unsubscribed_at is not null) end);
end $function$;

-- Allow 'solo' in the stored answer too.
alter table private.founder_members drop constraint if exists founder_members_living_check;
alter table private.founder_members add constraint founder_members_living_check
  check (living = any (array['', 'together', 'apart', 'both', 'soon', 'solo']));

-- founder_join: accept living = 'solo' ("On my own"). Patches only that line of the live definition.
do $$
declare d text;
begin
  select pg_get_functiondef('public.founder_join(jsonb)'::regprocedure) into d;
  if position('''soon'', ''solo'')' in d) = 0 then
    d := replace(d, 'in (''together'', ''apart'', ''both'', ''soon'')', 'in (''together'', ''apart'', ''both'', ''soon'', ''solo'')');
    if position('''solo''' in d) = 0 then raise exception 'founder_join living list not found'; end if;
    execute d;
  end if;
end $$;
