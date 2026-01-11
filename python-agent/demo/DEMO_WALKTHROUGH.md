# NeuroLink Mini - BOM Agent Demo Walkthrough

## Project Overview

**Device**: NeuroLink Mini v1.0 - Portable Brain-Computer Interface Signal Acquisition Unit

**Description**: A medical-grade 8-channel neural signal acquisition device for research applications. Uses the Texas Instruments ADS1299 analog front-end with STM32H7 processing, USB-C connectivity with patient isolation, and medical-grade connectors.

**Key Requirements**:
- Medical device compliance (IEC 60601-1, ISO 13485, FDA Class II)
- IPC Class 3 quality (highest reliability)
- Ultra-low noise analog design
- Patient safety isolation
- 50 unit prototype run, $15,000 budget

---

## Prerequisites

Start in a new terminal in the python-agent directory:

```bash
cd /Users/mark/part-sourcing-hackathon/python-agent
```

Make sure you have the API key set:
```bash
export ANTHROPIC_API_KEY=sk-ant-...  # Or use .env file
```

---

## Demo Steps

### Step 1: Start the API Server

Open a terminal and start the service:

```bash
uv run uvicorn bom_agent_service.main:app --reload --port 8000
```

Keep this running. You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

---

### Step 2: Verify System Health

In a new terminal, check the API is running:

```bash
curl http://localhost:8000/health
```

Expected output:
```json
{"status":"healthy"}
```

Check available endpoints:
```bash
curl http://localhost:8000/
```

---

### Step 3: View Current Knowledge Base

Check what suppliers are pre-configured:

```bash
uv run sourcing kb suppliers list
```

Expected output:
```
┌─────────┬──────────┬───────┬─────────┬─────────┬────────┐
│ ID      │ Name     │ Trust │ On-Time │ Quality │ Orders │
├─────────┼──────────┼───────┼─────────┼─────────┼────────┤
│ digikey │ Digi-Key │ high  │     95% │     99% │      0 │
│ mouser  │ Mouser   │ high  │     92% │     98% │      0 │
│ newark  │ Newark   │ high  │     90% │     97% │      0 │
└─────────┴──────────┴───────┴─────────┴─────────┴────────┘
```

Check for any banned parts:
```bash
uv run sourcing kb parts list
```

---

### Step 4: Review the Input Files

**BOM CSV** (`demo/neurolink_bom.csv`):
```bash
cat demo/neurolink_bom.csv
```

Key components:
- U1: ADS1299 - 8-channel neural ADC ($50+)
- U2: STM32H743 - High-performance MCU
- U3/U4: Ultra-low-noise LDOs
- U5: Instrumentation amplifier
- U6: Digital isolator (patient safety)
- J2: Medical-grade connector

**Intake Sheet** (`demo/neurolink_intake.yaml`):
```bash
cat demo/neurolink_intake.yaml
```

Note the strict requirements:
- Medical compliance (IEC 60601-1)
- IPC Class 3 quality
- No brokers allowed
- 21 day max lead time
- Critical parts marked (U1, U2, U3, U5, U6, J2)

---

### Step 5: Process the BOM Through Agent Flow

This is the main event - run the full agent pipeline:

```bash
uv run sourcing process demo/neurolink_bom.csv --intake demo/neurolink_intake.yaml
```

Watch as the agents work through each step:
1. **Intake**: Parse BOM and project context
2. **Enrichment**: Fetch supplier offers (mock data)
3. **Engineering Review**: Check compliance, preferred manufacturers
4. **Sourcing Review**: Evaluate suppliers, lead times, risk
5. **Finance Review**: Budget approval, price optimization

This will take 1-2 minutes as agents reason through each part.

---

### Step 6: Check Project Status

After processing completes, view the project:

```bash
uv run sourcing status
```

This lists all projects. Note the project ID (e.g., `NL-2025-001` or `PRJ-xxx`).

Get detailed status for the project:

```bash
uv run sourcing status NL-2025-001
```

Or use the actual project ID shown.

---

### Step 7: View Execution Trace

See the full agent reasoning chain:

```bash
uv run sourcing trace NL-2025-001
```

This shows each decision with:
- Agent name
- Reasoning (why approved/rejected)
- References (data sources used)
- Timestamps

**Look for interesting decisions**:
- Did critical parts (U1, U2) get extra scrutiny?
- Were any parts rejected for not meeting medical grade?
- Did the engineering notes influence decisions?

---

### Step 8: API Direct Access

You can also query the API directly:

**List all projects:**
```bash
curl -s http://localhost:8000/projects | python3 -m json.tool
```

**Get project details:**
```bash
curl -s http://localhost:8000/projects/NL-2025-001 | python3 -m json.tool
```

**Get trace via API:**
```bash
curl -s http://localhost:8000/projects/NL-2025-001/trace | python3 -m json.tool
```

---

### Step 9: Modify Knowledge Base

Let's say we discover a part has quality issues. Ban it:

```bash
uv run sourcing kb parts ban "GRM188R71H104KA93D" --reason "Received batch with delamination issues"
```

Verify the ban:
```bash
uv run sourcing kb parts show GRM188R71H104KA93D
```

Add an approved alternate:
```bash
uv run sourcing kb parts alternate "GRM188R71H104KA93D" "GRM188R71H104MA93D" --reason "Higher reliability automotive grade"
```

---

### Step 10: Adjust Supplier Trust

Demote a supplier's trust level:

```bash
uv run sourcing kb suppliers trust mouser medium --reason "Recent delivery delays"
```

Verify:
```bash
uv run sourcing kb suppliers show mouser
```

---

### Step 11: Re-process with Updated Knowledge

Process the BOM again to see how knowledge base changes affect decisions:

```bash
uv run sourcing process demo/neurolink_bom.csv --intake demo/neurolink_intake.yaml
```

Compare the new trace with the previous run - parts using the banned capacitor should now show different behavior.

---

### Step 12: Interactive Chat Mode

For ad-hoc questions about parts:

```bash
uv run sourcing chat
```

Try questions like:
- "What are good alternatives to the ADS1299?"
- "What should I look for in medical-grade connectors?"
- "How do I ensure IEC 60601-1 compliance for power supplies?"

Type `quit` to exit.

---

## Understanding Agent Decisions

### Engineering Agent Evaluates:
- Compliance requirements (RoHS, IEC 60601-1, etc.)
- Preferred manufacturers (from intake)
- Critical parts (extra scrutiny)
- Engineering notes (medical-grade, low-noise, etc.)
- Part lifecycle (active, NRND, EOL)

### Sourcing Agent Evaluates:
- Broker policy (no brokers for this project)
- Preferred distributors (DigiKey, Mouser, Newark)
- Lead time limits (21 days max)
- Stock availability
- Supplier trust levels

### Finance Agent Evaluates:
- Budget constraints ($15,000 total)
- Price breaks at quantity
- Total project spend tracking
- Individual line item costs

---

## Cleanup

Stop the API server with Ctrl+C.

Delete test data if desired:
```bash
rm -rf data/*.db
```

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `demo/neurolink_bom.csv` | Sample BOM - 23 line items |
| `demo/neurolink_intake.yaml` | Project requirements |
| `data/projects.db` | Project storage |
| `data/org_knowledge.db` | Parts/supplier knowledge |
| `data/agent_memory/` | CrewAI learning storage |

---

## Troubleshooting

**API not responding:**
```bash
# Check if something else is using port 8000
lsof -i :8000

# Use a different port
uv run uvicorn bom_agent_service.main:app --port 8001
uv run sourcing --api-url http://localhost:8001 status
```

**Agent errors:**
```bash
# Check API key is set
echo $ANTHROPIC_API_KEY

# View server logs in the uvicorn terminal
```

**Reset database:**
```bash
rm data/*.db
# Restart the API server
```
