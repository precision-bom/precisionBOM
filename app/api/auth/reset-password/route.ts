import { NextResponse } from "next/server";
import { db, users, passwordResetTokens } from "@/lib/db";
import { hashPassword, verifySecureToken } from "@/lib/auth";
import { eq, and, gt } from "drizzle-orm";

interface ResetPasswordRequest {
  token: string;
  password: string;
}

export async function POST(request: Request) {
  try {
    const body: ResetPasswordRequest = await request.json();
    const { token, password } = body;

    // Validate required fields
    if (!token || !password) {
      return NextResponse.json(
        { success: false, error: "Token and password are required" },
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

    // Find all non-expired tokens
    const tokens = await db
      .select()
      .from(passwordResetTokens)
      .where(gt(passwordResetTokens.expiresAt, new Date()));

    // Find matching token by verifying hash
    let validTokenRecord = null;
    for (const tokenRecord of tokens) {
      const isValid = await verifySecureToken(token, tokenRecord.tokenHash);
      if (isValid) {
        validTokenRecord = tokenRecord;
        break;
      }
    }

    if (!validTokenRecord) {
      return NextResponse.json(
        { success: false, error: "Invalid or expired token" },
        { status: 400 }
      );
    }

    // Hash new password
    const passwordHash = await hashPassword(password);

    // Update user password
    await db
      .update(users)
      .set({ passwordHash })
      .where(eq(users.id, validTokenRecord.userId));

    // Delete the used token
    await db
      .delete(passwordResetTokens)
      .where(eq(passwordResetTokens.id, validTokenRecord.id));

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Reset password error:", error);
    return NextResponse.json(
      { success: false, error: "Password reset failed" },
      { status: 500 }
    );
  }
}
