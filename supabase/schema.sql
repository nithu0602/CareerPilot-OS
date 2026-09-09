create table if not exists candidate_profiles (
  id uuid primary key default gen_random_uuid(),
  display_name text,
  email text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists jobs (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  company text not null,
  location text,
  source_url text,
  created_at timestamptz not null default now()
);

create table if not exists applications (
  id uuid primary key default gen_random_uuid(),
  candidate_profile_id uuid references candidate_profiles(id) on delete cascade,
  job_id uuid references jobs(id) on delete cascade,
  status text not null default 'saved',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
