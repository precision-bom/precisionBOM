import Link from "next/link";

// Circuit trace SVG component for visual interest
function CircuitTrace({ className = "" }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 400 200"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Horizontal traces */}
      <path
        d="M0 100 H80 L100 80 H180 L200 100 H280 L300 80 H400"
        stroke="currentColor"
        strokeWidth="2"
        className="text-trace-500/30"
      />
      <path
        d="M0 120 H60 L80 140 H160 L180 120 H260 L280 140 H400"
        stroke="currentColor"
        strokeWidth="2"
        className="text-copper-400/20"
      />

      {/* Vias / pads */}
      <circle cx="100" cy="80" r="6" className="fill-trace-500/40" />
      <circle cx="200" cy="100" r="6" className="fill-copper-400/40" />
      <circle cx="300" cy="80" r="6" className="fill-trace-500/40" />
      <circle cx="80" cy="140" r="4" className="fill-copper-400/30" />
      <circle cx="180" cy="120" r="4" className="fill-trace-500/30" />
      <circle cx="280" cy="140" r="4" className="fill-copper-400/30" />

      {/* Animated trace highlight */}
      <path
        d="M0 100 H80 L100 80 H180 L200 100 H280 L300 80 H400"
        stroke="url(#traceGlow)"
        strokeWidth="2"
        className="animate-trace-flow"
      />

      <defs>
        <linearGradient id="traceGlow" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#22c55e" stopOpacity="0" />
          <stop offset="50%" stopColor="#22c55e" stopOpacity="0.8" />
          <stop offset="100%" stopColor="#22c55e" stopOpacity="0" />
        </linearGradient>
      </defs>
    </svg>
  );
}

// Feature card component
function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="group relative p-6 rounded-lg border border-substrate-800 bg-substrate-950/50 backdrop-blur-sm hover:border-trace-500/50 transition-all duration-300 hover:shadow-trace">
      {/* Corner accents like PCB pads */}
      <div className="absolute top-2 left-2 w-2 h-2 border-l border-t border-substrate-700 group-hover:border-trace-500/50 transition-colors" />
      <div className="absolute top-2 right-2 w-2 h-2 border-r border-t border-substrate-700 group-hover:border-trace-500/50 transition-colors" />
      <div className="absolute bottom-2 left-2 w-2 h-2 border-l border-b border-substrate-700 group-hover:border-trace-500/50 transition-colors" />
      <div className="absolute bottom-2 right-2 w-2 h-2 border-r border-b border-substrate-700 group-hover:border-trace-500/50 transition-colors" />

      <div className="mb-4 text-trace-500">{icon}</div>
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      <p className="text-sm text-substrate-400 leading-relaxed">{description}</p>
    </div>
  );
}

// Stat component
function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div className="text-center">
      <div className="text-3xl md:text-4xl font-bold text-copper-400 mb-1">
        {value}
      </div>
      <div className="text-sm text-substrate-500 uppercase tracking-wider">
        {label}
      </div>
    </div>
  );
}

export default function LandingPage() {
  return (
    <div className="relative">
      {/* Hero Section */}
      <section className="relative pt-20 pb-32 overflow-hidden">
        {/* Circuit trace decoration */}
        <div className="absolute inset-0 flex items-center justify-center opacity-30 pointer-events-none">
          <CircuitTrace className="w-full max-w-6xl" />
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center max-w-3xl mx-auto">
            {/* Terminal-style prefix */}
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-trace-500/30 bg-trace-500/10 mb-8">
              <span className="w-2 h-2 rounded-full bg-trace-500 animate-pulse" />
              <span className="text-xs text-trace-400 uppercase tracking-wider">
                Now in Beta
              </span>
            </div>

            {/* Main headline */}
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
              <span className="text-white">Trace your parts.</span>
              <br />
              <span className="bg-gradient-to-r from-trace-400 to-copper-400 bg-clip-text text-transparent">
                Source with confidence.
              </span>
            </h1>

            {/* Subheadline */}
            <p className="text-lg md:text-xl text-substrate-400 mb-10 max-w-2xl mx-auto leading-relaxed">
              AI-powered BOM optimization that searches across distributors,
              analyzes availability, and finds the best sourcing strategy for
              your electronics projects.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/register"
                className="inline-flex items-center justify-center px-8 py-3 text-base font-medium bg-trace-500 hover:bg-trace-600 text-white rounded-md transition-all shadow-trace hover:shadow-trace-lg"
              >
                Get Started Free
                <svg
                  className="ml-2 w-4 h-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 7l5 5m0 0l-5 5m5-5H6"
                  />
                </svg>
              </Link>
              <Link
                href="#features"
                className="inline-flex items-center justify-center px-8 py-3 text-base font-medium border border-substrate-700 hover:border-substrate-600 text-substrate-300 hover:text-white rounded-md transition-all"
              >
                See How It Works
              </Link>
            </div>

            {/* Terminal-style demo hint */}
            <div className="mt-16 p-4 rounded-lg border border-substrate-800 bg-substrate-950/80 max-w-xl mx-auto text-left">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-3 h-3 rounded-full bg-red-500/80" />
                <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                <div className="w-3 h-3 rounded-full bg-green-500/80" />
                <span className="text-xs text-substrate-600 ml-2">
                  tracesource
                </span>
              </div>
              <code className="text-sm text-substrate-400">
                <span className="text-trace-500">$</span> upload bom.csv
                <br />
                <span className="text-substrate-600"># Parsing 47 line items...</span>
                <br />
                <span className="text-substrate-600"># Searching Octopart, Mouser, DigiKey...</span>
                <br />
                <span className="text-copper-400">{">"}</span> Found optimal sourcing:{" "}
                <span className="text-trace-400">$2,847.32</span>
                <span className="text-substrate-600"> (23% savings)</span>
              </code>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 border-t border-substrate-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Built for engineers who ship
            </h2>
            <p className="text-substrate-400 max-w-2xl mx-auto">
              Stop juggling spreadsheets and browser tabs. TraceSource automates
              the tedious parts of BOM sourcing so you can focus on design.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <FeatureCard
              icon={
                <svg
                  className="w-8 h-8"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              }
              title="Multi-Distributor Search"
              description="Search Octopart, Mouser, and DigiKey simultaneously. Compare prices and availability in real-time."
            />
            <FeatureCard
              icon={
                <svg
                  className="w-8 h-8"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                  />
                </svg>
              }
              title="AI-Powered Optimization"
              description="Intelligent suggestions for alternates, quantity breaks, and sourcing strategies based on your priorities."
            />
            <FeatureCard
              icon={
                <svg
                  className="w-8 h-8"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
              }
              title="Cost vs Availability"
              description="Visualize trade-offs between cost and lead time. Make informed decisions with clear data."
            />
            <FeatureCard
              icon={
                <svg
                  className="w-8 h-8"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                  />
                </svg>
              }
              title="One-Click Export"
              description="Export optimized BOMs to CSV, Excel, or directly to distributor carts. No manual data entry."
            />
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-24 border-t border-substrate-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-12">
            <Stat value="10M+" label="Parts Indexed" />
            <Stat value="3" label="Distributors" />
            <Stat value="23%" label="Avg. Savings" />
            <Stat value="<5s" label="Search Time" />
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-24 border-t border-substrate-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              From BOM to order in minutes
            </h2>
            <p className="text-substrate-400 max-w-2xl mx-auto">
              Three simple steps to optimize your sourcing
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <div className="relative">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-10 h-10 rounded-full border-2 border-trace-500 flex items-center justify-center text-trace-500 font-bold">
                  1
                </div>
                <div className="hidden md:block flex-1 h-px bg-gradient-to-r from-trace-500/50 to-transparent" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Upload Your BOM
              </h3>
              <p className="text-substrate-400 text-sm">
                Drag and drop your CSV or Excel file. We parse manufacturer
                part numbers, quantities, and references automatically.
              </p>
            </div>

            {/* Step 2 */}
            <div className="relative">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-10 h-10 rounded-full border-2 border-copper-400 flex items-center justify-center text-copper-400 font-bold">
                  2
                </div>
                <div className="hidden md:block flex-1 h-px bg-gradient-to-r from-copper-400/50 to-transparent" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Review Suggestions
              </h3>
              <p className="text-substrate-400 text-sm">
                Our AI analyzes your BOM and suggests optimizations: alternates,
                quantity breaks, and distributor splits.
              </p>
            </div>

            {/* Step 3 */}
            <div className="relative">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-10 h-10 rounded-full border-2 border-trace-500 flex items-center justify-center text-trace-500 font-bold">
                  3
                </div>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Export & Order
              </h3>
              <p className="text-substrate-400 text-sm">
                Export your optimized BOM or add items directly to distributor
                carts. Track everything in one place.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-24 border-t border-substrate-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="relative rounded-xl border border-trace-500/30 bg-gradient-to-b from-trace-950/50 to-substrate-950 p-12 md:p-16 text-center overflow-hidden">
            {/* Background circuit pattern */}
            <div className="absolute inset-0 opacity-10">
              <CircuitTrace className="w-full h-full" />
            </div>

            <div className="relative z-10">
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                Ready to optimize your sourcing?
              </h2>
              <p className="text-substrate-400 max-w-xl mx-auto mb-8">
                Join engineers who are saving time and money on every build.
                Start with our free tier - no credit card required.
              </p>
              <Link
                href="/register"
                className="inline-flex items-center justify-center px-8 py-3 text-base font-medium bg-trace-500 hover:bg-trace-600 text-white rounded-md transition-all shadow-trace hover:shadow-trace-lg"
              >
                Start Sourcing Now
                <svg
                  className="ml-2 w-4 h-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 7l5 5m0 0l-5 5m5-5H6"
                  />
                </svg>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
