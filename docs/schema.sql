-- Supabase schema for the workout planner. Run once in the SQL editor of
-- your own project.

create table public.sessions (
  id uuid primary key default gen_random_uuid(),
  session_day text not null,
  session_date date not null,
  session_style text not null default 'unspecified',
  notes text,
  data jsonb not null,
  created_at timestamptz not null default now()
);

-- Single-row table: where the user is in the card queue.
create table public.rotation_state (
  id integer primary key default 1,
  queue_position integer not null default 0
);
insert into public.rotation_state (id, queue_position) values (1, 0);

-- Per-date overrides for the recurring commitment (e.g. a skipped or extra
-- team sport session). Overrides always win over the default weekly pattern.
create table public.commitment_overrides (
  id uuid primary key default gen_random_uuid(),
  on_date date not null unique,
  has_commitment boolean not null
);

create table public.user_preferences (
  exercise_name text primary key,
  excluded boolean not null default false,
  exclusion_reason text,
  hard_to_access boolean not null default false,
  access_note text
);
