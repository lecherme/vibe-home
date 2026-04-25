from datetime import datetime, timezone
from typing import Optional

from app.schemas.property import Property, PropertyStatus


PROPERTIES: list[Property] = [
    Property(
        id="prop_001",
        title="Harbor View Penthouse",
        description=(
            "Top-floor penthouse with wraparound windows, a private terrace, and "
            "direct elevator access overlooking the marina."
        ),
        price=2450000.0,
        location="Seattle, WA",
        bedrooms=3,
        bathrooms=2,
        area_sqm=182.5,
        images=[
            "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85",
            "https://images.unsplash.com/photo-1494526585095-c41746248156",
        ],
        status=PropertyStatus.AVAILABLE,
        created_at=datetime(2026, 4, 23, 16, 30, tzinfo=timezone.utc),
    ),
    Property(
        id="prop_002",
        title="Desert Courtyard Retreat",
        description=(
            "Single-level home with a shaded courtyard, polished concrete floors, "
            "and a seamless indoor-outdoor entertaining layout."
        ),
        price=1180000.0,
        location="Scottsdale, AZ",
        bedrooms=4,
        bathrooms=3,
        area_sqm=210.2,
        images=[
            "https://images.unsplash.com/photo-1564013799919-ab600027ffc6",
            "https://images.unsplash.com/photo-1512917774080-9991f1c4c750",
        ],
        status=PropertyStatus.AVAILABLE,
        created_at=datetime(2026, 4, 21, 9, 15, tzinfo=timezone.utc),
    ),
    Property(
        id="prop_003",
        title="Parkside Brownstone",
        description=(
            "Renovated brownstone with original millwork, chef's kitchen, and a "
            "garden-level lounge opening onto a landscaped patio."
        ),
        price=1985000.0,
        location="Brooklyn, NY",
        bedrooms=4,
        bathrooms=3,
        area_sqm=196.8,
        images=[
            "https://images.unsplash.com/photo-1600585154526-990dced4db0d",
            "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c",
        ],
        status=PropertyStatus.SOLD,
        created_at=datetime(2026, 4, 19, 18, 5, tzinfo=timezone.utc),
    ),
    Property(
        id="prop_004",
        title="Lakefront Glass House",
        description=(
            "Contemporary lakefront residence with double-height living room, "
            "sauna, and a cantilevered deck above the waterline."
        ),
        price=3125000.0,
        location="Madison, WI",
        bedrooms=5,
        bathrooms=4,
        area_sqm=328.4,
        images=[
            "https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde",
            "https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b",
        ],
        status=PropertyStatus.AVAILABLE,
        created_at=datetime(2026, 4, 18, 12, 45, tzinfo=timezone.utc),
    ),
    Property(
        id="prop_005",
        title="Historic Loft at Market Square",
        description=(
            "Warehouse loft conversion with exposed brick, timber beams, and "
            "oversized factory windows in a walkable downtown district."
        ),
        price=845000.0,
        location="Nashville, TN",
        bedrooms=2,
        bathrooms=2,
        area_sqm=134.1,
        images=[
            "https://images.unsplash.com/photo-1484154218962-a197022b5858",
            "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688",
        ],
        status=PropertyStatus.RENTED,
        created_at=datetime(2026, 4, 17, 14, 20, tzinfo=timezone.utc),
    ),
    Property(
        id="prop_006",
        title="Cliffside Villa",
        description=(
            "Ocean-facing villa with infinity pool, detached guest suite, and "
            "sunset terraces carved into the hillside."
        ),
        price=4290000.0,
        location="Malibu, CA",
        bedrooms=5,
        bathrooms=5,
        area_sqm=410.7,
        images=[
            "https://images.unsplash.com/photo-1600607687644-c7171b42498f",
            "https://images.unsplash.com/photo-1600573472592-401b489a3cdc",
        ],
        status=PropertyStatus.AVAILABLE,
        created_at=datetime(2026, 4, 15, 8, 10, tzinfo=timezone.utc),
    ),
    Property(
        id="prop_007",
        title="River District Townhome",
        description=(
            "Three-story townhome with rooftop lounge, attached garage, and open "
            "kitchen-dining level near the arts district."
        ),
        price=965000.0,
        location="Portland, OR",
        bedrooms=3,
        bathrooms=3,
        area_sqm=158.0,
        images=[
            "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d",
            "https://images.unsplash.com/photo-1600047509358-9dc75507daeb",
        ],
        status=PropertyStatus.AVAILABLE,
        created_at=datetime(2026, 4, 14, 11, 55, tzinfo=timezone.utc),
    ),
    Property(
        id="prop_008",
        title="Countryside Manor",
        description=(
            "Expansive manor home with library, conservatory, and equestrian-ready "
            "grounds bordered by mature oak trees."
        ),
        price=2750000.0,
        location="Lexington, KY",
        bedrooms=6,
        bathrooms=5,
        area_sqm=455.6,
        images=[
            "https://images.unsplash.com/photo-1570129477492-45c003edd2be",
            "https://images.unsplash.com/photo-1448630360428-65456885c650",
        ],
        status=PropertyStatus.SOLD,
        created_at=datetime(2026, 4, 12, 10, 0, tzinfo=timezone.utc),
    ),
    Property(
        id="prop_009",
        title="Midtown Skyline Condo",
        description=(
            "Corner condo with panoramic skyline views, concierge access, and a "
            "residents-only fitness studio and lounge."
        ),
        price=1125000.0,
        location="Atlanta, GA",
        bedrooms=2,
        bathrooms=2,
        area_sqm=121.4,
        images=[
            "https://images.unsplash.com/photo-1600607688969-a5bfcd646154",
            "https://images.unsplash.com/photo-1460317442991-0ec209397118",
        ],
        status=PropertyStatus.AVAILABLE,
        created_at=datetime(2026, 4, 11, 19, 40, tzinfo=timezone.utc),
    ),
    Property(
        id="prop_010",
        title="Snowline Chalet",
        description=(
            "Mountain chalet with vaulted timber ceilings, stone fireplace, and "
            "heated gear room minutes from the lifts."
        ),
        price=1540000.0,
        location="Aspen, CO",
        bedrooms=4,
        bathrooms=3,
        area_sqm=187.9,
        images=[
            "https://images.unsplash.com/photo-1518780664697-55e3ad937233",
            "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85",
        ],
        status=PropertyStatus.RENTED,
        created_at=datetime(2026, 4, 9, 7, 25, tzinfo=timezone.utc),
    ),
    Property(
        id="prop_011",
        title="Palm Grove Bungalow",
        description=(
            "Renovated bungalow with breezy lanai, terrazzo floors, and lush "
            "tropical planting around a saltwater plunge pool."
        ),
        price=739000.0,
        location="St. Petersburg, FL",
        bedrooms=3,
        bathrooms=2,
        area_sqm=116.3,
        images=[
            "https://images.unsplash.com/photo-1605146769289-440113cc3d00",
            "https://images.unsplash.com/photo-1512915922686-57c11dde9b6b",
        ],
        status=PropertyStatus.AVAILABLE,
        created_at=datetime(2026, 4, 7, 13, 5, tzinfo=timezone.utc),
    ),
    Property(
        id="prop_012",
        title="University District Duplex",
        description=(
            "Income-friendly duplex with refreshed interiors, separate entrances, "
            "and quick access to campus and transit."
        ),
        price=689000.0,
        location="Ann Arbor, MI",
        bedrooms=4,
        bathrooms=2,
        area_sqm=149.7,
        images=[
            "https://images.unsplash.com/photo-1494526585095-c41746248156",
            "https://images.unsplash.com/photo-1449844908441-8829872d2607",
        ],
        status=PropertyStatus.SOLD,
        created_at=datetime(2026, 4, 5, 15, 30, tzinfo=timezone.utc),
    ),
    Property(
        id="prop_013",
        title="Canal House Residence",
        description=(
            "Light-filled residence with indoor atrium, floating stair, and a "
            "dockside deck designed for paddleboard access."
        ),
        price=1330000.0,
        location="Fort Lauderdale, FL",
        bedrooms=3,
        bathrooms=3,
        area_sqm=172.6,
        images=[
            "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c",
            "https://images.unsplash.com/photo-1600585154340-be6161a56a0c",
        ],
        status=PropertyStatus.AVAILABLE,
        created_at=datetime(2026, 4, 3, 17, 50, tzinfo=timezone.utc),
    ),
    Property(
        id="prop_014",
        title="Old Town Courtyard Flat",
        description=(
            "Quiet courtyard flat with limestone finishes, bespoke storage, and "
            "walkable access to cafés, galleries, and the river trail."
        ),
        price=598000.0,
        location="Savannah, GA",
        bedrooms=1,
        bathrooms=1,
        area_sqm=78.2,
        images=[
            "https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6",
            "https://images.unsplash.com/photo-1480074568708-e7b720bb3f09",
        ],
        status=PropertyStatus.RENTED,
        created_at=datetime(2026, 4, 2, 9, 45, tzinfo=timezone.utc),
    ),
    Property(
        id="prop_015",
        title="Forest Edge Cabin",
        description=(
            "Minimalist timber cabin with wood stove, reading loft, and floor-to-"
            "ceiling glazing facing a protected forest preserve."
        ),
        price=525000.0,
        location="Bend, OR",
        bedrooms=2,
        bathrooms=1,
        area_sqm=89.5,
        images=[
            "https://images.unsplash.com/photo-1518780664697-55e3ad937233",
            "https://images.unsplash.com/photo-1472224371017-08207f84aaae",
        ],
        status=PropertyStatus.AVAILABLE,
        created_at=datetime(2026, 3, 31, 20, 15, tzinfo=timezone.utc),
    ),
    Property(
        id="prop_016",
        title="Capitol Hill Row House",
        description=(
            "Updated row house with solar panels, a lower-level studio suite, and "
            "a brick patio designed for year-round outdoor dining."
        ),
        price=1495000.0,
        location="Washington, DC",
        bedrooms=4,
        bathrooms=3,
        area_sqm=201.0,
        images=[
            "https://images.unsplash.com/photo-1600047509782-20d39509f26d",
            "https://images.unsplash.com/photo-1600566752355-35792bedcfea",
        ],
        status=PropertyStatus.AVAILABLE,
        created_at=datetime(2026, 3, 29, 12, 0, tzinfo=timezone.utc),
    ),
]


def get_all() -> list[Property]:
    return [property_item.model_copy(deep=True) for property_item in PROPERTIES]


def get_by_id(id: str) -> Optional[Property]:
    for property_item in PROPERTIES:
        if property_item.id == id:
            return property_item.model_copy(deep=True)

    return None
