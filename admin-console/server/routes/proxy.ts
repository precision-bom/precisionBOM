import { Router } from 'express'
import type { Response } from 'express'
import { requireAuth, type AuthRequest } from '../middleware/auth.js'

const router = Router()

function getEnv() {
  return {
    PYTHON_API_URL: process.env.PYTHON_API_URL || 'http://localhost:8000',
    ADMIN_API_KEY: process.env.ADMIN_API_KEY || '',
  }
}

// Apply auth middleware to all proxy routes
router.use(requireAuth)

// Proxy all requests to Python API
router.all('/*splat', async (req: AuthRequest, res: Response) => {
  const { PYTHON_API_URL, ADMIN_API_KEY } = getEnv()
  // Use req.path to get full path (req.params.splat only gets first segment in Express 5)
  const path = req.path.startsWith('/') ? req.path.slice(1) : req.path
  const queryString = req.url.includes('?') ? req.url.slice(req.url.indexOf('?')) : ''
  const targetUrl = `${PYTHON_API_URL}/${path}${queryString}`

  if (!ADMIN_API_KEY) {
    res.status(500).json({ error: 'ADMIN_API_KEY not configured' })
    return
  }

  try {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'X-API-Key': ADMIN_API_KEY,
    }

    const fetchOptions: RequestInit = {
      method: req.method,
      headers,
    }

    if (req.method !== 'GET' && req.method !== 'HEAD' && req.body) {
      fetchOptions.body = JSON.stringify(req.body)
    }

    const response = await fetch(targetUrl, fetchOptions)

    // Handle non-JSON responses
    const contentType = response.headers.get('content-type')
    if (contentType?.includes('application/json')) {
      const data = await response.json()
      res.status(response.status).json(data)
    } else {
      const text = await response.text()
      res.status(response.status).send(text)
    }
  } catch (error) {
    console.error('Proxy error:', error)
    res.status(502).json({
      error: 'Failed to connect to API',
      details: error instanceof Error ? error.message : 'Unknown error'
    })
  }
})

export default router
