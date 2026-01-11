import Link from "next/link";

// Feature card data
const coreFeatures = [
  {
    title: "Multi-Source Search",
    icon: (
      <svg
        className="w-8 h-8"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M10 7v6m3-3H7"
        />
      </svg>
    ),
    description:
      "Search across Octopart, Mouser, DigiKey simultaneously. Real-time stock levels, pricing across qty breaks.",
    details: [
      "Parallel API queries",
      "Live inventory status",
      "Price break analysis",
      "Lead time visibility",
    ],
  },
  {
    title: "AI Optimization",
    icon: (
      <svg
        className="w-8 h-8"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
        />
      </svg>
    ),
    description:
      "GPT-powered suggestions for cost reduction, stock availability, vendor consolidation. Not just search - strategy.",
    details: [
      "Cost optimization",
      "Alternate part suggestions",
      "Vendor consolidation",
      "Risk assessment",
    ],
  },
  {
    title: "BOM Intelligence",
    icon: (
      <svg
        className="w-8 h-8"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
        />
      </svg>
    ),
    description:
      "Auto-detect columns from messy CSVs. Handles part numbers, MPNs, descriptions. Fuzzy matching for ambiguous parts.",
    details: [
      "Column auto-detection",
      "MPN normalization",
      "Fuzzy matching",
      "Description parsing",
    ],
  },
  {
    title: "Export Ready",
    icon: (
      <svg
        className="w-8 h-8"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
        />
      </svg>
    ),
    description:
      "Download optimized BOMs. Track reasoning. Share with team.",
    details: [
      "CSV/Excel export",
      "Decision audit trail",
      "Shareable links",
      "Version history",
    ],
  },
];

const teamFeatures = [
  {
    title: "Saved BOMs",
    description: "Store and version your bill of materials. Quick access to recent projects.",
    available: true,
  },
  {
    title: "History",
    description: "Track every search, every decision. Full audit trail for compliance.",
    available: true,
  },
  {
    title: "Collaboration",
    description: "Share BOMs with team members. Comment on part selections. Assign reviewers.",
    available: false,
    comingSoon: true,
  },
];

const integrations = [
  { name: "Octopart", available: true },
  { name: "Mouser", available: true },
  { name: "DigiKey", available: true },
  { name: "Arrow", available: false },
  { name: "Newark", available: false },
  { name: "LCSC", available: false },
];

export default function FeaturesPage() {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Background grid pattern */}
      <div className="fixed inset-0 bg-grid-pattern bg-grid opacity-50 pointer-events-none" />

      {/* Gradient overlay */}
      <div className="fixed inset-0 bg-dark-gradient pointer-events-none" />

      {/* Content */}
      <div className="relative z-10">
        {/* Navigation */}
        <nav className="border-b border-trace-900/50 backdrop-blur-sm">
          <div className="max-w-6xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <Link href="/" className="font-mono text-xl font-bold text-trace-500">
                TraceSource
              </Link>
              <div className="flex items-center gap-6">
                <Link
                  href="/features"
                  className="text-sm text-trace-400 hover:text-trace-300 transition-colors"
                >
                  Features
                </Link>
                <Link
                  href="/"
                  className="text-sm bg-trace-600 hover:bg-trace-500 px-4 py-2 rounded font-mono transition-colors"
                >
                  Launch App
                </Link>
              </div>
            </div>
          </div>
        </nav>

        {/* Header */}
        <header className="max-w-6xl mx-auto px-6 pt-24 pb-16">
          <div className="max-w-3xl">
            <p className="font-mono text-trace-500 text-sm mb-4 tracking-wider uppercase">
              Features
            </p>
            <h1 className="text-4xl md:text-5xl font-bold mb-6 leading-tight">
              Built for engineers who speak in{" "}
              <span className="text-copper-400">nets</span> and{" "}
              <span className="text-trace-500">vias</span>
            </h1>
            <p className="text-lg text-substrate-400 font-mono">
              Stop wasting hours on distributor sites. Get sourcing suggestions in seconds.
            </p>
          </div>
        </header>

        {/* Core Features */}
        <section className="max-w-6xl mx-auto px-6 py-16">
          <div className="grid md:grid-cols-2 gap-6">
            {coreFeatures.map((feature, index) => (
              <div
                key={index}
                className="group relative bg-[#171717] border border-substrate-800 rounded-lg p-6 hover:border-trace-700 transition-all duration-300 hover:shadow-trace"
              >
                {/* Corner accent */}
                <div className="absolute top-0 right-0 w-16 h-16 overflow-hidden">
                  <div className="absolute top-2 right-2 w-2 h-2 bg-trace-500 rounded-full opacity-50 group-hover:opacity-100 transition-opacity" />
                </div>

                {/* Icon */}
                <div className="text-copper-400 mb-4">{feature.icon}</div>

                {/* Title */}
                <h3 className="font-mono text-xl font-semibold text-white mb-3">
                  {feature.title}
                </h3>

                {/* Description */}
                <p className="text-substrate-400 mb-4 leading-relaxed">
                  {feature.description}
                </p>

                {/* Details */}
                <ul className="space-y-2">
                  {feature.details.map((detail, detailIndex) => (
                    <li
                      key={detailIndex}
                      className="flex items-center gap-2 text-sm text-substrate-500"
                    >
                      <span className="w-1.5 h-1.5 bg-trace-600 rounded-full" />
                      <span className="font-mono">{detail}</span>
                    </li>
                  ))}
                </ul>

                {/* Bottom trace line */}
                <div className="absolute bottom-0 left-6 right-6 h-px bg-gradient-to-r from-transparent via-trace-800 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
            ))}
          </div>
        </section>

        {/* Divider with circuit pattern */}
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex items-center gap-4">
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-substrate-700 to-transparent" />
            <div className="flex gap-2">
              <div className="w-2 h-2 bg-trace-600 rounded-full" />
              <div className="w-2 h-2 bg-copper-500 rounded-full" />
              <div className="w-2 h-2 bg-trace-600 rounded-full" />
            </div>
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-substrate-700 to-transparent" />
          </div>
        </div>

        {/* For Teams */}
        <section className="max-w-6xl mx-auto px-6 py-16">
          <div className="mb-12">
            <h2 className="font-mono text-2xl font-bold text-white mb-2">
              For Teams
            </h2>
            <p className="text-substrate-400">
              Streamline your procurement workflow across the organization.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {teamFeatures.map((feature, index) => (
              <div
                key={index}
                className={`relative bg-[#171717] border rounded-lg p-6 ${
                  feature.comingSoon
                    ? "border-dashed border-substrate-700"
                    : "border-substrate-800"
                }`}
              >
                {feature.comingSoon && (
                  <span className="absolute top-4 right-4 text-xs font-mono text-copper-400 bg-copper-400/10 px-2 py-1 rounded">
                    Coming Soon
                  </span>
                )}

                <h3 className="font-mono text-lg font-semibold text-white mb-2">
                  {feature.title}
                </h3>
                <p
                  className={`text-sm ${
                    feature.comingSoon ? "text-substrate-600" : "text-substrate-400"
                  }`}
                >
                  {feature.description}
                </p>

                {feature.available && (
                  <div className="mt-4 flex items-center gap-2 text-trace-500 text-sm">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                    <span className="font-mono">Available now</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* Integrations */}
        <section className="max-w-6xl mx-auto px-6 py-16">
          <div className="bg-[#171717] border border-substrate-800 rounded-lg p-8">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8">
              <div>
                <h2 className="font-mono text-2xl font-bold text-white mb-2">
                  Integrations
                </h2>
                <p className="text-substrate-400">
                  Works with your existing workflow. More providers coming.
                </p>
              </div>

              <div className="flex flex-wrap gap-3">
                {integrations.map((integration, index) => (
                  <div
                    key={index}
                    className={`font-mono text-sm px-4 py-2 rounded border ${
                      integration.available
                        ? "bg-trace-950/50 border-trace-800 text-trace-400"
                        : "bg-substrate-900/50 border-substrate-800 text-substrate-600"
                    }`}
                  >
                    {integration.name}
                    {!integration.available && (
                      <span className="ml-2 text-xs text-substrate-700">soon</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="max-w-6xl mx-auto px-6 py-24">
          <div className="text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Start sourcing <span className="text-trace-500">smarter</span>
            </h2>
            <p className="text-substrate-400 mb-8 max-w-lg mx-auto">
              Upload your BOM. Get optimized sourcing suggestions. Ship faster.
            </p>
            <Link
              href="/"
              className="inline-flex items-center gap-2 bg-trace-600 hover:bg-trace-500 text-white px-8 py-3 rounded font-mono font-semibold transition-all duration-300 hover:shadow-trace-lg"
            >
              <span>Launch TraceSource</span>
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
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
        </section>

        {/* Footer */}
        <footer className="border-t border-substrate-800">
          <div className="max-w-6xl mx-auto px-6 py-8">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div className="font-mono text-sm text-substrate-500">
                TraceSource - BOM sourcing for hardware teams
              </div>
              <div className="flex items-center gap-6 text-sm text-substrate-600">
                <span className="font-mono">v1.0</span>
                <div className="w-px h-4 bg-substrate-800" />
                <span className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-trace-500 rounded-full animate-pulse-slow" />
                  <span className="font-mono">All systems operational</span>
                </span>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
