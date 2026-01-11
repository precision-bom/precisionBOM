import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TraceSource - AI-Powered BOM Sourcing",
  description:
    "Trace your parts. Source with confidence. AI-powered BOM optimization across Octopart, Mouser, and DigiKey.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="bg-substrate-950 text-silkscreen min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}
