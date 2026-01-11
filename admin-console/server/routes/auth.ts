import { Router } from 'express'
import jwt from 'jsonwebtoken'
import type { Request, Response } from 'express'

const router = Router()

function getEnv() {
  return {
    ADMIN_USER: process.env.ADMIN_USER || 'admin',
    ADMIN_PASSWORD: process.env.ADMIN_PASSWORD || 'changeme',
    JWT_SECRET: process.env.JWT_SECRET || 'dev-secret',
  }
}

// POST /api/auth/login
router.post('/login', (req: Request, res: Response) => {
  const { ADMIN_USER, ADMIN_PASSWORD, JWT_SECRET } = getEnv()
  const { username, password } = req.body

  if (username !== ADMIN_USER || password !== ADMIN_PASSWORD) {
    res.status(401).json({ error: 'Invalid credentials' })
    return
  }

  const token = jwt.sign(
    { sub: username, role: 'admin' },
    JWT_SECRET,
    { expiresIn: '8h' }
  )

  res.cookie('auth_token', token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 8 * 60 * 60 * 1000, // 8 hours
    path: '/',
  })

  res.json({ success: true, user: { username, role: 'admin' } })
})

// POST /api/auth/logout
router.post('/logout', (_req: Request, res: Response) => {
  res.clearCookie('auth_token', { path: '/' })
  res.json({ success: true })
})

// GET /api/auth/me
router.get('/me', (req: Request, res: Response) => {
  const { JWT_SECRET } = getEnv()
  const token = req.cookies?.auth_token

  if (!token) {
    res.status(401).json({ error: 'Not authenticated' })
    return
  }

  try {
    const decoded = jwt.verify(token, JWT_SECRET) as { sub: string; role: string }
    res.json({ user: { username: decoded.sub, role: decoded.role } })
  } catch {
    res.status(401).json({ error: 'Invalid token' })
  }
})

export default router
