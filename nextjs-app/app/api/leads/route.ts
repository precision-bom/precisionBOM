import { NextResponse } from "next/server";
import { db, leads } from "@/lib/db";
import { generateId } from "@/lib/auth";
import { eq } from "drizzle-orm";

interface LeadRequest {
  email: string;
  source?: string;
}

function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export async function POST(request: Request) {
  try {
    const body: LeadRequest = await request.json();
    const { email, source } = body;

    // Validate required fields
    if (!email) {
      return NextResponse.json(
        { success: false, error: "Email is required" },
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

    const normalizedEmail = email.toLowerCase().trim();

    // Check if already signed up
    const [existingLead] = await db
      .select()
      .from(leads)
      .where(eq(leads.email, normalizedEmail));

    if (existingLead) {
      // Still return success - don't reveal if email exists
      return NextResponse.json({
        success: true,
        message: "Thanks for your interest!",
      });
    }

    // Create lead
    const leadId = generateId();

    await db.insert(leads).values({
      id: leadId,
      email: normalizedEmail,
      source: source || "landing",
      createdAt: new Date(),
    });

    return NextResponse.json({
      success: true,
      message: "Thanks for signing up!",
    });
  } catch (error) {
    console.error("Lead capture error:", error);
    return NextResponse.json(
      { success: false, error: "Something went wrong" },
      { status: 500 }
    );
  }
}
