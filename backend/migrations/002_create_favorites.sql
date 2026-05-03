create table if not exists public.favorites (
    user_id text not null,
    property_id text not null references public.properties(id) on delete cascade,
    created_at timestamptz not null default timezone('utc', now()),
    constraint favorites_user_id_property_id_key unique (user_id, property_id)
);
