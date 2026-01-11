# BOM Agent Admin Console

A React-based admin console for managing the BOM (Bill of Materials) Agent API. Provides a web interface to view and manage projects, parts knowledge, suppliers, and API keys.

## Features

- **Dashboard** - Overview of projects, parts, and suppliers counts
- **Projects** - View project list, details, line items, and execution traces
- **Parts Knowledge** - View parts, ban/unban parts, manage approved alternates
- **Suppliers** - View suppliers, create new ones, manage trust levels
- **API Keys** - View and manage API keys (requires API endpoints)

## Tech Stack

- **Frontend**: Vite + React + TypeScript
- **Styling**: Tailwind CSS v4 + shadcn/ui components
- **Backend**: Express.js (local dev) / Vercel Functions (production)
- **Auth**: JWT cookie-based sessions with env var credentials

## Prerequisites

- Node.js 18+
- Python BOM Agent API running (default: http://localhost:8000)
- Admin API key with `admin` scope from the Python API

## Quick Start

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start the development servers**
   ```bash
   # Terminal 1: Start Express backend
   npm run server

   # Terminal 2: Start Vite frontend
   npm run dev
   ```

4. **Open the app**

   Navigate to http://localhost:5173 and login with your admin credentials (default: admin/admin).

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ADMIN_USER` | Admin login username | `admin` |
| `ADMIN_PASSWORD` | Admin login password | `changeme` |
| `JWT_SECRET` | Secret for signing JWT tokens | `dev-secret` |
| `PYTHON_API_URL` | URL of the Python BOM Agent API | `http://localhost:8000` |
| `ADMIN_API_KEY` | API key with admin scope for Python API | (required) |
| `PORT` | Express server port | `3001` |

## Creating an Admin API Key

Before using the admin console, create an API key with admin scope:

```bash
cd ../python-agent

# Create a client for the admin console
uv run sourcing client create --name "Admin Console" --slug "admin-console"
# Note the client_id from output

# Create an API key with admin scope
uv run sourcing apikey create --client-id <client_id> --name "admin-key" --scopes "admin,all"
# Copy the API key (pbom_sk_xxx) - shown only once!
```

Add this key to your `.env` as `ADMIN_API_KEY`.

## Project Structure

```
admin-console/
├── server/                 # Express backend (local dev)
│   ├── index.ts           # Express app entry
│   ├── routes/
│   │   ├── auth.ts        # /api/auth/* routes (login/logout/me)
│   │   └── proxy.ts       # /api/proxy/* routes (forwards to Python API)
│   └── middleware/
│       └── auth.ts        # JWT verification middleware
├── src/                    # React frontend
│   ├── components/
│   │   ├── ui/            # shadcn/ui components
│   │   ├── layout/        # AppLayout, Sidebar, Header
│   │   └── shared/        # DataTable, ConfirmDialog
│   ├── pages/             # Page components
│   ├── lib/
│   │   ├── api-client.ts  # Typed API client
│   │   └── utils.ts       # Utilities
│   ├── context/
│   │   └── AuthContext.tsx # Auth state management
│   └── types/             # TypeScript types
├── api/                    # Vercel serverless functions
└── vercel.json            # Vercel configuration
```

## Available Scripts

- `npm run dev` - Start Vite dev server (frontend)
- `npm run server` - Start Express backend with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Authentication Flow

1. User visits `/login` and enters username/password
2. Express validates credentials against `ADMIN_USER`/`ADMIN_PASSWORD` env vars
3. On success, JWT token is set as HttpOnly cookie (8hr expiry)
4. Protected routes check cookie via `/api/auth/me`
5. All API requests proxy through `/api/proxy/*` with `ADMIN_API_KEY`

## API Proxy

The admin console doesn't expose the Python API key to the browser. Instead:

1. Browser makes request to `/api/proxy/projects`
2. Express middleware validates JWT cookie
3. Express forwards request to Python API with `X-API-Key` header
4. Response is returned to browser

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for Vercel deployment instructions.

## License

MIT
