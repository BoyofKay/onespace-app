-- OneSpace Production only (17 Nov 2026): keep a yes/no record of which Edge Function secrets exist,
-- so the Command Center (read-only) can show them without anyone opening the Supabase console.
-- Every 30 minutes: store the answer to the previous secrets-check call, then ask again.
-- Values are never read or stored — only true/false per secret name.
create table if not exists private.ops_secret_status (
  name text primary key check (name ~ '^[A-Z0-9_]{3,80}$'),
  present boolean not null,
  checked_at timestamptz not null
);
alter table private.ops_secret_status enable row level security;
create table if not exists private.ops_pending_requests (
  kind text primary key,
  request_id bigint not null,
  sent_at timestamptz not null
);
alter table private.ops_pending_requests enable row level security;

create or replace function private.refresh_secret_status() returns void
language plpgsql security definer set search_path = '' as $$
declare
  pending record;
  body jsonb;
  k text;
begin
  select p.request_id, p.sent_at into pending from private.ops_pending_requests p where p.kind = 'secrets';
  if found then
    select h.content::jsonb into body from net._http_response h
      where h.id = pending.request_id and h.status_code = 200;
    if body is not null and jsonb_typeof(body) = 'object' then
      for k in select jsonb_object_keys(body) loop
        if jsonb_typeof(body->k) = 'boolean' and k ~ '^[A-Z0-9_]{3,80}$' then
          insert into private.ops_secret_status (name, present, checked_at) values (k, (body->>k)::boolean, pending.sent_at)
          on conflict (name) do update set present = excluded.present, checked_at = excluded.checked_at;
        end if;
      end loop;
    end if;
  end if;
  insert into private.ops_pending_requests (kind, request_id, sent_at)
  values ('secrets', net.http_get('https://letcgxbnblohhfyeuigz.supabase.co/functions/v1/secrets-check',
      headers := jsonb_build_object('x-onespace-push-secret',
        (select decrypted_secret from vault.decrypted_secrets where name = 'onespace_push_worker_secret')),
      timeout_milliseconds := 20000), now())
  on conflict (kind) do update set request_id = excluded.request_id, sent_at = excluded.sent_at;
exception when others then
  null; -- monitoring must never fail loudly
end $$;
revoke all on function private.refresh_secret_status() from public;

select cron.schedule('onespace-secret-status', '*/30 * * * *', $c$select private.refresh_secret_status()$c$);
