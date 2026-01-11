import type { VercelRequest, VercelResponse } from '@vercel/node'
import jwt from 'jsonwebtoken'

const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret'
const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000'
const ADMIN_API_KEY = process.env.ADMIN_API_KEY || ''

function parseCookies(cookieHeader: string | undefined): Record<string, string> {
  if (!cookieHeader) return {}
  return Object.fromEntries(
    cookieHeader.split(';').map(c => {
      const [key, ...v] = c.trim().split('=')
      return [key, v.join('=')]
    })
  )
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  // Verify JWT token
  const cookies = parseCookies(req.headers.cookie)
  const token = cookies.auth_token

  if (!token) {
    return res.status(401).json({ error: 'Not authenticated' })
  }

  try {
    jwt.verify(token, JWT_SECRET)
  } catch {
    return res.status(401).json({ error: 'Invalid token' })
  }

  // Check API key is configured
  if (!ADMIN_API_KEY) {
    return res.status(500).json({ error: 'ADMIN_API_KEY not configured' })
  }

  // Build target URL
  const pathSegments = req.query.path
  const path = Array.isArray(pathSegments) ? pathSegments.join('/') : pathSegments || ''
  const queryString = req.url?.includes('?') ? req.url.slice(req.url.indexOf('?')) : ''
  const targetUrl = `${PYTHON_API_URL}/${path}${queryString}`

  try {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'X-API-Key': ADMIN_API_KEY,
    }

    const fetchOptions: RequestInit = {
      method: req.method || 'GET',
      headers,
    }

    if (req.method !== 'GET' && req.method !== 'HEAD' && req.body) {
      fetchOptions.body = JSON.stringify(req.body)
    }

    const response = await fetch(targetUrl, fetchOptions)

    // Handle response
    const contentType = response.headers.get('content-type')
    if (contentType?.includes('application/json')) {
      const data = await response.json()
      return res.status(response.status).json(data)
    } else {
      const text = await response.text()
      return res.status(response.status).send(text)
    }
  } catch (error) {
    console.error('Proxy error:', error)
    return res.status(502).json({
      error: 'Failed to connect to API',
      details: error instanceof Error ? error.message : 'Unknown error'
    })
  }
}
