import bcrypt from "bcryptjs";
import { SignJWT, jwtVerify } from "jose";
import { cookies } from "next/headers";
import { db, users, sessions } from "@/lib/db";
import { eq, and, gt } from "drizzle-orm";

const JWT_SECRET = new TextEncoder().encode(
  process.env.JWT_SECRET || "your-secret-key-change-in-production"
);

const SESSION_COOKIE = "session";
const SESSION_DURATION = 30 * 24 * 60 * 60 * 1000; // 30 days

// Generate a random ID
export function generateId(length = 21): string {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let result = "";
  const randomValues = new Uint8Array(length);
  crypto.getRandomValues(randomValues);
  for (let i = 0; i < length; i++) {
    result += chars[randomValues[i] % chars.length];
  }
  return result;
}

// Password utilities
export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 12);
}

export async function verifyPassword(
  password: string,
  hash: string
): Promise<boolean> {
  return bcrypt.compare(password, hash);
}

// JWT utilities
export async function createToken(payload: Record<string, unknown>): Promise<string> {
  return new SignJWT(payload)
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("30d")
    .sign(JWT_SECRET);
}

export async function verifyToken(token: string): Promise<Record<string, unknown> | null> {
  try {
    const { payload } = await jwtVerify(token, JWT_SECRET);
    return payload as Record<string, unknown>;
  } catch {
    return null;
  }
}

// Session management
export async function createSession(userId: string): Promise<string> {
  const sessionId = generateId();
  const expiresAt = new Date(Date.now() + SESSION_DURATION);

  await db.insert(sessions).values({
    id: sessionId,
    userId,
    expiresAt,
    createdAt: new Date(),
  });

  const token = await createToken({ sessionId, userId });

  const cookieStore = await cookies();
  cookieStore.set(SESSION_COOKIE, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    expires: expiresAt,
    path: "/",
  });

  return sessionId;
}

export async function getSession(): Promise<{
  user: typeof users.$inferSelect;
  session: typeof sessions.$inferSelect;
} | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get(SESSION_COOKIE)?.value;

  if (!token) return null;

  const payload = await verifyToken(token);
  if (!payload?.sessionId) return null;

  const [session] = await db
    .select()
    .from(sessions)
    .where(
      and(
        eq(sessions.id, payload.sessionId as string),
        gt(sessions.expiresAt, new Date())
      )
    );

  if (!session) return null;

  const [user] = await db.select().from(users).where(eq(users.id, session.userId));
  if (!user) return null;

  return { user, session };
}

export async function destroySession(): Promise<void> {
  const cookieStore = await cookies();
  const token = cookieStore.get(SESSION_COOKIE)?.value;

  if (token) {
    const payload = await verifyToken(token);
    if (payload?.sessionId) {
      await db.delete(sessions).where(eq(sessions.id, payload.sessionId as string));
    }
  }

  cookieStore.delete(SESSION_COOKIE);
}

// Generate secure tokens for password reset / email verification
export async function generateSecureToken(): Promise<{ token: string; hash: string }> {
  const token = generateId(32);
  const hash = await bcrypt.hash(token, 10);
  return { token, hash };
}

export async function verifySecureToken(token: string, hash: string): Promise<boolean> {
  return bcrypt.compare(token, hash);
}
