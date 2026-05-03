create table if not exists public.properties (
    id text primary key,
    title text not null,
    description text not null,
    price double precision not null check (price >= 0),
    location text not null,
    bedrooms integer not null check (bedrooms >= 0),
    bathrooms integer not null check (bathrooms >= 0),
    area_sqm double precision not null check (area_sqm >= 0),
    images text[] not null default '{}'::text[],
    status text not null check (status in ('available', 'sold', 'rented')),
    created_at timestamptz not null default timezone('utc', now())
);
