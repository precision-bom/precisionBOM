"use client";

import { useState } from "react";

interface LeadCaptureFormProps {
  source?: string;
}

export function LeadCaptureForm({ source = "landing" }: LeadCaptureFormProps) {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email) return;

    setStatus("loading");

    try {
      const response = await fetch("/api/leads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, source }),
      });

      const data = await response.json();

      if (data.success) {
        setStatus("success");
        setMessage(data.message || "You're on the list!");
        setEmail("");
      } else {
        setStatus("error");
        setMessage(data.error || "Something went wrong");
      }
    } catch {
      setStatus("error");
      setMessage("Connection failed. Please try again.");
    }
  };

  if (status === "success") {
    return (
      <div className="border-4 border-green-500 bg-black p-6 text-center">
        <pre className="font-mono text-sm text-green-500 mb-2">
{`┌────────────────────────┐
│  `}<span className="text-green-400">[✓] CONFIRMED</span>{`        │
└────────────────────────┘`}
        </pre>
        <p className="font-sans text-neutral-300">{message}</p>
        <p className="font-mono text-xs text-neutral-500 mt-2">We&apos;ll be in touch soon.</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-md mx-auto">
      <div className="border-4 border-white bg-black p-6 hover:border-green-500/50 transition-colors duration-300">
        <pre className="font-mono text-xs text-center mb-4">
          <span className="text-green-500">┌────────────────────────┐</span>
          {"\n"}
          <span className="text-green-500">│</span>
          <span className="text-white">  GET EARLY ACCESS      </span>
          <span className="text-green-500">│</span>
          {"\n"}
          <span className="text-green-500">└────────────────────────┘</span>
        </pre>

        <div className="flex flex-col sm:flex-row gap-3">
          <input
            type="email"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              if (status === "error") setStatus("idle");
            }}
            placeholder="engineer@company.com"
            className="flex-1 px-4 py-3 bg-black border-2 border-white text-white font-mono text-sm placeholder:text-neutral-600 focus:outline-none focus:border-green-500 transition-colors"
            disabled={status === "loading"}
          />
          <button
            type="submit"
            disabled={status === "loading" || !email}
            className="px-6 py-3 bg-green-500 text-black font-mono text-sm font-bold uppercase tracking-wider border-2 border-green-500 hover:bg-black hover:text-green-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
          >
            {status === "loading" ? "..." : "NOTIFY ME"}
          </button>
        </div>

        {status === "error" && (
          <p className="font-mono text-xs text-red-500 mt-3 text-center">
            [ERROR] {message}
          </p>
        )}

        <p className="font-mono text-xs text-neutral-500 mt-4 text-center">
          Be first to know when new features drop.
        </p>
      </div>
    </form>
  );
}
