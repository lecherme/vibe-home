# F27 Need Interpretation Layer

## Goal

让 AI search 真正理解用户需求，而不只是提取 filter。

当用户说"一室两厅 一家三口"，系统应该：

1. 修复入口：一室两厅 正确进入搜索管道（BUG-026 并入）
2. 正确解析 filter：bedrooms_min=1
3. 识别并展示意图：living_rooms=2（展示给用户，暂不参与过滤）
4. 识别场景信号：household_size=3，raw 保留"一家三口"
5. 检测 tension 并生成 notice："1室对3口之家可能偏小"
6. 不丢弃任何用户原始表达

核心产品原则：理解用户意图和有没有数据是两件独立的事。
系统必须向用户反馈"我理解了什么"，无论搜索结果是否存在。

## Includes: BUG-026 — intent guard 修复

`_is_property_search` 中的房型 pattern 只匹配阿拉伯数字：

```python
re.compile(r"\d+\s*(?:室|居|卧|卫|bedrooms?|beds?|bathrooms?|baths?)\b")
```

"一室两厅" 在 `_CHINESE_DIGIT_RE` 转换之前就被 guard 拒绝，永远进不了 `_parse_filters`。

修复方案：在 `_is_property_search` 入口处先用 `_CHINESE_DIGIT_RE` 做中文数字转换，再做 pattern 匹配。同时补充 `厅` 的匹配支持：

```python
re.compile(r"\d+\s*(?:室|厅|居|卧|卫|bedrooms?|beds?|bathrooms?|baths?)\b", re.IGNORECASE)
```

## living_rooms：意图展示，暂不过滤

living_rooms 分两层处理：

| 层 | 内容 | 当前行为 |
|----|------|----------|
| 意图反馈层 | 向用户展示"已理解：2厅" | V1 实现 |
| 过滤层 | 按 living_rooms=2 过滤搜索结果 | 暂不实现，等真实数据 |

`IntentField.filterable=False` 时前端渲染为虚线边框 chip，加注"（暂无数据）"。

## Schema 变更

### 新增类型 (`backend/app/schemas/ai_search.py`)

```python
class IntentField(BaseModel):
    field: str
    value: Any
    raw: str
    label: str
    filterable: bool  # False = 已理解但不参与过滤

class UserNeed(BaseModel):
    type: Literal["household_size", "quiet_environment", "lifestyle"]
    value: int | bool | str
    raw: str

class SearchNotice(BaseModel):
    type: Literal["tension", "suggestion"]
    message: str
    related_need_type: str | None = None

class InterpretedNeeds(BaseModel):
    needs: list[UserNeed] = Field(default_factory=list)
    notices: list[SearchNotice] = Field(default_factory=list)
    unresolved: list[str] = Field(default_factory=list)
```

### AiSearchResult 追加字段（optional，不改现有字段）

```python
interpreted_intent: list[IntentField] = Field(default_factory=list)
interpreted_needs: InterpretedNeeds = Field(default_factory=InterpretedNeeds)
```

## Backend 改动

**文件：`backend/app/services/ai_search/service.py`**

### 1. 修复 `_is_property_search`（BUG-026）

函数入口处先做中文数字转换，后续 pattern 匹配全部在转换后的字符串上进行。补充 `厅` pattern。

### 2. 新增 `_extract_living_rooms(query) -> int | None`

确定性 regex 提取，不调 LLM：

```python
_LIVING_ROOM_PATTERN = re.compile(r"(\d+)\s*厅", re.IGNORECASE)

def _extract_living_rooms(query: str) -> int | None:
    normalized = _CHINESE_DIGIT_RE.sub(lambda m: _CHINESE_DIGITS[m.group(0)], query)
    match = _LIVING_ROOM_PATTERN.search(normalized)
    return int(match.group(1)) if match else None
```

### 3. 新增 `_interpret_needs(query, parsed_filters) -> InterpretedNeeds`

独立 LLM 调用，识别场景信号（needs）。LLM 只输出 needs + unresolved，不输出 notices。

System prompt 包含：
- NeedType 枚举（仅 household_size / quiet_environment / lifestyle）
- 6 个 few-shot examples（见下）
- 枚举外的 type 静默丢弃规则

Few-shot examples：

```
Example 1: 纯 filters — {"needs": [], "unresolved": []}
Example 2: 适合老人住，安静一点 — lifestyle + quiet_environment, unresolved: ["不要太远"]
Example 3: 三室两厅 一家四口 — household_size:4, unresolved: []
Example 4: 一室两厅 一家三口 — household_size:3, unresolved: []  ← 核心 case
Example 5: 靠近好学校 — needs: [], unresolved: ["靠近好学校", "周边环境好"]
Example 6: 现在房价会涨吗 — needs: [], unresolved: []
```

### 4. 新增 `_detect_tensions(needs, parsed_filters) -> list[SearchNotice]`

纯 Python，不调 LLM。规则见 `tension-policy.md`。V1 只实现：

```
need.type == "household_size" AND need.value > bedrooms_min + 1
→ SearchNotice(type="tension", message="{n}室对{m}口之家可能偏小")
```

### 5. 更新 `ai_search()` 主流程

在 `_parse_filters` 之后、`_resolve_result_ids` 之前插入 living_rooms 提取和 need interpretation。`_interpret_needs` 调用必须包裹在独立 try/except 中，失败不影响搜索结果。

### 不改动的函数

- `_parse_filters`（及其内部所有子函数）
- `_relax_filters` / `_apply_relaxation`
- `_resolve_result_ids`
- `_generate_summary`
- `_build_match_reasons`
- `_build_parsed_constraints`

## Frontend 改动

**文件：`frontend/types/ai-search.ts`**

```typescript
export interface IntentField { field: string; value: ...; raw: string; label: string; filterable: boolean }
export type NeedType = 'household_size' | 'quiet_environment' | 'lifestyle'
export type NoticeType = 'tension' | 'suggestion'
export interface UserNeed { type: NeedType; value: ...; raw: string }
export interface SearchNotice { type: NoticeType; message: string; related_need_type: string | null }
export interface InterpretedNeeds { needs: UserNeed[]; notices: SearchNotice[]; unresolved: string[] }
```

`AiSearchResult` 追加（optional，与 F26 风格一致）：
```typescript
interpreted_intent?: IntentField[]
interpreted_needs?: InterpretedNeeds
```

**新增：`frontend/components/features/search/interpreted-needs-card.tsx`**

使用 Tailwind class，不依赖 shadcn：
- notices（tension）→ 黄色背景条，⚠️ 图标，amber-50/amber-600
- needs tags → 灰色小标签，显示 raw 原始表达
- unresolved → 浅灰色小字："以下内容暂未用于筛选：xxx"
- `filterable=false` 的 interpreted_intent → 虚线边框 chip，加注"（暂无数据）"
- 全部为空 → 不渲染任何内容，不占位

**修改：`frontend/app/(dashboard)/search/page.tsx`**

在 `ai-parsed-filters-card` 下方、搜索结果上方渲染 `InterpretedNeedsCard`。

## 配套文档

新建 `.ai/features/F27-need-interpretation/tension-policy.md`（由 T01 创建）。

## Constraints

- All implementation must follow `.ai/conventions.md` and `.ai/orchestration.md`.
- Workers must implement only their assigned task.
- `status.json` is updated only by Claude Code orchestration.

## Dependencies

- F26 done（`AiSearchResult` schema 已扩展，`strict_items`/`recommended_items` 在前）

## Required Env Vars

No new env vars.
