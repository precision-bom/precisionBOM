import Link from "next/link";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-substrate-950 bg-dark-gradient">
      {/* Grid pattern overlay */}
      <div className="absolute inset-0 bg-grid-pattern bg-grid opacity-50" />

      {/* Home link */}
      <Link
        href="/"
        className="absolute top-6 left-6 z-10 flex items-center gap-2 text-substrate-400 hover:text-trace-500 transition-colors font-mono text-sm"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-4 w-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M10 19l-7-7m0 0l7-7m-7 7h18"
          />
        </svg>
        <span>Back to Home</span>
      </Link>

      {/* Centered content */}
      <div className="relative z-10 flex min-h-screen items-center justify-center px-4 py-12">
        {children}
      </div>

      {/* Decorative circuit traces */}
      <div className="absolute bottom-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-trace-500/20 to-transparent" />
      <div className="absolute top-0 right-0 h-full w-px bg-gradient-to-b from-transparent via-trace-500/20 to-transparent" />
    </div>
  );
}
