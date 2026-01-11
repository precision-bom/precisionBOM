# Admin Console Development Journal

## 2026-01-11: Initial Implementation

### Summary
Built a React-based admin console for the BOM Agent API, providing a web interface to manage projects, parts knowledge, suppliers, and API keys.

### Tech Stack Decisions

**Frontend: Vite + React + TypeScript**
- Chose Vite for fast HMR and modern build tooling
- TypeScript for type safety across the API client
- Tailwind CSS v4 with shadcn/ui for consistent, accessible components

**Backend: Express.js (local) / Vercel Functions (production)**
- Express.js for local development with hot reload via tsx
- Structured to easily convert to Vercel serverless functions
- Single codebase supports both deployment targets

**Authentication: JWT Cookie + Environment Variables**
- Initially considered SQLite-backed user database
- Simplified to env var credentials (ADMIN_USER/ADMIN_PASSWORD) for hackathon scope
- JWT stored in HttpOnly cookie for security (not exposed to JavaScript)
- 8-hour session expiry

### Architecture Decisions

**API Proxy Pattern**
- Browser never sees the Python API key
- All `/api/proxy/*` requests authenticated via JWT cookie
- Express/Vercel adds `X-API-Key` header before forwarding to Python API
- Decouples frontend auth from backend API auth

**Why not direct API calls?**
- CORS complexity with credentials
- API key exposure in browser network tab
- Can't revoke browser-held keys easily

### Challenges & Solutions

**1. ES Module Loading Order**
- Problem: Environment variables read at module load time, before `dotenv.config()`
- Symptom: Login always failed with "Invalid credentials"
- Solution: Read env vars inside functions, not at module scope

```typescript
// Before (broken)
const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret'

// After (working)
function getEnv() {
  return { JWT_SECRET: process.env.JWT_SECRET || 'dev-secret' }
}
```

**2. Express 5 Wildcard Routes**
- Problem: `/*` route syntax removed in Express 5
- Symptom: `PathError: Missing parameter name at index 2: /*`
- Solution: Use named wildcard `/*splat` and `req.path` for full path

```typescript
// Express 5 requires named wildcards
router.all('/*splat', async (req, res) => {
  const path = req.path.slice(1) // Use req.path, not req.params.splat
})
```

**3. Cookie Not Sent**
- Problem: Fetch calls didn't include cookies
- Symptom: 401 on every request after login
- Solution: Add `credentials: 'include'` to all fetch calls

**4. SameSite Cookie Issues**
- Problem: `SameSite=Strict` blocked cookies during navigation
- Symptom: Redirect loops after login
- Solution: Changed to `SameSite=Lax`

### Features Implemented

- [x] Login page with username/password auth
- [x] Dashboard with entity counts
- [x] Projects list with status badges
- [x] Project detail view with line items and trace
- [x] Parts list with ban/unban actions
- [x] Add approved alternates to parts
- [x] Suppliers list with trust level management
- [x] Create new suppliers
- [x] API Keys page (ready for backend endpoints)
- [x] Responsive sidebar navigation
- [x] Logout functionality

### Files Created

```
admin-console/
├── server/
│   ├── index.ts              # Express entry point
│   ├── routes/auth.ts        # Login/logout/me endpoints
│   ├── routes/proxy.ts       # Python API proxy
│   └── middleware/auth.ts    # JWT verification
├── src/
│   ├── context/AuthContext.tsx
│   ├── lib/api-client.ts     # Typed API client
│   ├── pages/*.tsx           # All page components
│   └── components/...        # UI components
├── api/                      # Vercel serverless functions
│   ├── auth/*.ts
│   └── proxy/[...path].ts
├── vercel.json
├── README.md
├── DEPLOYMENT.md
└── .env.example
```

### Next Steps

1. Add API key management endpoints to Python API
2. Implement client management UI
3. Add search/filter to lists
4. Add pagination for large datasets
5. Consider adding activity logs/audit trail

### Time Spent
~3 hours for full implementation including debugging auth issues
