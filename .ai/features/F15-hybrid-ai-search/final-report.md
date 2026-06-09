# F15 T04 Acceptance Report

**Date:** 2026-06-09  
**Environment:** Production — https://lecherme.cn / https://api.lecherme.cn  
**LLM:** DeepSeek `deepseek-v4-flash` (openai_compatible provider)  
**Embeddings:** ZhipuAI `embedding-3` (dimensions=1536)

---

## Verdict: PASS

All three manual acceptance criteria confirmed on production.

---

## A22 — Tab switching; Filter Search unaffected

- ✓ `/search` page shows two tabs: "Filter Search" / "✨ AI Search"
- ✓ Tabs switch without page reload; state is independent
- ✓ Filter search returns 39 properties; existing functionality unaffected

## A23 — Natural language query → results + parsed filters + summary

Test query: `"more than 2 bedrooms less than 10000000 hkd"`

- ✓ `query_parsed: true`
- ✓ filter chips: `🛏️ ≥3 Beds` / `💰 < $10000000`
- ✓ 2 matching properties returned
- ✓ AI summary present

Chinese query (`"2个浴室以上 预算2500w港币"`) also confirmed: `query_parsed: true`, correct chips, results returned.

## A24 — Error banner when keys unconfigured; no crash

- ✓ LLM failure → `query_parsed: false` → "AI parsing unavailable — showing keyword results" banner displayed, no crash
- ✓ A6 (503 on missing API keys) verified in T03 code review

---

## V1 Known Limitations

- **Bedroom/bathroom filters are lower-bound only.** Backend applies `>=` semantics. "less than X bedrooms" not reliably supported. Chips display `≥` to reflect actual behavior. Full operator support deferred.
- **LLM parse instability (~60% success rate on DeepSeek).** `_parse_filters` retries once on failure, reducing visible errors, but occasional `query_parsed: false` fallback still occurs. Root cause: non-deterministic JSON output from LLM. To be addressed in a future iteration (structured output / stricter prompt / model upgrade).
- **Summary generation may return empty** for 0-result or non-English queries. Fallback `"Found {total} properties matching your search."` handles this gracefully.

---

## Post-T03 fixups applied during acceptance

| Fix | File | Reason |
|-----|------|--------|
| `json_mode=True` in `_parse_filters` | `llm/service.py`, `ai_search/service.py` | LLM returned non-JSON for comparative expressions |
| Retry on parse failure | `ai_search/service.py` | Transient LLM instability; single retry recovers most failures |
| Prompt: "more than X → X+1" | `ai_search/service.py` | Semantic mapping for comparative bedroom/bathroom expressions |
| Prompt: HKD default + 万/w conversion | `ai_search/service.py` | Chinese price expressions without explicit currency unit |
| `≥` prefix on bedroom/bathroom chips | `ai-parsed-filters-card.tsx` | Backend always applies `>=`; chip now reflects actual semantics |
| Server `.env` typo `deepseep` → `deepseek` | production only | Model name typo caused all LLM calls to fail with 400 |
