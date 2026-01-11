# Journal: Batch Processing Refactor

**Date**: 2026-01-10
**Session**: Evening

## Summary

Refactored all three agents (Engineering, Sourcing, Finance) to process entire BOMs in a single LLM call per step instead of one call per part. This reduced processing time from ~10 minutes to ~3 minutes for a 20-part BOM.

## Goals
- [x] Identify performance bottleneck (69 LLM calls for 23-part BOM)
- [x] Refactor EngineeringAgent for batch processing
- [x] Refactor SourcingAgent for batch processing
- [x] Refactor FinanceAgent for batch processing
- [x] Update BOM flow to use batch evaluation
- [x] Test and verify performance improvement

## Changes Made

### Root Cause Analysis

Initial investigation revealed:
- No explicit LLM model set (defaulting to slower model)
- Memory overhead with SQLite long-term storage per call
- 23 parts × 3 agents = 69 separate LLM calls
- Each call taking ~10 seconds = ~11.5 minutes total

### Phase 1: LLM and Memory Optimization

**`agents/memory_config.py`**
- Added `get_llm()` function returning `gpt-4o-mini`
- Configurable via `CREWAI_MODEL` environment variable
- Removed memory configuration entirely (was adding overhead)
- Moved `FINANCE_POLICIES` here for consistency

**`main.py`**
- Added FastAPI `lifespan` context manager
- Agents now initialize at server startup (primed and ready)
- Prints "Agents initialized with model: gpt-4o-mini"

### Phase 2: Batch Processing

**`agents/engineering.py`**
```python
# Before: Called once per part
def evaluate(self, line_item, project_context, offers_store) -> AgentDecision

# After: Called once for all parts
def evaluate_batch(self, line_items, project_context, offers_store) -> dict[str, AgentDecision]
```
- Builds context for ALL parts in single prompt
- LLM returns JSON array with decision per part
- Parses batch response into dict mapping MPN → decision

**`agents/sourcing.py`**
- Same pattern: `evaluate_batch()` processes all items
- Includes all offers for all parts in prompt
- Returns dict mapping MPN to sourcing decision

**`agents/finance.py`**
- Same pattern: `evaluate_batch()` for all items
- Shows budget overview and running totals
- Returns dict mapping MPN to finance decision

**`flows/bom_flow.py`**
- Each review step calls `evaluate_batch()` once
- Applies returned decisions to all line items in loop
- Added global agent initialization with `initialize_agents()`

## Decisions

### Decision: Batch All Parts in Single LLM Call
**Context**: Processing 23 parts with 3 agents meant 69 LLM calls
**Options Considered**:
1. Optimize per-call overhead (faster model, no memory) - ~50% improvement
2. Batch all parts in single call per agent - ~75% improvement
3. Parallel processing of individual calls - complex, rate limits
**Chosen**: Option 2 (batch processing)
**Rationale**:
- Reduces 69 calls to 3 calls
- LLM can see full context and make consistent decisions
- Simpler implementation than parallelization
- No rate limit concerns

### Decision: Use gpt-4o-mini
**Context**: CrewAI was defaulting to GPT-4 (slow, expensive)
**Options Considered**:
1. GPT-4 (default) - most capable but slow
2. GPT-4o - fast but expensive
3. GPT-4o-mini - fast and cheap
4. Claude models - would need different API key setup
**Chosen**: Option 3 (gpt-4o-mini)
**Rationale**: Good balance of speed and cost for this use case. Can be overridden via `CREWAI_MODEL` env var.

### Decision: Remove Memory Entirely
**Context**: CrewAI memory was adding overhead without clear benefit
**Options Considered**:
1. Keep long-term memory for learning
2. Keep short-term memory only
3. Remove all memory, use only knowledge sources
**Chosen**: Option 3 (no memory)
**Rationale**:
- Memory adds ~2-3 seconds overhead per call
- Knowledge sources provide sufficient context
- No clear benefit to remembering across projects
- Can add back later if needed

## Performance Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| LLM calls (20 parts) | 60 | 3 | 20x fewer |
| Processing time (20 parts) | ~10 min | ~3 min | 3-4x faster |
| Processing time (2 parts) | 53 sec | 27 sec | 2x faster |

## Files Created/Modified

| File | Action | Purpose |
|------|--------|---------|
| `agents/memory_config.py` | MODIFY | Add LLM config, remove memory |
| `agents/engineering.py` | MODIFY | Batch processing |
| `agents/sourcing.py` | MODIFY | Batch processing |
| `agents/finance.py` | MODIFY | Batch processing |
| `flows/bom_flow.py` | MODIFY | Use batch methods, agent init |
| `main.py` | MODIFY | Startup agent initialization |

## Testing

Verified with demo BOM:
```bash
# 20-part BOM completed in ~3 minutes
uv run sourcing process demo/neurolink_bom.csv --intake demo/neurolink_intake.yaml

# All 20 parts reached pending_purchase status
```

## Next Steps
- [ ] Consider adding retry logic for failed JSON parsing
- [ ] Add streaming output to show progress during batch processing
- [ ] Consider chunking very large BOMs (>50 parts) to avoid token limits
- [ ] Add metrics/timing to trace output

## Notes

- The batch prompts ask for JSON array output which works well with gpt-4o-mini
- Default approval/rejection for missing items in response handles edge cases
- Knowledge sources (policies, org knowledge) still work with batch approach
- Could further optimize by running all 3 agents in parallel (but adds complexity)
