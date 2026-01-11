# Submission Checklist

## Required Deliverables

### 1. Pitch Video (3-5 minutes)
- [ ] Record screen + voiceover demo
- [ ] Upload to YouTube/Vimeo/Google Drive
- [ ] Get shareable link
- [ ] Upload link to Milgram under "Additional Information"

**Video Content**:
- [ ] Title slide (10 sec)
- [ ] Problem statement (30 sec)
- [ ] Solution overview (30 sec)
- [ ] Architecture diagram (20 sec)
- [ ] Live demo (60-90 sec)
- [ ] Tech stack (20 sec)
- [ ] Market opportunity (30 sec)
- [ ] Team & ask (20 sec)

### 2. Live Website OR GitHub Repository
- [ ] Option A: Deploy to Vercel (https://precisionbom.vercel.app)
- [ ] Option B: GitHub repo public (https://github.com/youruser/precisionbom)
- [ ] Ensure demo is functional
- [ ] Add README with setup instructions

### 3. Milgram Submission Form
- [ ] Category: Hardware and Physical Products, AI for Manufacturing, AI Agents and MCP Systems, Open Innovation
- [ ] Project Title: precisionBOM
- [ ] Project Summary: Already entered
- [ ] Project Duration: Jan 10-11, 2026
- [ ] Images: Upload 2-4 screenshots
- [ ] Additional Info: Pitch video link

### 4. Screenshots (2-4 images)
- [ ] Landing page hero section
- [ ] BOM upload interface
- [ ] Agent processing/trace view
- [ ] Optimization results with strategies

---

## Pre-Submission Testing

### Frontend (Next.js)
```bash
cd nextjs-app
npm run build    # Ensure no build errors
npm run start    # Test production build locally
```

### Backend (Python)
```bash
cd python-agent
uv run uvicorn bom_agent_service.main:app --port 8000
curl http://localhost:8000/health  # Should return {"status":"healthy"}
```

### End-to-End Flow
1. [ ] User can sign up / login
2. [ ] User can upload BOM CSV
3. [ ] System processes BOM through agents
4. [ ] User sees optimization strategies
5. [ ] Blockchain audit trail works (or mock for demo)

---

## Recording Setup

### Screen Recording
- Use QuickTime (Mac) or OBS
- Resolution: 1920x1080 preferred
- Audio: Clear mic, no background noise
- Browser: Chrome with clean profile (no personal tabs)

### Demo Account
- Create a demo user: demo@precisionbom.com
- Pre-upload sample BOM for smooth demo
- Clear browser console/network tabs

### Script Timing
| Section | Duration | Cumulative |
|---------|----------|------------|
| Title | 10s | 0:10 |
| Problem | 30s | 0:40 |
| Solution | 30s | 1:10 |
| Architecture | 20s | 1:30 |
| Demo | 90s | 3:00 |
| Tech stack | 20s | 3:20 |
| Market | 30s | 3:50 |
| Ask | 20s | 4:10 |

**Target**: 4 minutes (leave buffer for 5 min max)

---

## Submission URLs

- **Milgram**: https://milgram.com (event submission platform)
- **GitHub**: https://github.com/[your-repo]
- **Live Site**: https://precisionbom.vercel.app
- **Video**: [Upload and paste link here]

---

## Emergency Contacts

- Hackathon Organizer (Mcrich): Discord #issues channel
- CrewAI Support (Colin): Discord #issues channel
- Rilo Support (Georgi): DM on Discord

---

## Post-Submission

- [ ] Prepare for live demo (same as video but interactive)
- [ ] Have backup plan if live demo fails (show video)
- [ ] Bring laptop charger
- [ ] Test on venue WiFi if possible
- [ ] Know your pitch cold - no reading from notes
