# F27 Tension Policy

## V1 Rule

- Detect a `tension` notice when a `household_size` need is present and `household_size > bedrooms_min + 1`.

## Notice Shape

- Output type: `tension`
- Output message: `"{n}室对{m}口之家可能偏小"`
- `related_need_type`: `household_size`

## Current Limits

- `living_rooms` is interpretation-only and does not participate in filtering.
- No LLM-generated notices are allowed.
- If `bedrooms_min` is absent, no household-size tension is generated in V1.
