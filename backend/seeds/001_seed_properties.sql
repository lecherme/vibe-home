-- backend/seeds/001_seed_properties.sql
-- Dev / demo seed: 20 Hong Kong property listings
--
-- HOW TO RUN:
--   Option A — psql (requires DATABASE_URL with direct Postgres access):
--     psql "$DATABASE_URL" -f backend/seeds/001_seed_properties.sql
--
--   Option B — Supabase Studio (recommended):
--     Open your project → SQL Editor → paste this file → Run
--
-- Safe to re-run: ON CONFLICT (id) DO NOTHING makes it idempotent.
-- For development / demo only. Do not run in production.
--
-- Images:
--   prop-hk-001 to prop-hk-008: real photos from Supabase Storage (image[0])
--   prop-hk-009 to prop-hk-020, plus image[1] / image[2] for all: picsum.photos placeholders

INSERT INTO public.properties
  (id, title, description, price, location, bedrooms, bathrooms, area_sqm, images, status, created_at)
VALUES

-- ─── 1 — Studio · Sham Shui Po · $3.2M · available ──────────────────────────
(
  'prop-hk-001',
  'Cosy Studio in Sham Shui Po',
  'A compact yet well-designed studio on the 18th floor of a modern residential block in Sham Shui Po. Fully renovated in 2023 with an open-plan kitchen, engineered-wood flooring, and city skyline views from the living area. Five minutes'' walk to Sham Shui Po MTR Station and close to the buzzing fabric and electronics markets. Ideal for a first-time buyer or a buy-to-let investor looking for solid rental yield.',
  3200000,
  'Sham Shui Po, Kowloon, Hong Kong',
  1, 1, 28.0,
  ARRAY[
    'https://ethrhylyxtoirnemsady.supabase.co/storage/v1/object/public/home_study/properties/0f1266fa-6fae-4178-87a0-e287fe628784/2c65a2d5-fdad-49dc-a465-e52c98b198ab.jpg',
    'https://picsum.photos/seed/hk01b/800/600',
    'https://picsum.photos/seed/hk01c/800/600'
  ],
  'available',
  '2025-11-03 09:15:00+00'
),

-- ─── 2 — 1 bed · Tuen Mun · $2.8M · rented ──────────────────────────────────
(
  'prop-hk-002',
  'Modern 1-Bedroom in Tuen Mun Town Centre',
  'Freshly painted 1-bedroom apartment on the 8th floor of a well-managed estate in Tuen Mun Town Centre. The split layout separates the bedroom from the living area, making it comfortable for a working professional or couple. Shopping malls, supermarkets, and the light rail network are all within a 3-minute walk. Currently tenanted — a steady rental investment with no void period.',
  2800000,
  'Tuen Mun, New Territories, Hong Kong',
  1, 1, 42.0,
  ARRAY[
    'https://ethrhylyxtoirnemsady.supabase.co/storage/v1/object/public/home_study/properties/159af5b8-305f-4d3d-8df0-b66f9b29e618/671524b3-5739-45dc-be62-abf8612acf6b.jpg',
    'https://picsum.photos/seed/hk02b/800/600',
    'https://picsum.photos/seed/hk02c/800/600'
  ],
  'rented',
  '2025-09-18 14:30:00+00'
),

-- ─── 3 — 2 bed · North Point · $7.5M · available ─────────────────────────────
(
  'prop-hk-003',
  'Bright 2-Bedroom in North Point',
  'A cheerful 2-bedroom flat on the 22nd floor of a well-located building in North Point, enjoying unobstructed harbour views on clear days. The open kitchen flows into a spacious dining-living area with large windows that flood the space with natural light. North Point MTR Station is a 4-minute walk, and the wet market, restaurants, and City''super are all nearby. One covered car park space included.',
  7500000,
  'North Point, Hong Kong Island, Hong Kong',
  2, 1, 55.0,
  ARRAY[
    'https://ethrhylyxtoirnemsady.supabase.co/storage/v1/object/public/home_study/properties/53925d2f-4d9a-4b2e-854c-f6436b5450e9/b7281552-9fdb-4d5a-94b7-9771373d0d57.jpg',
    'https://picsum.photos/seed/hk03b/800/600',
    'https://picsum.photos/seed/hk03c/800/600'
  ],
  'available',
  '2026-01-11 08:45:00+00'
),

-- ─── 4 — 2 bed · Quarry Bay (Taikoo) · $9.8M · available ────────────────────
(
  'prop-hk-004',
  'Spacious 2-Bedroom at Taikoo Shing',
  'A generously proportioned 2-bedroom, 2-bathroom unit in Taikoo Shing, one of Hong Kong Island''s most sought-after residential estates. The unit features a large wrap-around balcony, brand-new kitchen appliances, and full access to the estate''s clubhouse, swimming pool, and tennis courts. Quarry Bay MTR is connected by an air-conditioned covered walkway — no rain, no fuss.',
  9800000,
  'Quarry Bay, Hong Kong Island, Hong Kong',
  2, 2, 72.0,
  ARRAY[
    'https://ethrhylyxtoirnemsady.supabase.co/storage/v1/object/public/home_study/properties/53e0d32b-0877-4e77-a163-27363caa6886/94bf54e4-91e5-48f1-b809-f4f44054a284.jpg',
    'https://picsum.photos/seed/hk04b/800/600',
    'https://picsum.photos/seed/hk04c/800/600'
  ],
  'available',
  '2025-12-22 11:00:00+00'
),

-- ─── 5 — 2 bed · Sha Tin · $6.2M · sold ─────────────────────────────────────
(
  'prop-hk-005',
  'Family 2-Bedroom near Sha Tin Town Hall',
  'A well-kept 2-bedroom flat on a low floor in a lushly landscaped estate opposite the Shing Mun River in Sha Tin. The bedrooms are separated by a full-length corridor, and the living room opens onto a balcony with calming garden views. Within walking distance of Sha Tin Town Hall, the New Town Plaza shopping centre, and Sha Tin MTR. Sold with all furniture and appliances included — move in immediately.',
  6200000,
  'Sha Tin, New Territories, Hong Kong',
  2, 1, 61.0,
  ARRAY[
    'https://ethrhylyxtoirnemsady.supabase.co/storage/v1/object/public/home_study/properties/7defaa79-d951-413b-bb2c-ed3e05cc1132/3b2e2052-8c3d-4ae7-8108-a0cb7df67c53.jpg',
    'https://picsum.photos/seed/hk05b/800/600',
    'https://picsum.photos/seed/hk05c/800/600'
  ],
  'sold',
  '2025-10-30 16:20:00+00'
),

-- ─── 6 — 3 bed · Wan Chai · $14.5M · available ───────────────────────────────
(
  'prop-hk-006',
  'Contemporary 3-Bedroom in Wan Chai',
  'A beautifully styled 3-bedroom, 2-bathroom apartment on the 31st floor of a landmark tower in the heart of Wan Chai. Floor-to-ceiling windows capture a panoramic view of Victoria Harbour and Kowloon. The open-plan living-dining area features bespoke joinery, underfloor heating in both bathrooms, and a premium Gaggenau kitchen. Two MTR lines are within a 5-minute walk.',
  14500000,
  'Wan Chai, Hong Kong Island, Hong Kong',
  3, 2, 95.0,
  ARRAY[
    'https://ethrhylyxtoirnemsady.supabase.co/storage/v1/object/public/home_study/properties/c6714167-547c-45de-b772-e70df55d4e5e/c5d210a3-905b-4442-9db4-fae1a656e7f2.jpg',
    'https://picsum.photos/seed/hk06b/800/600',
    'https://picsum.photos/seed/hk06c/800/600'
  ],
  'available',
  '2026-01-28 12:00:00+00'
),

-- ─── 7 — 3 bed · Kennedy Town · $12.8M · available ──────────────────────────
(
  'prop-hk-007',
  'Renovated 3-Bedroom with Sea View in Kennedy Town',
  'A fully renovated 3-bedroom, 2-bathroom apartment on the 20th floor of a residential development perched above Kennedy Town Promenade. The living room and master bedroom both enjoy direct views of the Lamma Channel. The kitchen has been extended and fitted with Siemens appliances and a custom wine cooler. The building offers a 24-hour concierge, a rooftop garden, and a residents'' gym.',
  12800000,
  'Kennedy Town, Hong Kong Island, Hong Kong',
  3, 2, 88.0,
  ARRAY[
    'https://ethrhylyxtoirnemsady.supabase.co/storage/v1/object/public/home_study/properties/c6714167-547c-45de-b772-e70df55d4e5e/743660-3840x2160-desktop-4k-house-wallpaper-photo.jpg',
    'https://picsum.photos/seed/hk07b/800/600',
    'https://picsum.photos/seed/hk07c/800/600'
  ],
  'available',
  '2025-11-15 15:30:00+00'
),

-- ─── 8 — 3 bed · Tsim Sha Tsui · $18.9M · available ─────────────────────────
(
  'prop-hk-008',
  'Luxury 3-Bedroom in Tsim Sha Tsui East',
  'An impeccably finished 3-bedroom, 2-bathroom apartment on the 38th floor of a prestigious tower in Tsim Sha Tsui East. The full Hong Kong Island skyline and Victoria Harbour are on display from every room. Bespoke Italian marble flooring, motorised window blinds, and a Crestron smart-home system are all included. The building offers a 24-hour concierge, valet parking, a lap pool, and a business lounge.',
  18900000,
  'Tsim Sha Tsui, Kowloon, Hong Kong',
  3, 2, 105.0,
  ARRAY[
    'https://ethrhylyxtoirnemsady.supabase.co/storage/v1/object/public/home_study/properties/c6714167-547c-45de-b772-e70df55d4e5e/istockphoto-524085051-1024x1024.jpg',
    'https://picsum.photos/seed/hk08b/800/600',
    'https://picsum.photos/seed/hk08c/800/600'
  ],
  'available',
  '2026-02-03 11:30:00+00'
),

-- ─── 9 – 20: picsum placeholder images ───────────────────────────────────────

-- ─── 9 — 2 bed · Tai Po · $5.4M · available ─────────────────────────────────
(
  'prop-hk-009',
  'Peaceful 2-Bedroom near Tai Po Waterfront Park',
  'A tranquil 2-bedroom apartment on the 15th floor of a low-density residential development in Tai Po, surrounded by greenery and a short cycle ride from Tai Po Waterfront Park. The master bedroom enjoys an en-suite wet room, and the living space opens onto a large balcony with views of the Plover Cove hills. Tai Po Market KCR station is 7 minutes away on foot.',
  5400000,
  'Tai Po, New Territories, Hong Kong',
  2, 1, 58.0,
  ARRAY[
    'https://picsum.photos/seed/hk09a/800/600',
    'https://picsum.photos/seed/hk09b/800/600',
    'https://picsum.photos/seed/hk09c/800/600'
  ],
  'available',
  '2026-02-14 09:30:00+00'
),

-- ─── 10 — 1 bed · Kennedy Town · $5.9M · rented ─────────────────────────────
(
  'prop-hk-010',
  '1-Bedroom Sea-View Flat in Kennedy Town',
  'A sleek 1-bedroom apartment on the 28th floor of a boutique residential tower in Kennedy Town, offering sweeping views of the Lamma Channel and Green Island. The open-plan kitchen features Italian marble worktops and Miele appliances. Kennedy Town MTR is a 6-minute walk, with the waterfront promenade and popular restaurants steps from the building. Currently tenanted — an ideal hands-off rental investment.',
  5900000,
  'Kennedy Town, Hong Kong Island, Hong Kong',
  1, 1, 38.0,
  ARRAY[
    'https://picsum.photos/seed/hk10a/800/600',
    'https://picsum.photos/seed/hk10b/800/600',
    'https://picsum.photos/seed/hk10c/800/600'
  ],
  'rented',
  '2025-07-19 13:00:00+00'
),

-- ─── 11 — 3 bed · Mid-Levels · $26.5M · available ───────────────────────────
(
  'prop-hk-011',
  'Elegant 3-Bedroom in Mid-Levels West',
  'A refined 3-bedroom, 3-bathroom apartment on the 19th floor of a distinguished residential development on Robinson Road in Mid-Levels West. Redesigned with a bespoke open kitchen, herringbone parquet flooring, and a full-width balcony overlooking the lush hillside. The building provides 24-hour security, a residents'' clubhouse, and direct access to the Mid-Levels Escalator system 3 minutes away.',
  26500000,
  'Mid-Levels, Hong Kong Island, Hong Kong',
  3, 3, 135.0,
  ARRAY[
    'https://picsum.photos/seed/hk11a/800/600',
    'https://picsum.photos/seed/hk11b/800/600',
    'https://picsum.photos/seed/hk11c/800/600'
  ],
  'available',
  '2026-01-05 10:00:00+00'
),

-- ─── 12 — 4 bed · Causeway Bay · $32M · available ───────────────────────────
(
  'prop-hk-012',
  'Prestigious 4-Bedroom Penthouse in Causeway Bay',
  'A rare full-floor 4-bedroom, 3-bathroom penthouse on the 42nd floor of a landmark residential tower in Causeway Bay. The 270-degree panorama takes in Victoria Harbour, the Happy Valley Racecourse, and Hong Kong Island''s mountainous spine. The kitchen is fitted with Sub-Zero and Wolf appliances, and the master suite occupies an entire wing with a dressing room, soaking tub, and rain shower. Three car park spaces and a private wine cellar included.',
  32000000,
  'Causeway Bay, Hong Kong Island, Hong Kong',
  4, 3, 158.0,
  ARRAY[
    'https://picsum.photos/seed/hk12a/800/600',
    'https://picsum.photos/seed/hk12b/800/600',
    'https://picsum.photos/seed/hk12c/800/600'
  ],
  'available',
  '2026-02-28 09:00:00+00'
),

-- ─── 13 — 4 bed · Stanley · $28.5M · sold ───────────────────────────────────
(
  'prop-hk-013',
  'Stylish 4-Bedroom Townhouse in Stanley',
  'A stunning 4-bedroom, 3-bathroom townhouse set within a gated garden community in Stanley, with views of the bay and surrounding hills. The double-fronted property spans three floors and features a private rooftop terrace with a jacuzzi, a chef''s kitchen with a La Cornue range, and a home cinema on the lower level. Two covered parking spaces and a domestic helper''s suite complete this exceptional home.',
  28500000,
  'Stanley, Hong Kong Island, Hong Kong',
  4, 3, 185.0,
  ARRAY[
    'https://picsum.photos/seed/hk13a/800/600',
    'https://picsum.photos/seed/hk13b/800/600',
    'https://picsum.photos/seed/hk13c/800/600'
  ],
  'sold',
  '2025-04-08 13:15:00+00'
),

-- ─── 14 — 5 bed · The Peak · $75M · available ───────────────────────────────
(
  'prop-hk-014',
  'Spectacular 5-Bedroom Villa at The Peak',
  'An extraordinary 5-bedroom, 4-bathroom villa commanding one of the most coveted positions on Victoria Peak, with 360-degree views encompassing the entire Hong Kong skyline, Lantau Island, and the South China Sea on clear days. Spread across two floors and a rooftop entertaining deck with an infinity pool and outdoor cinema. Interior highlights include a library, home gym, sauna, and a fully equipped home office. Three garages, two domestic helper rooms, and a private garden of 150 m².',
  75000000,
  'The Peak, Hong Kong Island, Hong Kong',
  5, 4, 320.0,
  ARRAY[
    'https://picsum.photos/seed/hk14a/800/600',
    'https://picsum.photos/seed/hk14b/800/600',
    'https://picsum.photos/seed/hk14c/800/600'
  ],
  'available',
  '2026-03-10 08:30:00+00'
),

-- ─── 15 — 4 bed · Sai Kung · $19.5M · available ─────────────────────────────
(
  'prop-hk-015',
  'Tranquil 4-Bedroom Village House in Sai Kung',
  'A beautifully restored 4-bedroom, 3-bathroom village house in the hills above Sai Kung, surrounded by country park on three sides. The ground floor features a double-height living room and a professional-grade open kitchen; the second floor has three bedrooms; and the rooftop terrace offers unobstructed sea views towards the High Island Reservoir. Private parking for two vehicles included. Close to Sai Kung town''s seafood restaurants and water sports facilities.',
  19500000,
  'Sai Kung, New Territories, Hong Kong',
  4, 3, 210.0,
  ARRAY[
    'https://picsum.photos/seed/hk15a/800/600',
    'https://picsum.photos/seed/hk15b/800/600',
    'https://picsum.photos/seed/hk15c/800/600'
  ],
  'available',
  '2026-03-20 08:00:00+00'
),

-- ─── 16 — 5 bed · Repulse Bay · $88M · available ────────────────────────────
(
  'prop-hk-016',
  'Grand 5-Bedroom Beachfront Villa in Repulse Bay',
  'A magnificent 5-bedroom, 4-bathroom beachfront villa in the heart of Repulse Bay, widely regarded as Hong Kong''s most desirable residential address. The villa spans three floors with a private garden leading onto a landscaped terrace above Repulse Bay Beach. The main living area features soaring 5-metre ceilings and floor-to-ceiling glazing framing the sea. The kitchen is anchored by a 4-metre Calacatta marble island, and the master suite occupies the entire top floor with a private sun deck, walk-in dressing room, and a free-standing copper bath.',
  88000000,
  'Repulse Bay, Hong Kong Island, Hong Kong',
  5, 4, 380.0,
  ARRAY[
    'https://picsum.photos/seed/hk16a/800/600',
    'https://picsum.photos/seed/hk16b/800/600',
    'https://picsum.photos/seed/hk16c/800/600'
  ],
  'available',
  '2026-04-01 10:00:00+00'
),

-- ─── 17 — 3 bed · Happy Valley · $22M · sold ─────────────────────────────────
(
  'prop-hk-017',
  'Charming 3-Bedroom Duplex near Happy Valley Racecourse',
  'A rare 3-bedroom, 2-bathroom garden duplex in a low-rise boutique development steps from the Happy Valley Racecourse. The ground floor opens directly onto a private landscaped garden of 40 m², and the upper floor features a study and a master bedroom with an en-suite spa bathroom. Two car park spaces and a private storage room included. Tram and bus connections to Central take under 10 minutes.',
  22000000,
  'Happy Valley, Hong Kong Island, Hong Kong',
  3, 2, 118.0,
  ARRAY[
    'https://picsum.photos/seed/hk17a/800/600',
    'https://picsum.photos/seed/hk17b/800/600',
    'https://picsum.photos/seed/hk17c/800/600'
  ],
  'sold',
  '2025-05-22 14:00:00+00'
),

-- ─── 18 — 2 bed · Mong Kok · $7.2M · available ──────────────────────────────
(
  'prop-hk-018',
  'Urban 2-Bedroom in Mong Kok',
  'A smartly renovated 2-bedroom flat on the 16th floor of a well-managed block in the heart of Mong Kok. The kitchen has been opened up to create an airy living-dining area, and the bathrooms were completely refitted in 2024. Mong Kok MTR is 3 minutes away on foot, and the Langham Place mall, Ladies'' Market, and a host of dim sum restaurants are all around the corner.',
  7200000,
  'Mong Kok, Kowloon, Hong Kong',
  2, 1, 52.0,
  ARRAY[
    'https://picsum.photos/seed/hk18a/800/600',
    'https://picsum.photos/seed/hk18b/800/600',
    'https://picsum.photos/seed/hk18c/800/600'
  ],
  'available',
  '2026-03-02 10:45:00+00'
),

-- ─── 19 — 3 bed · Aberdeen · $13.5M · rented ─────────────────────────────────
(
  'prop-hk-019',
  'Harbour-View 3-Bedroom in Aberdeen',
  'A spacious 3-bedroom flat on the 25th floor overlooking the iconic Aberdeen Typhoon Shelter and its fleet of traditional sampans. The open-plan layout features a chef''s kitchen with a large island, and the master suite has a walk-in wardrobe and a soaking tub. The building''s clubhouse includes an indoor pool, a rooftop terrace, and a children''s play area. Currently tenanted at $38,000 per month.',
  13500000,
  'Aberdeen, Hong Kong Island, Hong Kong',
  3, 2, 98.0,
  ARRAY[
    'https://picsum.photos/seed/hk19a/800/600',
    'https://picsum.photos/seed/hk19b/800/600',
    'https://picsum.photos/seed/hk19c/800/600'
  ],
  'rented',
  '2025-06-10 09:00:00+00'
),

-- ─── 20 — 1 bed · Cheung Sha Wan · $3.8M · sold ─────────────────────────────
(
  'prop-hk-020',
  'Affordable 1-Bedroom in Cheung Sha Wan',
  'Well-maintained 1-bedroom flat on the 12th floor of a residential tower in Cheung Sha Wan. Bright eastern-facing living room, modernised bathroom, and ample built-in storage throughout. Just two stops from Sham Shui Po MTR and minutes from the D2 Place lifestyle mall. A practical entry-level home in one of Kowloon''s most convenient neighbourhoods.',
  3800000,
  'Cheung Sha Wan, Kowloon, Hong Kong',
  1, 1, 35.0,
  ARRAY[
    'https://picsum.photos/seed/hk20a/800/600',
    'https://picsum.photos/seed/hk20b/800/600',
    'https://picsum.photos/seed/hk20c/800/600'
  ],
  'sold',
  '2025-08-05 10:00:00+00'
)

ON CONFLICT (id) DO NOTHING;

-- ─── Favorites: manual insert example — do NOT run as-is ─────────────────────
-- Find your user UUID in Supabase Studio → Authentication → Users.
-- Then paste into SQL Editor and run.
--
-- INSERT INTO public.favorites (user_id, property_id, created_at) VALUES
--   ('<your-user-uuid>', 'prop-hk-006', now()),
--   ('<your-user-uuid>', 'prop-hk-011', now()),
--   ('<your-user-uuid>', 'prop-hk-014', now()),
--   ('<your-user-uuid>', 'prop-hk-004', now())
-- ON CONFLICT DO NOTHING;
