alter table if exists public.properties
    add column if not exists built_year integer,
    add column if not exists subway_distance_m integer,
    add column if not exists tags text[] not null default '{}'::text[];
