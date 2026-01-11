import { NextResponse } from "next/server";
import { getSession } from "@/lib/auth";

export async function GET() {
  try {
    const sessionData = await getSession();

    if (!sessionData) {
      return NextResponse.json({ user: null });
    }

    const { user } = sessionData;

    return NextResponse.json({
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        emailVerified: user.emailVerified,
      },
    });
  } catch (error) {
    console.error("Get session error:", error);
    return NextResponse.json({ user: null });
  }
}
