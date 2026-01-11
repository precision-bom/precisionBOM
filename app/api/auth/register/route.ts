import { NextResponse } from "next/server";
import { db, users, emailVerificationTokens } from "@/lib/db";
import {
  hashPassword,
  createSession,
  generateId,
  generateSecureToken,
} from "@/lib/auth";
import { sendVerificationEmail } from "@/lib/email";
import { eq } from "drizzle-orm";

interface RegisterRequest {
  email: string;
  password: string;
  name?: string;
}

function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export async function POST(request: Request) {
  try {
    const body: RegisterRequest = await request.json();
    const { email, password, name } = body;

    // Validate required fields
    if (!email || !password) {
      return NextResponse.json(
        { success: false, error: "Email and password are required" },
        { status: 400 }
      );
    }

    // Validate email format
    if (!isValidEmail(email)) {
      return NextResponse.json(
        { success: false, error: "Invalid email format" },
        { status: 400 }
      );
    }

    // Validate password length
    if (password.length < 8) {
      return NextResponse.json(
        { success: false, error: "Password must be at least 8 characters" },
        { status: 400 }
      );
    }

    // Check if email already exists
    const [existingUser] = await db
      .select()
      .from(users)
      .where(eq(users.email, email.toLowerCase()));

    if (existingUser) {
      return NextResponse.json(
        { success: false, error: "Email already registered" },
        { status: 409 }
      );
    }

    // Hash password and create user
    const passwordHash = await hashPassword(password);
    const userId = generateId();

    await db.insert(users).values({
      id: userId,
      email: email.toLowerCase(),
      passwordHash,
      name: name || null,
      createdAt: new Date(),
      emailVerified: false,
    });

    // Generate email verification token
    const { token, hash } = await generateSecureToken();
    const tokenId = generateId();

    await db.insert(emailVerificationTokens).values({
      id: tokenId,
      userId,
      tokenHash: hash,
      expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000), // 24 hours
      createdAt: new Date(),
    });

    // Send verification email
    await sendVerificationEmail(email.toLowerCase(), token);

    // Create session
    await createSession(userId);

    return NextResponse.json({
      success: true,
      user: {
        id: userId,
        email: email.toLowerCase(),
        name: name || null,
      },
    });
  } catch (error) {
    console.error("Registration error:", error);
    return NextResponse.json(
      { success: false, error: "Registration failed" },
      { status: 500 }
    );
  }
}
