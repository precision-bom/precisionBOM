import type { VercelRequest, VercelResponse } from '@vercel/node'
import jwt from 'jsonwebtoken'

const ADMIN_USER = process.env.ADMIN_USER || 'admin'
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'changeme'
const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret'

export default function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const { username, password } = req.body || {}

  if (username !== ADMIN_USER || password !== ADMIN_PASSWORD) {
    return res.status(401).json({ error: 'Invalid credentials' })
  }

  const token = jwt.sign(
    { sub: username, role: 'admin' },
    JWT_SECRET,
    { expiresIn: '8h' }
  )

  res.setHeader('Set-Cookie', [
    `auth_token=${token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${8 * 60 * 60}${process.env.NODE_ENV === 'production' ? '; Secure' : ''}`
  ])

  return res.status(200).json({ success: true, user: { username, role: 'admin' } })
}
