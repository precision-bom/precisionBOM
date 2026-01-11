# Journal: Interactive Demo Script for NeuroLink Mini

**Date**: 2026-01-10
**Session**: Afternoon

## Summary

Created an interactive demo script showcasing the BOM Agent system using a fictional biomedical device (NeuroLink Mini - portable brain-computer interface). The demo walks through all system functionality with explanations, API calls shown, and pauses for user input at each step.

## Goals
- [x] Create realistic sample BOM for frontier tech device
- [x] Create project intake YAML with medical device requirements
- [x] Build interactive demo script with step-by-step explanations
- [x] Add simple server startup script

## Changes Made

### Demo Files Created

**`demo/neurolink_bom.csv`**
- 23-component BOM for neural signal acquisition device
- Key ICs: ADS1299 (neural ADC), STM32H743 (MCU), INA333 (instrumentation amp)
- Medical-grade components: digital isolator, Harwin connectors
- Mix of passives: Murata capacitors, Yageo/Panasonic resistors, KEMET tantalums

**`demo/neurolink_intake.yaml`**
- Medical device compliance: IEC 60601-1, ISO 13485, FDA Class II
- IPC Class 3 quality (highest reliability tier)
- Strict constraints: no brokers, 21-day lead time, $15K budget for 50 units
- 6 critical parts marked for extra agent scrutiny
- Engineering notes emphasizing low-noise design, patient safety isolation

**`demo/run_demo.sh`**
- 11-step interactive walkthrough
- Each step includes:
  - Banner with step title
  - `📖 Explanation` of what's happening
  - `API Call:` showing the HTTP endpoint
  - `Command:` showing the CLI command
  - `Output:` with bordered command results
  - `Press Enter to continue...` pause
- Covers: architecture, health check, knowledge base, BOM processing, trace viewing, knowledge modification, supplier trust, direct API access
- Colored output with visual hierarchy (banners, sections, dim text)

**`demo/DEMO_WALKTHROUGH.md`**
- Manual reference guide with all commands
- Can be followed without running the script

### Server Script

**`src/bom_agent_service/server.py`** (NEW)
```python
def main():
    uvicorn.run(
        "bom_agent_service.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
```

**`pyproject.toml`** (MODIFIED)
- Added `sourcing-server` script entry point
- Server now starts with: `uv run sourcing-server`

## Decisions

### Decision: Use Biomedical/BCI Device for Demo
**Context**: Needed a compelling sample project to demonstrate the system
**Options Considered**:
1. Generic electronics (boring, doesn't showcase medical compliance)
2. Consumer IoT device (already had one in sample_bom.csv)
3. Biomedical BCI device (frontier tech, strict requirements)
**Chosen**: Option 3 (BCI device)
**Rationale**:
- Medical compliance requirements (IEC 60601-1) exercise the engineering agent's compliance checking
- Critical parts (neural ADC, isolators) demonstrate the critical parts feature
- High-value components test budget tracking
- "No brokers" policy tests sourcing constraints
- Makes for a more interesting demo narrative

### Decision: Interactive Script vs. Non-Interactive
**Context**: How should the demo script behave?
**Options Considered**:
1. Run everything automatically with delays
2. Pause at each step for user input
3. Mix of both (auto for quick parts, pause for important)
**Chosen**: Option 2 (pause at every step)
**Rationale**: User explicitly requested step-by-step walkthrough with ability to examine each part before continuing. Educational value is higher when user controls the pace.

### Decision: Show Both API and CLI Commands
**Context**: What level of detail to show in demo?
**Options Considered**:
1. Just show CLI commands (simpler)
2. Show both API endpoints and CLI commands (educational)
**Chosen**: Option 2 (show both)
**Rationale**: Demonstrates that CLI is a thin wrapper over REST API. Helps users understand they can integrate with the API directly from other tools/UIs.

## Files Created/Modified

| File | Action | Lines |
|------|--------|-------|
| `demo/neurolink_bom.csv` | CREATE | 24 |
| `demo/neurolink_intake.yaml` | CREATE | 65 |
| `demo/run_demo.sh` | CREATE | 502 |
| `demo/DEMO_WALKTHROUGH.md` | CREATE | 280 |
| `src/bom_agent_service/server.py` | CREATE | 15 |
| `pyproject.toml` | MODIFY | +1 line |

## Demo Flow

```
Step 1:  System Architecture      → ASCII diagram of layers
Step 2:  API Health Check         → /health endpoint
Step 3:  Knowledge - Suppliers    → Trust levels, metrics
Step 4:  Knowledge - Parts        → Banned parts, alternates
Step 5:  The Project              → NeuroLink Mini overview
Step 6:  Agent Pipeline           → Process BOM (1-2 min)
Step 7:  View Results             → Project status
Step 8:  Agent Reasoning Trace    → Full audit trail
Step 9:  Modify Knowledge         → Ban part, add alternate
Step 10: Supplier Trust           → Adjust trust level
Step 11: Direct API Access        → Raw JSON endpoints
```

## Testing

Verified demo script runs correctly:
- Server starts with `uv run sourcing-server`
- All CLI commands execute properly
- API endpoints respond correctly
- Script pauses at each step as expected

## Next Steps
- [ ] Run full demo end-to-end and capture output for documentation
- [ ] Consider adding demo for chat mode
- [ ] Could add a "quick demo" mode that skips pauses

## Notes

- The NeuroLink Mini is fictional but uses real part numbers (ADS1299, STM32H7, etc.)
- Medical compliance requirements in the intake are realistic for a Class II device
- Demo takes approximately 10-15 minutes to run through completely (including agent processing time)
- The script gracefully handles the case where project ID needs to be extracted from API response
