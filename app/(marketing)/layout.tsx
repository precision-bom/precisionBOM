import Link from "next/link";

export default function MarketingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white font-mono">
      {/* Background grid pattern */}
      <div className="fixed inset-0 bg-grid-pattern bg-grid opacity-50 pointer-events-none" />

      {/* Gradient overlay */}
      <div className="fixed inset-0 bg-dark-gradient pointer-events-none" />

      {/* Navigation */}
      <nav className="relative z-50 border-b border-substrate-800/50 backdrop-blur-sm bg-[#0a0a0a]/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-2 group">
              <div className="relative">
                <svg
                  width="32"
                  height="32"
                  viewBox="0 0 32 32"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  className="text-trace-500"
                >
                  {/* PCB trace pattern logo */}
                  <rect x="2" y="2" width="28" height="28" rx="4" stroke="currentColor" strokeWidth="1.5" fill="none" />
                  <circle cx="8" cy="8" r="2" fill="currentColor" />
                  <circle cx="24" cy="8" r="2" fill="currentColor" />
                  <circle cx="8" cy="24" r="2" fill="currentColor" />
                  <circle cx="24" cy="24" r="2" fill="currentColor" />
                  <path d="M8 8 L16 16 L24 8" stroke="currentColor" strokeWidth="1.5" fill="none" />
                  <path d="M8 24 L16 16 L24 24" stroke="currentColor" strokeWidth="1.5" fill="none" />
                  <circle cx="16" cy="16" r="3" fill="#fbbf24" />
                </svg>
              </div>
              <span className="text-lg font-bold tracking-tight">
                <span className="text-trace-500">Trace</span>
                <span className="text-copper-400">Source</span>
              </span>
            </Link>

            {/* Navigation Links */}
            <div className="hidden md:flex items-center gap-8">
              <Link
                href="#features"
                className="text-sm text-substrate-400 hover:text-trace-500 transition-colors"
              >
                Features
              </Link>
              <Link
                href="/about"
                className="text-sm text-substrate-400 hover:text-trace-500 transition-colors"
              >
                About
              </Link>
            </div>

            {/* Auth Buttons */}
            <div className="flex items-center gap-3">
              <Link
                href="/login"
                className="text-sm px-4 py-2 text-substrate-300 hover:text-white transition-colors"
              >
                Login
              </Link>
              <Link
                href="/register"
                className="text-sm px-4 py-2 bg-trace-500 hover:bg-trace-600 text-white rounded-md transition-colors shadow-trace"
              >
                Sign Up
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="relative z-10">{children}</main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-substrate-800/50 bg-[#0a0a0a]/90 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* Brand */}
            <div className="col-span-1 md:col-span-2">
              <Link href="/" className="flex items-center gap-2 mb-4">
                <span className="text-lg font-bold tracking-tight">
                  <span className="text-trace-500">Trace</span>
                  <span className="text-copper-400">Source</span>
                </span>
              </Link>
              <p className="text-sm text-substrate-500 max-w-xs">
                AI-powered BOM sourcing for electronics engineers.
                Find parts faster. Source smarter.
              </p>
            </div>

            {/* Product Links */}
            <div>
              <h4 className="text-xs uppercase tracking-wider text-substrate-500 mb-4">
                Product
              </h4>
              <ul className="space-y-2">
                <li>
                  <Link
                    href="#features"
                    className="text-sm text-substrate-400 hover:text-trace-500 transition-colors"
                  >
                    Features
                  </Link>
                </li>
                <li>
                  <Link
                    href="/pricing"
                    className="text-sm text-substrate-400 hover:text-trace-500 transition-colors"
                  >
                    Pricing
                  </Link>
                </li>
                <li>
                  <Link
                    href="/docs"
                    className="text-sm text-substrate-400 hover:text-trace-500 transition-colors"
                  >
                    Documentation
                  </Link>
                </li>
              </ul>
            </div>

            {/* Legal Links */}
            <div>
              <h4 className="text-xs uppercase tracking-wider text-substrate-500 mb-4">
                Legal
              </h4>
              <ul className="space-y-2">
                <li>
                  <Link
                    href="/privacy"
                    className="text-sm text-substrate-400 hover:text-trace-500 transition-colors"
                  >
                    Privacy Policy
                  </Link>
                </li>
                <li>
                  <Link
                    href="/terms"
                    className="text-sm text-substrate-400 hover:text-trace-500 transition-colors"
                  >
                    Terms of Service
                  </Link>
                </li>
                <li>
                  <Link
                    href="/about"
                    className="text-sm text-substrate-400 hover:text-trace-500 transition-colors"
                  >
                    About Us
                  </Link>
                </li>
              </ul>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="mt-12 pt-8 border-t border-substrate-800/50 flex flex-col sm:flex-row justify-between items-center gap-4">
            <p className="text-xs text-substrate-600">
              &copy; {new Date().getFullYear()} TraceSource. All rights reserved.
            </p>
            <div className="flex items-center gap-1 text-xs text-substrate-600">
              <span className="inline-block w-2 h-2 rounded-full bg-trace-500 animate-pulse" />
              <span>All systems operational</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
