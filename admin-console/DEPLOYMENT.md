# Vercel Deployment Guide

This guide covers deploying the BOM Agent Admin Console to Vercel.

## Prerequisites

1. A Vercel account (https://vercel.com)
2. Vercel CLI installed: `npm i -g vercel`
3. Your Python BOM Agent API deployed and accessible via HTTPS
4. An admin API key with `admin` scope

## Quick Deploy

### Option 1: Deploy via Vercel Dashboard

1. Push your code to GitHub/GitLab/Bitbucket
2. Go to [Vercel Dashboard](https://vercel.com/dashboard)
3. Click "Add New Project"
4. Import your repository
5. Configure the project:
   - Framework Preset: Vite
   - Root Directory: `admin-console` (if in a monorepo)
   - Build Command: `npm run build`
   - Output Directory: `dist`
6. Add environment variables (see below)
7. Click "Deploy"

### Option 2: Deploy via CLI

```bash
# Login to Vercel
vercel login

# Deploy (will prompt for project settings)
vercel

# For production deployment
vercel --prod
```

## Environment Variables

Set these in the Vercel dashboard under Project Settings > Environment Variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `ADMIN_USER` | Admin login username | Yes |
| `ADMIN_PASSWORD` | Admin login password (use a strong password!) | Yes |
| `JWT_SECRET` | Random secret for JWT signing (32+ chars) | Yes |
| `PYTHON_API_URL` | Full URL of your Python API (e.g., `https://api.example.com`) | Yes |
| `ADMIN_API_KEY` | API key with admin scope | Yes |

### Generating a JWT Secret

```bash
# Generate a secure random secret
openssl rand -base64 32
```

## Project Structure for Vercel

```
admin-console/
├── api/                    # Vercel serverless functions
│   ├── auth/
│   │   ├── login.ts       # POST /api/auth/login
│   │   ├── logout.ts      # POST /api/auth/logout
│   │   └── me.ts          # GET /api/auth/me
│   └── proxy/
│       └── [...path].ts   # ALL /api/proxy/* -> Python API
├── dist/                   # Built frontend (created by build)
├── vercel.json            # Vercel configuration
└── ...
```

## How It Works

1. **Frontend**: Vite builds the React app to `dist/`
2. **API Routes**: Files in `api/` become serverless functions
3. **Routing**: `vercel.json` configures:
   - `/api/*` routes to serverless functions
   - All other routes serve the SPA (for client-side routing)

## Security Considerations

1. **Use HTTPS**: Vercel provides HTTPS by default
2. **Strong Passwords**: Use a strong `ADMIN_PASSWORD` in production
3. **JWT Secret**: Generate a unique, random `JWT_SECRET`
4. **API Key Security**: The `ADMIN_API_KEY` is never exposed to the browser
5. **Environment Variables**: Never commit secrets to git

## Custom Domain

1. Go to Project Settings > Domains
2. Add your custom domain
3. Configure DNS as instructed
4. Vercel will automatically provision SSL

## Troubleshooting

### "ADMIN_API_KEY not configured"
- Ensure the environment variable is set in Vercel dashboard
- Redeploy after adding environment variables

### 401 Unauthorized on API calls
- Check that `PYTHON_API_URL` is correct and accessible
- Verify the `ADMIN_API_KEY` has `admin` scope
- Ensure the Python API is running and accepts the key

### Login not working
- Verify `ADMIN_USER` and `ADMIN_PASSWORD` are set
- Check browser console for errors
- Ensure cookies are enabled

### SPA routes returning 404
- Verify `vercel.json` has the correct rewrite rules
- Check that the build output is in `dist/`

## Updating

To update the deployed app:

```bash
# Push changes to your repository (if using Git integration)
git push

# Or deploy manually
vercel --prod
```

## Local Testing of Vercel Functions

```bash
# Install Vercel CLI
npm i -g vercel

# Run locally with Vercel dev server
vercel dev
```

This runs the serverless functions locally with the same environment as production.
