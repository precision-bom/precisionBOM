import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy | TraceSource",
  description: "Learn how TraceSource collects, uses, and protects your data.",
};

const sections = [
  { id: "information-collected", title: "Information We Collect" },
  { id: "how-we-use", title: "How We Use Your Information" },
  { id: "data-storage", title: "Data Storage & Security" },
  { id: "third-party", title: "Third-Party Services" },
  { id: "your-rights", title: "Your Rights" },
  { id: "cookies", title: "Cookies" },
  { id: "contact", title: "Contact Us" },
];

export default function PrivacyPage() {
  return (
    <div className="container mx-auto px-4 py-12 max-w-4xl">
      {/* Page Header */}
      <div className="mb-12">
        <h1 className="font-mono text-4xl font-bold text-silkscreen mb-4">
          Privacy Policy
        </h1>
        <p className="text-substrate-400">
          Last updated: January 10, 2025
        </p>
      </div>

      {/* Table of Contents */}
      <nav className="mb-12 p-6 rounded-lg border border-trace-900/50 bg-[#171717]/50">
        <h2 className="font-mono text-lg font-semibold text-trace-500 mb-4">
          Table of Contents
        </h2>
        <ol className="space-y-2">
          {sections.map((section, index) => (
            <li key={section.id}>
              <a
                href={`#${section.id}`}
                className="text-substrate-300 hover:text-trace-500 transition-colors flex items-center gap-2"
              >
                <span className="font-mono text-trace-600 text-sm">
                  {String(index + 1).padStart(2, "0")}
                </span>
                {section.title}
              </a>
            </li>
          ))}
        </ol>
      </nav>

      {/* Introduction */}
      <div className="prose-section mb-12">
        <p className="text-substrate-300 leading-relaxed">
          At TraceSource, we take your privacy seriously. This Privacy Policy explains how we collect,
          use, disclose, and safeguard your information when you use our BOM (Bill of Materials)
          sourcing platform. Please read this policy carefully to understand our practices regarding
          your personal data.
        </p>
      </div>

      {/* Section 1: Information We Collect */}
      <section id="information-collected" className="mb-12 scroll-mt-8">
        <h2 className="font-mono text-2xl font-bold text-silkscreen mb-6 flex items-center gap-3">
          <span className="text-trace-500">01</span>
          Information We Collect
        </h2>
        <div className="space-y-6 text-substrate-300 leading-relaxed">
          <div>
            <h3 className="font-mono text-lg text-substrate-100 mb-3">Account Information</h3>
            <p>
              When you create an account, we collect your email address, name, and any other
              information you choose to provide. This information is used to identify you and
              provide personalized services.
            </p>
          </div>
          <div>
            <h3 className="font-mono text-lg text-substrate-100 mb-3">BOM Data</h3>
            <p>
              When you upload Bill of Materials files, we process the component data including
              part numbers, manufacturers, quantities, and specifications. This data is used to
              provide sourcing suggestions and is stored securely in your account.
            </p>
          </div>
          <div>
            <h3 className="font-mono text-lg text-substrate-100 mb-3">Usage Analytics</h3>
            <p>
              We collect anonymized usage data to understand how our platform is used and to
              improve our services. This includes page views, feature usage, search queries,
              and interaction patterns. We do not link this data to your personal identity.
            </p>
          </div>
        </div>
      </section>

      {/* Section 2: How We Use Your Information */}
      <section id="how-we-use" className="mb-12 scroll-mt-8">
        <h2 className="font-mono text-2xl font-bold text-silkscreen mb-6 flex items-center gap-3">
          <span className="text-trace-500">02</span>
          How We Use Your Information
        </h2>
        <div className="space-y-6 text-substrate-300 leading-relaxed">
          <div>
            <h3 className="font-mono text-lg text-substrate-100 mb-3">Providing Our Service</h3>
            <p>
              We use your BOM data to analyze components, search for availability across
              distributors, and provide intelligent sourcing recommendations. Your data enables
              us to deliver accurate pricing, availability, and alternative part suggestions.
            </p>
          </div>
          <div>
            <h3 className="font-mono text-lg text-substrate-100 mb-3">Improving Our AI</h3>
            <p>
              Aggregated and anonymized data may be used to improve our AI models and
              recommendation algorithms. We never use your identifiable data to train models
              without explicit consent.
            </p>
          </div>
          <div>
            <h3 className="font-mono text-lg text-substrate-100 mb-3">We Do Not Sell Your Data</h3>
            <p className="text-trace-400 font-medium">
              TraceSource will never sell, rent, or trade your personal information or BOM
              data to third parties for marketing purposes. Your data is yours.
            </p>
          </div>
        </div>
      </section>

      {/* Section 3: Data Storage & Security */}
      <section id="data-storage" className="mb-12 scroll-mt-8">
        <h2 className="font-mono text-2xl font-bold text-silkscreen mb-6 flex items-center gap-3">
          <span className="text-trace-500">03</span>
          Data Storage & Security
        </h2>
        <div className="space-y-4 text-substrate-300 leading-relaxed">
          <p>
            Your data is stored on secure servers with industry-standard encryption both in
            transit (TLS 1.3) and at rest (AES-256). We implement multiple layers of security
            including:
          </p>
          <ul className="list-none space-y-2 ml-4">
            <li className="flex items-start gap-3">
              <span className="text-trace-500 mt-1">&#8226;</span>
              <span>Encrypted database storage with regular security audits</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-trace-500 mt-1">&#8226;</span>
              <span>Access controls and authentication mechanisms</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-trace-500 mt-1">&#8226;</span>
              <span>Regular backups with encrypted off-site storage</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-trace-500 mt-1">&#8226;</span>
              <span>Monitoring and logging for suspicious activities</span>
            </li>
          </ul>
          <p>
            We retain your data for as long as your account is active or as needed to provide
            services. You may request deletion of your data at any time.
          </p>
        </div>
      </section>

      {/* Section 4: Third-Party Services */}
      <section id="third-party" className="mb-12 scroll-mt-8">
        <h2 className="font-mono text-2xl font-bold text-silkscreen mb-6 flex items-center gap-3">
          <span className="text-trace-500">04</span>
          Third-Party Services
        </h2>
        <div className="space-y-6 text-substrate-300 leading-relaxed">
          <p>
            To provide our services, we integrate with the following third-party providers:
          </p>
          <div>
            <h3 className="font-mono text-lg text-substrate-100 mb-3">AI Analysis (OpenAI)</h3>
            <p>
              We use OpenAI&apos;s API to analyze BOM data and provide intelligent recommendations.
              Component data is processed through their API but is not used to train their
              models per our enterprise agreement.
            </p>
          </div>
          <div>
            <h3 className="font-mono text-lg text-substrate-100 mb-3">Part Distributors</h3>
            <p>
              We query electronic component distributors (such as Mouser, DigiKey, and others)
              to retrieve real-time pricing and availability. Only the necessary part numbers
              and specifications are shared to fulfill search requests.
            </p>
          </div>
          <p>
            Each third-party service has its own privacy policy governing their use of data.
            We carefully select partners who maintain strong privacy and security practices.
          </p>
        </div>
      </section>

      {/* Section 5: Your Rights */}
      <section id="your-rights" className="mb-12 scroll-mt-8">
        <h2 className="font-mono text-2xl font-bold text-silkscreen mb-6 flex items-center gap-3">
          <span className="text-trace-500">05</span>
          Your Rights
        </h2>
        <div className="space-y-4 text-substrate-300 leading-relaxed">
          <p>
            You have the following rights regarding your personal data:
          </p>
          <ul className="list-none space-y-3 ml-4">
            <li className="flex items-start gap-3">
              <span className="font-mono text-trace-500 text-sm font-bold">ACCESS</span>
              <span>Request a copy of all personal data we hold about you</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="font-mono text-trace-500 text-sm font-bold">DELETE</span>
              <span>Request deletion of your account and all associated data</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="font-mono text-trace-500 text-sm font-bold">EXPORT</span>
              <span>Download your BOM data in standard formats (CSV, JSON)</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="font-mono text-trace-500 text-sm font-bold">CORRECT</span>
              <span>Update or correct any inaccurate personal information</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="font-mono text-trace-500 text-sm font-bold">OBJECT</span>
              <span>Opt out of certain data processing activities</span>
            </li>
          </ul>
          <p>
            To exercise any of these rights, please contact us using the information provided
            below. We will respond to your request within 30 days.
          </p>
        </div>
      </section>

      {/* Section 6: Cookies */}
      <section id="cookies" className="mb-12 scroll-mt-8">
        <h2 className="font-mono text-2xl font-bold text-silkscreen mb-6 flex items-center gap-3">
          <span className="text-trace-500">06</span>
          Cookies
        </h2>
        <div className="space-y-4 text-substrate-300 leading-relaxed">
          <p>
            We use minimal, functional cookies that are essential for the operation of our
            platform. These include:
          </p>
          <ul className="list-none space-y-2 ml-4">
            <li className="flex items-start gap-3">
              <span className="text-trace-500 mt-1">&#8226;</span>
              <span><strong className="text-substrate-100">Session cookies:</strong> To keep you logged in during your visit</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-trace-500 mt-1">&#8226;</span>
              <span><strong className="text-substrate-100">Security cookies:</strong> To protect against cross-site request forgery</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-trace-500 mt-1">&#8226;</span>
              <span><strong className="text-substrate-100">Preference cookies:</strong> To remember your display and interface preferences</span>
            </li>
          </ul>
          <p>
            We do not use tracking cookies, advertising cookies, or third-party analytics
            cookies that follow you across websites. Your browsing activity on TraceSource
            stays on TraceSource.
          </p>
        </div>
      </section>

      {/* Section 7: Contact */}
      <section id="contact" className="mb-12 scroll-mt-8">
        <h2 className="font-mono text-2xl font-bold text-silkscreen mb-6 flex items-center gap-3">
          <span className="text-trace-500">07</span>
          Contact Us
        </h2>
        <div className="space-y-4 text-substrate-300 leading-relaxed">
          <p>
            If you have questions about this Privacy Policy, your personal data, or would like
            to exercise your rights, please contact us:
          </p>
          <div className="p-6 rounded-lg border border-trace-900/50 bg-[#171717]/50">
            <p className="font-mono text-substrate-100">TraceSource Privacy Team</p>
            <p className="mt-2">
              Email:{" "}
              <a
                href="mailto:privacy@tracesource.io"
                className="text-trace-500 hover:text-trace-400 transition-colors"
              >
                privacy@tracesource.io
              </a>
            </p>
          </div>
          <p>
            We will respond to all legitimate requests within 30 days. Occasionally it may take
            longer if your request is particularly complex or you have made multiple requests.
          </p>
        </div>
      </section>

      {/* Back to top */}
      <div className="pt-8 border-t border-trace-900/50">
        <Link
          href="/terms"
          className="text-trace-500 hover:text-trace-400 transition-colors font-mono text-sm"
        >
          View Terms of Service &rarr;
        </Link>
      </div>
    </div>
  );
}
