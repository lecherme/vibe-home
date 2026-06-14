-- backend/seeds/002_seed_property_fields.sql
-- Backfill additional property metadata for existing demo listings.
--
-- HOW TO RUN:
--   Option A — psql (requires DATABASE_URL with direct Postgres access):
--     psql "$DATABASE_URL" -f backend/seeds/002_seed_property_fields.sql
--
--   Option B — Supabase Studio:
--     Open your project -> SQL Editor -> paste this file -> Run

UPDATE public.properties
SET
  built_year = data.built_year,
  subway_distance_m = data.subway_distance_m,
  tags = data.tags
FROM (
  VALUES
    ('prop-hk-001', 1998, 320, ARRAY['近地铁', '装修好', '市景']::text[]),
    ('prop-hk-002', 2004, 180, ARRAY['rental yield', 'town centre', 'light rail access']::text[]),
    ('prop-hk-003', 1996, 260, ARRAY['harbour view', 'natural light', '近地铁']::text[]),
    ('prop-hk-004', 1981, 140, ARRAY['covered walkway', 'clubhouse', '家庭房']::text[]),
    ('prop-hk-005', 1987, 520, ARRAY['river view', '家具齐全', 'family friendly']::text[]),
    ('prop-hk-006', 2016, 340, ARRAY['harbour view', 'luxury renovation', 'dual MTR access']::text[]),
    ('prop-hk-007', 2009, 480, ARRAY['sea view', '装修好', 'rooftop gym']::text[]),
    ('prop-hk-008', 2018, 300, ARRAY['Victoria Harbour view', 'smart home', 'concierge']::text[]),
    ('prop-hk-009', 2001, 650, ARRAY['balcony', '绿景', 'quiet estate']::text[]),
    ('prop-hk-010', 2015, 430, ARRAY['sea view', 'boutique tower', 'tenanted']::text[]),
    ('prop-hk-011', 1993, 220, ARRAY['Mid-Levels escalator', 'parquet flooring', 'clubhouse']::text[]),
    ('prop-hk-012', 2020, 210, ARRAY['penthouse', 'harbour view', 'wine cellar']::text[]),
    ('prop-hk-013', 1999, 1450, ARRAY['townhouse', 'rooftop terrace', 'gated community']::text[]),
    ('prop-hk-014', 2012, 1500, ARRAY['villa', 'infinity pool', '全景']::text[]),
    ('prop-hk-015', 2008, 1500, ARRAY['village house', 'sea view', 'private parking']::text[]),
    ('prop-hk-016', 2019, 1480, ARRAY['beachfront', 'private garden', 'luxury villa']::text[]),
    ('prop-hk-017', 1995, 1100, ARRAY['duplex', 'private garden', 'racecourse access']::text[]),
    ('prop-hk-018', 1991, 190, ARRAY['近地铁', '2024 renovation', 'shopping district']::text[]),
    ('prop-hk-019', 2011, 1180, ARRAY['harbour view', 'clubhouse', 'walk-in wardrobe']::text[]),
    ('prop-hk-020', 2003, 420, ARRAY['entry level', 'built-in storage', 'D2 Place']::text[]),
    ('prop-hk-021', 2005, 280, ARRAY['近地铁', 'studio', '旺角商圈']::text[]),
    ('prop-hk-022', 2010, 520, ARRAY['马铁沿线', 'quiet estate', 'first-time buyer']::text[]),
    ('prop-hk-023', 2017, 350, ARRAY['将军澳新区', '近地铁', 'family friendly']::text[])
) AS data(id, built_year, subway_distance_m, tags)
WHERE public.properties.id = data.id;
