import { Metadata } from "next";

export const metadata: Metadata = {
  title: "About | TraceSource",
  description: "The story behind TraceSource - BOM sourcing built by engineers, for engineers",
};

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-dark-gradient">
      {/* Grid overlay */}
      <div className="fixed inset-0 bg-grid-pattern bg-grid opacity-50 pointer-events-none" />

      <main className="relative z-10">
        {/* Header */}
        <header className="border-b border-trace-500/20">
          <div className="container mx-auto px-6 py-4">
            <a href="/" className="inline-flex items-center gap-2 text-trace-500 hover:text-trace-400 transition-colors font-mono text-sm">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              back to app
            </a>
          </div>
        </header>

        {/* Hero Section */}
        <section className="container mx-auto px-6 py-20">
          <div className="max-w-4xl">
            <div className="inline-block mb-4">
              <span className="font-mono text-copper-400 text-sm tracking-wider">// ABOUT</span>
            </div>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-silkscreen mb-6 font-mono">
              The story behind<br />
              <span className="text-trace-500">the traces</span>
            </h1>
            <div className="w-24 h-1 bg-copper-gradient rounded-full" />
          </div>
        </section>

        {/* Mission Section */}
        <section className="container mx-auto px-6 py-16">
          <div className="max-w-4xl">
            <h2 className="font-mono text-copper-400 text-sm tracking-wider mb-6">// WHY WE BUILT THIS</h2>
            <div className="space-y-6 text-lg text-substrate-300 leading-relaxed">
              <p className="text-2xl text-silkscreen font-semibold">
                We built this because BOM sourcing sucks.
              </p>
              <p>
                Hours wasted cross-referencing distributors. Tabs upon tabs of Digi-Key, Mouser,
                and LCSC searches. Copy-pasting part numbers into spreadsheets like it's 2005.
              </p>
              <p>
                Stock changes mid-project. Lead times shift overnight. That capacitor you spec'd
                last week? Now it's 52-week backorder and you're scrambling for alternatives at 11pm
                before your Monday production meeting.
              </p>
              <p className="text-trace-400 font-mono text-base border-l-2 border-trace-500 pl-4">
                We're engineers who got tired of spreadsheet hell. So we built the tool we wished existed.
              </p>
            </div>
          </div>
        </section>

        {/* What We Believe Section */}
        <section className="container mx-auto px-6 py-16">
          <div className="max-w-4xl">
            <h2 className="font-mono text-copper-400 text-sm tracking-wider mb-8">// WHAT WE BELIEVE</h2>
            <div className="grid gap-6 md:grid-cols-3">
              <BeliefCard
                number="01"
                title="Your time matters"
                description="You should be designing circuits, not hunting for stock levels. The mundane stuff should be automated."
              />
              <BeliefCard
                number="02"
                title="AI augments, not replaces"
                description="The LLM suggests and explains. You make the calls. We're not here to replace engineering judgment."
              />
              <BeliefCard
                number="03"
                title="Transparency first"
                description="See why we suggest what we suggest. Every recommendation comes with reasoning you can verify."
              />
            </div>
          </div>
        </section>

        {/* How It Works Section */}
        <section className="container mx-auto px-6 py-16">
          <div className="max-w-4xl">
            <h2 className="font-mono text-copper-400 text-sm tracking-wider mb-8">// HOW IT WORKS</h2>
            <div className="bg-substrate-900/50 border border-trace-500/20 rounded-lg p-8">
              <div className="space-y-8">
                <TechBlock
                  step="1"
                  title="Multi-provider aggregation"
                  description="We query Octopart, Mouser, Digi-Key, and more in parallel. Real-time pricing, real stock levels, actual lead times."
                  code="async fetchAllProviders(mpn: string)"
                />
                <TechBlock
                  step="2"
                  title="LLM-powered analysis"
                  description="Our AI disambiguates vague part descriptions, identifies compatible alternatives, and optimizes for your constraints - cost, stock, or minimal distributors."
                  code="agent.analyze({ parts, constraints })"
                />
                <TechBlock
                  step="3"
                  title="Ranked recommendations"
                  description="Get concrete suggestions with scores, not just raw data dumps. Each option explains the trade-offs so you can make informed decisions fast."
                  code="return suggestions.sort((a, b) => b.score - a.score)"
                />
              </div>
            </div>
          </div>
        </section>

        {/* Built With Section */}
        <section className="container mx-auto px-6 py-16">
          <div className="max-w-4xl">
            <h2 className="font-mono text-copper-400 text-sm tracking-wider mb-8">// STACK</h2>
            <p className="text-substrate-400 mb-6">
              We believe in being transparent about how things are built. Here's what's under the hood:
            </p>
            <div className="flex flex-wrap gap-3">
              <TechBadge>Next.js 14</TechBadge>
              <TechBadge>TypeScript</TechBadge>
              <TechBadge>OpenAI GPT-4</TechBadge>
              <TechBadge>Octopart API</TechBadge>
              <TechBadge>Mouser API</TechBadge>
              <TechBadge>Digi-Key API</TechBadge>
              <TechBadge>Tailwind CSS</TechBadge>
              <TechBadge>Vercel</TechBadge>
            </div>
            <p className="text-substrate-500 text-sm mt-6 font-mono">
              // No black boxes. Ask us anything about the implementation.
            </p>
          </div>
        </section>

        {/* Contact Section */}
        <section className="container mx-auto px-6 py-16 pb-24">
          <div className="max-w-4xl">
            <h2 className="font-mono text-copper-400 text-sm tracking-wider mb-8">// GET IN TOUCH</h2>
            <div className="bg-substrate-900/50 border border-copper-400/20 rounded-lg p-8">
              <h3 className="text-2xl font-semibold text-silkscreen mb-4">
                We want to hear from you
              </h3>
              <p className="text-substrate-300 mb-6">
                What features would make your life easier? Found a bug? Have a distributor
                you want us to add? We're all ears.
              </p>
              <div className="space-y-4">
                <a
                  href="mailto:feedback@tracesource.dev"
                  className="inline-flex items-center gap-2 px-6 py-3 bg-trace-500 hover:bg-trace-600 text-substrate-950 font-semibold rounded-lg transition-colors font-mono"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  feedback@tracesource.dev
                </a>
                <p className="text-substrate-500 text-sm">
                  Or open an issue on{" "}
                  <a href="https://github.com/tracesource" className="text-trace-400 hover:text-trace-300 underline">
                    GitHub
                  </a>
                  {" "}- we read everything.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-trace-500/10">
          <div className="container mx-auto px-6 py-8">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
              <div className="font-mono text-trace-500 text-lg font-bold">
                TraceSource
              </div>
              <div className="text-substrate-500 text-sm font-mono">
                Built by engineers, for engineers.
              </div>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}

function BeliefCard({ number, title, description }: { number: string; title: string; description: string }) {
  return (
    <div className="bg-substrate-900/30 border border-substrate-700/50 rounded-lg p-6 hover:border-trace-500/30 transition-colors">
      <div className="font-mono text-copper-400 text-xs mb-3">{number}</div>
      <h3 className="text-silkscreen font-semibold text-lg mb-2">{title}</h3>
      <p className="text-substrate-400 text-sm leading-relaxed">{description}</p>
    </div>
  );
}

function TechBlock({ step, title, description, code }: { step: string; title: string; description: string; code: string }) {
  return (
    <div className="flex gap-6">
      <div className="flex-shrink-0 w-10 h-10 bg-trace-500/10 border border-trace-500/30 rounded-lg flex items-center justify-center">
        <span className="font-mono text-trace-500 font-bold">{step}</span>
      </div>
      <div className="flex-1">
        <h3 className="text-silkscreen font-semibold text-lg mb-2">{title}</h3>
        <p className="text-substrate-400 text-sm mb-3">{description}</p>
        <code className="inline-block px-3 py-1 bg-substrate-950 border border-substrate-700 rounded text-copper-400 text-xs font-mono">
          {code}
        </code>
      </div>
    </div>
  );
}

function TechBadge({ children }: { children: React.ReactNode }) {
  return (
    <span className="px-4 py-2 bg-substrate-900 border border-substrate-700 rounded-full text-substrate-300 text-sm font-mono hover:border-trace-500/50 transition-colors">
      {children}
    </span>
  );
}
