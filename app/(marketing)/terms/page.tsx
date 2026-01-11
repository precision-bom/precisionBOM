import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms of Service | TraceSource",
  description: "Terms and conditions for using the TraceSource BOM sourcing platform.",
};

const sections = [
  { id: "service-description", title: "Service Description" },
  { id: "account-responsibilities", title: "Account Responsibilities" },
  { id: "acceptable-use", title: "Acceptable Use" },
  { id: "intellectual-property", title: "Intellectual Property" },
  { id: "ai-disclaimer", title: "AI-Generated Content Disclaimer" },
  { id: "limitation-liability", title: "Limitation of Liability" },
  { id: "changes", title: "Changes to Terms" },
  { id: "governing-law", title: "Governing Law" },
  { id: "contact", title: "Contact" },
];

export default function TermsPage() {
  return (
    <div className="container mx-auto px-4 py-12 max-w-4xl">
      {/* Page Header */}
      <div className="mb-12">
        <h1 className="font-mono text-4xl font-bold text-silkscreen mb-4">
          Terms of Service
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
          Welcome to TraceSource. By accessing or using our BOM sourcing platform, you agree to be
          bound by these Terms of Service. Please read them carefully before using our services.
          If you do not agree to these terms, you may not use TraceSource.
        </p>
      </div>

      {/* Section 1: Service Description */}
      <section id="service-description" className="mb-12 scroll-mt-8">
        <h2 className="font-mono text-2xl font-bold text-silkscreen mb-6 flex items-center gap-3">
          <span className="text-trace-500">01</span>
          Service Description
        </h2>
        <div className="space-y-4 text-substrate-300 leading-relaxed">
          <p>
            TraceSource is a Bill of Materials (BOM) sourcing platform that helps electronics
            engineers and procurement professionals find and source electronic components.
            Our services include:
          </p>
          <ul className="list-none space-y-2 ml-4">
            <li className="flex items-start gap-3">
              <span className="text-trace-500 mt-1">&#8226;</span>
              <span>BOM file upload and parsing</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-trace-500 mt-1">&#8226;</span>
              <span>AI-powered component analysis and recommendations</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-trace-500 mt-1">&#8226;</span>
              <span>Real-time pricing and availability data from multiple distributors</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-trace-500 mt-1">&#8226;</span>
              <span>Alternative part suggestions and cross-referencing</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-trace-500 mt-1">&#8226;</span>
              <span>BOM optimization and cost analysis</span>
            </li>
          </ul>
          <p>
            We reserve the right to modify, suspend, or discontinue any part of our services
            at any time with reasonable notice.
          </p>
        </div>
      </section>

      {/* Section 2: Account Responsibilities */}
      <section id="account-responsibilities" className="mb-12 scroll-mt-8">
        <h2 className="font-mono text-2xl font-bold text-silkscreen mb-6 flex items-center gap-3">
          <span className="text-trace-500">02</span>
          Account Responsibilities
        </h2>
        <div className="space-y-4 text-substrate-300 leading-relaxed">
          <p>When you create an account with TraceSource, you agree to:</p>
          <ul className="list-none space-y-2 ml-4">
            <li className="flex items-start gap-3">
              <span className="text-trace-500 mt-1">&#8226;</span>
              <span>Provide accurate, current, and complete registration information</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-trace-500 mt-1">&#8226;</span>
              <span>Maintain the security of your account credentials</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-trace-500 mt-1">&#8226;</span>
              <span>Notify us immediately of any unauthorized access to your account</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-trace-500 mt-1">&#8226;</span>
              <span>Accept responsibility for all activities that occur under your account</span>
            </li>
          </ul>
          <p>
            You must be at least 18 years old or have reached the age of majority in your
            jurisdiction to use TraceSource. By using our services, you represent that you
            meet these requirements.
          </p>
        </div>
      </section>

      {/* Section 3: Acceptable Use */}
      <section id="acceptable-use" className="mb-12 scroll-mt-8">
        <h2 className="font-mono text-2xl font-bold text-silkscreen mb-6 flex items-center gap-3">
          <span className="text-trace-500">03</span>
          Acceptable Use
        </h2>
        <div className="space-y-4 text-substrate-300 leading-relaxed">
          <p>You agree to use TraceSource only for lawful purposes. You may not:</p>
          <div className="p-4 rounded-lg border border-red-900/30 bg-red-950/20">
            <h4 className="font-mono text-red-400 mb-3">Prohibited Activities</h4>
            <ul className="list-none space-y-2">
              <li className="flex items-start gap-3">
                <span className="text-red-500 mt-1">&#10007;</span>
                <span>Abuse or overload our systems through automated scraping beyond normal usage</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-red-500 mt-1">&#10007;</span>
                <span>Attempt to gain unauthorized access to our systems or other users&apos; accounts</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-red-500 mt-1">&#10007;</span>
                <span>Use our service to collect data for competing services</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-red-500 mt-1">&#10007;</span>
                <span>Transmit malware, viruses, or other malicious code</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-red-500 mt-1">&#10007;</span>
                <span>Violate any applicable laws or regulations</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-red-500 mt-1">&#10007;</span>
                <span>Impersonate any person or entity</span>
              </li>
            </ul>
          </div>
          <p>
            We reserve the right to suspend or terminate accounts that violate these terms
            without prior notice.
          </p>
        </div>
      </section>

      {/* Section 4: Intellectual Property */}
      <section id="intellectual-property" className="mb-12 scroll-mt-8">
        <h2 className="font-mono text-2xl font-bold text-silkscreen mb-6 flex items-center gap-3">
          <span className="text-trace-500">04</span>
          Intellectual Property
        </h2>
        <div className="space-y-4 text-substrate-300 leading-relaxed">
          <div className="p-4 rounded-lg border border-trace-900/50 bg-trace-950/20">
            <h4 className="font-mono text-trace-400 mb-3">Your Content Ownership</h4>
            <p className="text-trace-200">
              Your BOMs are yours. You retain all ownership rights to the Bill of Materials
              data you upload to TraceSource. We do not claim any ownership over your content.
            </p>
          </div>
          <p>
            By uploading content to TraceSource, you grant us a limited license to process,
            analyze, and display your data solely for the purpose of providing our services
            to you.
          </p>
          <p>
            The TraceSource platform, including its design, features, code, and documentation,
            is owned by TraceSource and protected by intellectual property laws. You may not
            copy, modify, distribute, or create derivative works of our platform without
            explicit permission.
          </p>
        </div>
      </section>

      {/* Section 5: AI-Generated Content Disclaimer */}
      <section id="ai-disclaimer" className="mb-12 scroll-mt-8">
        <h2 className="font-mono text-2xl font-bold text-silkscreen mb-6 flex items-center gap-3">
          <span className="text-trace-500">05</span>
          AI-Generated Content Disclaimer
        </h2>
        <div className="space-y-4 text-substrate-300 leading-relaxed">
          <div className="p-4 rounded-lg border border-copper-900/50 bg-copper-950/20">
            <h4 className="font-mono text-copper-400 mb-3">Important Notice</h4>
            <p className="text-copper-200">
              Suggestions are suggestions. AI-generated recommendations should be verified
              before ordering components.
            </p>
          </div>
          <p>
            TraceSource uses artificial intelligence to analyze BOMs and provide component
            recommendations. While we strive for accuracy, AI-generated content may contain
            errors or inaccuracies. You acknowledge that:
          </p>
          <ul className="list-none space-y-2 ml-4">
            <li className="flex items-start gap-3">
              <span className="text-copper-500 mt-1">&#9888;</span>
              <span>AI suggestions are provided as guidance, not guarantees</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-copper-500 mt-1">&#9888;</span>
              <span>You should verify all component specifications before purchasing</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-copper-500 mt-1">&#9888;</span>
              <span>Alternative part suggestions may not be pin-for-pin compatible</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-copper-500 mt-1">&#9888;</span>
              <span>Pricing and availability data is subject to change</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-copper-500 mt-1">&#9888;</span>
              <span>Final sourcing decisions are your responsibility</span>
            </li>
          </ul>
          <p>
            TraceSource is not responsible for any losses, damages, or issues arising from
            reliance on AI-generated recommendations without proper verification.
          </p>
        </div>
      </section>

      {/* Section 6: Limitation of Liability */}
      <section id="limitation-liability" className="mb-12 scroll-mt-8">
        <h2 className="font-mono text-2xl font-bold text-silkscreen mb-6 flex items-center gap-3">
          <span className="text-trace-500">06</span>
          Limitation of Liability
        </h2>
        <div className="space-y-4 text-substrate-300 leading-relaxed">
          <p>
            To the maximum extent permitted by applicable law, TraceSource and its affiliates,
            officers, employees, and agents shall not be liable for:
          </p>
          <ul className="list-none space-y-2 ml-4">
            <li className="flex items-start gap-3">
              <span className="text-trace-500 mt-1">&#8226;</span>
              <span>Any indirect, incidental, special, consequential, or punitive damages</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-trace-500 mt-1">&#8226;</span>
              <span>Loss of profits, data, use, goodwill, or other intangible losses</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-trace-500 mt-1">&#8226;</span>
              <span>Damages resulting from unauthorized access to or use of our servers</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-trace-500 mt-1">&#8226;</span>
              <span>Interruption or cessation of transmission to or from our services</span>
            </li>
          </ul>
          <p>
            Our total liability for any claim arising from or relating to these terms or our
            services shall not exceed the amount you paid to TraceSource in the twelve months
            preceding the claim.
          </p>
          <p>
            The service is provided &quot;as is&quot; and &quot;as available&quot; without warranties of any
            kind, either express or implied.
          </p>
        </div>
      </section>

      {/* Section 7: Changes to Terms */}
      <section id="changes" className="mb-12 scroll-mt-8">
        <h2 className="font-mono text-2xl font-bold text-silkscreen mb-6 flex items-center gap-3">
          <span className="text-trace-500">07</span>
          Changes to Terms
        </h2>
        <div className="space-y-4 text-substrate-300 leading-relaxed">
          <p>
            We may update these Terms of Service from time to time. When we make changes, we will:
          </p>
          <ul className="list-none space-y-2 ml-4">
            <li className="flex items-start gap-3">
              <span className="text-trace-500 mt-1">&#8226;</span>
              <span>Update the &quot;Last updated&quot; date at the top of this page</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-trace-500 mt-1">&#8226;</span>
              <span>Notify you via email or through the platform for material changes</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-trace-500 mt-1">&#8226;</span>
              <span>Provide a reasonable period for you to review the changes</span>
            </li>
          </ul>
          <p>
            Your continued use of TraceSource after changes become effective constitutes
            acceptance of the revised terms. If you do not agree to the changes, you should
            discontinue use of our services.
          </p>
        </div>
      </section>

      {/* Section 8: Governing Law */}
      <section id="governing-law" className="mb-12 scroll-mt-8">
        <h2 className="font-mono text-2xl font-bold text-silkscreen mb-6 flex items-center gap-3">
          <span className="text-trace-500">08</span>
          Governing Law
        </h2>
        <div className="space-y-4 text-substrate-300 leading-relaxed">
          <p>
            These Terms of Service shall be governed by and construed in accordance with the
            laws of the State of Delaware, United States, without regard to its conflict of
            law provisions.
          </p>
          <p>
            Any disputes arising out of or relating to these terms or our services shall be
            resolved through binding arbitration in accordance with the rules of the American
            Arbitration Association. You agree to waive any right to a jury trial or to
            participate in a class action.
          </p>
          <p>
            If any provision of these terms is found to be unenforceable, the remaining
            provisions will continue in full force and effect.
          </p>
        </div>
      </section>

      {/* Section 9: Contact */}
      <section id="contact" className="mb-12 scroll-mt-8">
        <h2 className="font-mono text-2xl font-bold text-silkscreen mb-6 flex items-center gap-3">
          <span className="text-trace-500">09</span>
          Contact
        </h2>
        <div className="space-y-4 text-substrate-300 leading-relaxed">
          <p>
            If you have any questions about these Terms of Service, please contact us:
          </p>
          <div className="p-6 rounded-lg border border-trace-900/50 bg-[#171717]/50">
            <p className="font-mono text-substrate-100">TraceSource Legal Team</p>
            <p className="mt-2">
              Email:{" "}
              <a
                href="mailto:legal@tracesource.io"
                className="text-trace-500 hover:text-trace-400 transition-colors"
              >
                legal@tracesource.io
              </a>
            </p>
          </div>
        </div>
      </section>

      {/* Footer Links */}
      <div className="pt-8 border-t border-trace-900/50 flex justify-between items-center">
        <Link
          href="/privacy"
          className="text-trace-500 hover:text-trace-400 transition-colors font-mono text-sm"
        >
          &larr; View Privacy Policy
        </Link>
        <Link
          href="/"
          className="text-substrate-400 hover:text-trace-500 transition-colors font-mono text-sm"
        >
          Back to Home
        </Link>
      </div>
    </div>
  );
}
