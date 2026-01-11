# Team Runbook - Hackathon Day 2

## Timeline Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  SUNDAY JAN 11, 2026 - FINAL DAY                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  11:00 AM   Morning Standup - report progress                   │
│      │                                                          │
│      ▼                                                          │
│  11:30 AM   BUILD SPRINT 3 - Final execution                    │
│      │      • Polish demo flow                                  │
│      │      • Fix critical bugs                                 │
│      │      • Test end-to-end                                   │
│      │                                                          │
│      ▼                                                          │
│  1:30 PM    Pitch Clinic - Practice and feedback                │
│      │                                                          │
│      ▼                                                          │
│  2:30 PM    Final Office Hours - Last help                      │
│      │                                                          │
│      ▼                                                          │
│  3:00 PM    *** SUBMISSION DEADLINE ***                         │
│      │      Upload video to Milgram                             │
│      │                                                          │
│      ▼                                                          │
│  4:00 PM    FINAL DEMOS - Live presentations                    │
│      │                                                          │
│      ▼                                                          │
│  6:00 PM    Judging & Awards                                    │
│      │                                                          │
│      ▼                                                          │
│  7:00 PM    Networking & Next Steps                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Role Assignments

### LEAD ENGINEER (Jacob)
**Primary**: Demo, architecture, technical pitch

**Morning (11:00 AM - 1:30 PM)**:
- [ ] Verify all services running (Python API, Next.js)
- [ ] Run through demo flow 3 times
- [ ] Fix any bugs that break demo
- [ ] Prepare backup CLI demo

**Afternoon (1:30 PM - 4:00 PM)**:
- [ ] Practice pitch at clinic (1:30 PM)
- [ ] Record final video if not done
- [ ] Submit to Milgram by 3:00 PM
- [ ] Prepare for live demo

**Demo Responsibilities**:
- Run the live demo
- Answer technical questions
- Explain architecture

---

### SALES/PRESENTER (If you have a teammate)
**Primary**: Pitch delivery, networking, business questions

**Morning (11:00 AM - 1:30 PM)**:
- [ ] Memorize pitch deck (see PITCH_DECK.md)
- [ ] Practice 5-minute pitch 3 times
- [ ] Prepare Q&A answers (see TALKING_POINTS.md)
- [ ] Talk to 3 potential customers

**Afternoon (1:30 PM - 4:00 PM)**:
- [ ] Get feedback at pitch clinic
- [ ] Refine pitch based on feedback
- [ ] Network with judges before demo

**Demo Responsibilities**:
- Deliver the pitch
- Handle business questions
- Collect contact info from interested people

---

### DESIGNER/POLISH (If you have a teammate)
**Primary**: Screenshots, video, visuals

**Morning (11:00 AM - 1:30 PM)**:
- [ ] Take 4 high-quality screenshots
- [ ] Record pitch video (see RECORDING_SCRIPT.md)
- [ ] Edit video if needed
- [ ] Upload video to shareable link

**Afternoon (1:30 PM - 4:00 PM)**:
- [ ] Upload screenshots to Milgram
- [ ] Ensure video link works
- [ ] Submit by 3:00 PM

**Demo Responsibilities**:
- Screen share management
- Backup slides ready
- Record live demo for posterity

---

## Hour-by-Hour Schedule

### 11:00 AM - Morning Standup
**Location**: Main room
**Action**:
- Report what you built yesterday
- State today's goals
- Identify any blockers

**Script**: "Yesterday we built a full multi-agent BOM optimization system with DigiKey integration and blockchain audit. Today we're polishing the demo and recording our pitch video. No blockers."

---

### 11:00 AM - 1:30 PM - Build Sprint 3

**Priority 1: Demo Works End-to-End**
```bash
# Test full flow
cd python-agent
uv run uvicorn bom_agent_service.main:app --port 8000 &
cd ../nextjs-app
npm run dev &

# Test API
curl http://localhost:8000/health

# Test frontend
open http://localhost:3000
```

**Priority 2: Record Video (if not done)**
See RECORDING_SCRIPT.md

**Priority 3: Screenshots**
Take these screenshots:
1. Landing page (full hero)
2. BOM upload interface
3. Agent processing trace
4. Optimization results

---

### 1:30 PM - Pitch Clinic

**What to do**:
- Sign up for a slot
- Deliver full 4-minute pitch
- Get feedback from mentors
- Note what to improve

**Questions to ask mentors**:
- "What's unclear about our value prop?"
- "Which track are we strongest in?"
- "Any suggestions for the demo flow?"

---

### 2:30 PM - Final Office Hours

**Only go if**:
- Critical bug you can't fix
- Submission platform issues
- Need last-minute API credits

---

### 3:00 PM - SUBMISSION DEADLINE

**Checklist**:
- [ ] Video uploaded (YouTube/Vimeo/Drive)
- [ ] Video link works (test in incognito)
- [ ] Milgram form complete
- [ ] Screenshots uploaded
- [ ] GitHub/live site accessible

**Milgram Fields**:
- Project Title: precisionBOM
- Summary: [already entered]
- Categories: Hardware, AI Manufacturing, AI Agents, Open Innovation
- Additional Info: [paste video link]
- Images: [upload 4 screenshots]

---

### 4:00 PM - Final Demos

**Setup (3:45 PM)**:
- Plug in laptop
- Test projector/screen
- Open all demo tabs
- Close Slack/notifications
- Set Do Not Disturb

**During Demo**:
- Speak slowly and clearly
- Make eye contact with judges
- If demo breaks, pivot to slides/CLI
- Time yourself - stop at 5 minutes

**Order**:
- Title (10 sec)
- Problem (30 sec)
- Solution (30 sec)
- Architecture (20 sec)
- Live demo (90 sec)
- Tech/market (50 sec)
- Ask (20 sec)

---

### 6:00 PM - Judging & Awards

**While waiting**:
- Talk to other teams
- Exchange contacts
- Note interesting projects

**If you win**:
- Thank organizers and sponsors
- Mention track category
- Keep it short (30 seconds)

**If you don't win**:
- Congratulate winners
- Ask judges for feedback
- Network with judges afterward

---

## Emergency Procedures

### Demo Crashes During Presentation

**Plan A**: Restart demo (10 seconds)
```bash
# Quick restart
cd python-agent && uv run uvicorn bom_agent_service.main:app --port 8000
```

**Plan B**: Switch to CLI demo
```bash
uv run sourcing process sample_bom.csv --intake project_intake.yaml
uv run sourcing status
uv run sourcing trace [PROJECT_ID]
```

**Plan C**: Show pre-recorded video
- Have video ready to play
- Say: "Let me show you the recorded demo since we hit a technical issue"

---

### Can't Submit to Milgram

1. Screenshot your submission form
2. Email organizers: [organizer email]
3. DM @Mcrich on Discord
4. Timestamp your video upload to prove timing

---

### API Credits Run Out

- Use mock data mode
- Demo shows the flow, not real API calls
- Say: "We have DigiKey integration but using sample data for demo stability"

---

## Contact Info

**Team**:
- Jacob: +1.469.968.9490 / Discord: jacob

**Organizers**:
- Mcrich: Discord #issues
- Ashley K: Discord #issues

**Sponsors**:
- CrewAI (Colin): Discord
- Rilo (Georgi): Discord DM

---

## Post-Hackathon

### Immediately After (7:00 PM)
- [ ] Exchange contacts with 5 people
- [ ] Take team photo
- [ ] Post on LinkedIn/Twitter

### Monday
- [ ] Follow up with all contacts
- [ ] Send thank you to organizers
- [ ] Debrief: what worked, what didn't

### This Week
- [ ] Follow up with any investor interest
- [ ] Schedule pilot calls with potential customers
- [ ] Write blog post about the build
