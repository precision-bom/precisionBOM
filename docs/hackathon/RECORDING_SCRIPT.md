# Video Recording Script

## Recording Setup

### Equipment
- **Screen**: 1920x1080 or higher resolution
- **Mic**: External mic preferred (AirPods work, laptop mic is last resort)
- **Recording**: QuickTime (Mac) or OBS (cross-platform)
- **Browser**: Chrome in guest mode (clean, no personal bookmarks)

### Before Recording
```bash
# Start services
cd /Users/jacob/fun/precision-bom/precisionBOM/python-agent
uv run uvicorn bom_agent_service.main:app --port 8000 &

cd /Users/jacob/fun/precision-bom/precisionBOM/nextjs-app
npm run dev &

# Verify
curl http://localhost:8000/health
open http://localhost:3000
```

### Browser Prep
- [ ] Close all other apps
- [ ] Disable notifications (Do Not Disturb)
- [ ] Hide bookmark bar
- [ ] Set zoom to 100%
- [ ] Clear browser console
- [ ] Open app in guest/incognito mode

---

## Full Script (4 minutes)

### [0:00 - 0:10] Title Card

**[SHOW]**: Title slide or landing page

**[SAY]**:
> "Hi, I'm Jacob from PrecisionBOM. We're building AI agents that transform hardware sourcing from a 40-hour nightmare into a 4-minute workflow."

---

### [0:10 - 0:40] The Problem

**[SHOW]**: Stay on landing page or show problem slide

**[SAY]**:
> "If you've ever built hardware, you know the pain. Engineers spend over 40 hours per project just sourcing components. You're juggling DigiKey, Mouser, Octopart - comparing prices, checking stock, verifying compliance.
>
> The chip shortage showed us that supply chains break - $500 billion in economic impact. And for regulated industries like medical devices, you need audit trails for every sourcing decision.
>
> There's no single tool that combines technical specs, supply chain risk, and budget optimization. Until now."

---

### [0:40 - 1:10] The Solution

**[SHOW]**: Solution overview or architecture diagram

**[SAY]**:
> "PrecisionBOM changes this. Upload your bill of materials, and three AI agents analyze it in parallel.
>
> The Engineering agent validates specs and compliance - RoHS, IEC 60601, IPC class requirements. The Sourcing agent evaluates supply chain risk - lead times, stock levels, supplier reliability. The Finance agent optimizes for your budget.
>
> A Final Decision agent synthesizes everything into ranked sourcing strategies. And we record every decision to an Ethereum blockchain for audit compliance.
>
> What took 40 hours now takes 4 minutes."

---

### [1:10 - 1:30] Architecture

**[SHOW]**: Architecture diagram (from PITCH_DECK.md)

**[SAY]**:
> "Here's how it works technically. Your BOM uploads, we query real-time data from DigiKey, Mouser, and Octopart in parallel.
>
> Three specialized agents built with CrewAI analyze the data concurrently - Engineering, Sourcing, and Finance. Each uses Pydantic structured outputs for reliable, typed responses.
>
> The Final Decision agent synthesizes their analysis into ranked strategies, and everything gets recorded to Ethereum using ERC-7827 for immutable audit trails."

---

### [1:30 - 3:00] Live Demo

**[SHOW]**: Switch to browser with app open

**[SAY]**:
> "Let me show you this in action."

**[ACTION]**: Show landing page briefly (5 sec)

**[SAY]**:
> "This is PrecisionBOM. I'll log in."

**[ACTION]**: Login as demo user (5 sec)

**[SAY]**:
> "Here's my dashboard. Let's upload a BOM for a medical device - the NeuroLink Mini brain-computer interface."

**[ACTION]**: Click upload, select sample_bom.csv (10 sec)

**[SAY]**:
> "11 components - precision analog chips, microcontrollers, medical-grade connectors. The system parses everything automatically."

**[ACTION]**: Start processing (click Analyze)

**[SAY]**:
> "Now the three agents analyze in parallel. Watch the trace..."

**[SHOW]**: Agent processing view (30 sec)

**[SAY]**:
> "Engineering agent is checking IEC 60601 compliance for medical devices. Sourcing agent evaluates supply chain risk. Finance agent works within our $15,000 prototype budget.
>
> The ADS1299 neural ADC is marked critical, so it gets extra scrutiny."

**[ACTION]**: Wait for completion, show results

**[SAY]**:
> "Here are the optimization strategies."

**[SHOW]**: Results view (20 sec)

**[SAY]**:
> "Strategy 1 optimizes for cost - $12,400 total. Strategy 2 prioritizes lead time - everything ships in 7 days. Strategy 3 consolidates to two distributors for simpler logistics.
>
> Each shows exactly which parts from which suppliers, with real-time pricing."

**[ACTION]**: Show blockchain/audit view if available (10 sec)

**[SAY]**:
> "Every decision is recorded to Ethereum for the audit trail medical device companies need."

---

### [3:00 - 3:20] Tech Stack

**[SHOW]**: Tech stack slide or back to landing page

**[SAY]**:
> "Built this weekend with Next.js and React on the frontend, CrewAI for multi-agent orchestration, FastAPI backend, Neon Postgres database, and Ethereum for the audit trail. 45 passing tests. Real supplier API integrations."

---

### [3:20 - 3:50] Market Opportunity

**[SHOW]**: Market slide

**[SAY]**:
> "The electronic components distribution market is over $50 billion. Our targets are hardware startups, contract manufacturers, and regulated industries.
>
> Current tools like Arena are manual. Octopart is search-only. We're the first AI-native solution with multi-agent optimization and blockchain audit trails.
>
> SaaS model starting at $99 per month, plus a percentage of the savings we generate."

---

### [3:50 - 4:10] The Ask

**[SHOW]**: Contact/ask slide

**[SAY]**:
> "We're looking for three things. First, pilot customers - hardware startups or medical device companies who want to try our beta. Second, seed investment to expand API integrations. Third, introductions to contract manufacturers and hardware accelerators.
>
> If you know anyone building hardware, I'd love to talk. I'm Jacob - jacob@precisionbom.com.
>
> Thank you!"

---

## Recording Tips

### Voice
- Speak slowly and clearly
- Pause between sections
- Sound confident, not rushed
- If you mess up, pause and restart that section (can edit later)

### Screen
- Move cursor slowly and deliberately
- Don't click too fast
- Give UI time to load before speaking
- Keep mouse visible when pointing at things

### Editing (if needed)
- Cut obvious mistakes
- Don't over-edit (authenticity > polish)
- Keep total under 5 minutes
- Add subtle background music if desired (optional)

### Backup Plan
If live demo breaks during recording:
1. Use pre-processed project results
2. Show CLI demo instead
3. Walk through screenshots

---

## Export & Upload

### Export Settings
- Format: MP4 (H.264)
- Resolution: 1920x1080
- Frame rate: 30fps
- Audio: AAC

### Upload Options
1. **YouTube** (unlisted) - most reliable
2. **Vimeo** - professional look
3. **Google Drive** - easy sharing
4. **Loom** - quick upload

### Verify Before Submission
- [ ] Video plays without issues
- [ ] Audio is clear and audible
- [ ] Link works in incognito mode
- [ ] Total time under 5 minutes

---

## Video Checklist

- [ ] Services running before recording
- [ ] Demo data prepared
- [ ] Browser clean and zoomed correctly
- [ ] Mic tested
- [ ] Script printed/visible
- [ ] Record full take
- [ ] Watch playback, note issues
- [ ] Re-record if needed
- [ ] Export
- [ ] Upload
- [ ] Test link
- [ ] Submit to Milgram
