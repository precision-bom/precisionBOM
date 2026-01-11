import type { Request, Response, NextFunction } from 'express'
import jwt from 'jsonwebtoken'

export interface AuthRequest extends Request {
  user?: { username: string; role: string }
}

export function requireAuth(req: AuthRequest, res: Response, next: NextFunction): void {
  const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret'
  const token = req.cookies?.auth_token

  if (!token) {
    res.status(401).json({ error: 'Not authenticated' })
    return
  }

  try {
    const decoded = jwt.verify(token, JWT_SECRET) as { sub: string; role: string }
    req.user = { username: decoded.sub, role: decoded.role }
    next()
  } catch {
    res.status(401).json({ error: 'Invalid token' })
  }
}
