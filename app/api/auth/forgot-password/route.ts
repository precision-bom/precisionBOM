import { NextResponse } from "next/server";
import { db, users, passwordResetTokens } from "@/lib/db";
import { generateId, generateSecureToken } from "@/lib/auth";
import { sendPasswordResetEmail } from "@/lib/email";
import { eq } from "drizzle-orm";

interface ForgotPasswordRequest {
  email: string;
}

export async function POST(request: Request) {
  try {
    const body: ForgotPasswordRequest = await request.json();
    const { email } = body;

    // Validate required fields
    if (!email) {
      return NextResponse.json(
        { success: false, error: "Email is required" },
        { status: 400 }
      );
    }

    // Find user by email (don't reveal if user exists)
    const [user] = await db
      .select()
      .from(users)
      .where(eq(users.email, email.toLowerCase()));

    if (user) {
      // Generate password reset token
      const { token, hash } = await generateSecureToken();
      const tokenId = generateId();

      // Save token hash to database (expires in 1 hour)
      await db.insert(passwordResetTokens).values({
        id: tokenId,
        userId: user.id,
        tokenHash: hash,
        expiresAt: new Date(Date.now() + 60 * 60 * 1000), // 1 hour
        createdAt: new Date(),
      });

      // Send password reset email
      await sendPasswordResetEmail(email.toLowerCase(), token);
    }

    // Always return success to prevent email enumeration
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Forgot password error:", error);
    // Still return success to prevent information leakage
    return NextResponse.json({ success: true });
  }
}
