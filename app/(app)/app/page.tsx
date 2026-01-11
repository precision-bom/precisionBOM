"use client";

import { useState } from "react";
import FileUpload from "@/components/FileUpload";
import BomSuggestions from "@/components/BomSuggestions";
import PaymentTab from "@/components/PaymentTab";
import { BomSuggestionResult } from "@/types/bom";

export default function AppDashboard() {
  const [activeTab, setActiveTab] = useState<"sourcing" | "payment">("sourcing");
  const [suggestionResult, setSuggestionResult] =
    useState<BomSuggestionResult | null>(null);

  const handleSuggestionsReady = (result: BomSuggestionResult) => {
    setSuggestionResult(result);
  };

  const handleReset = () => {
    setSuggestionResult(null);
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl font-mono">
      <div className="flex items-center justify-between mb-8 border-b border-substrate-800 pb-6">
        <div>
          <h1 className="text-2xl font-mono font-semibold text-silkscreen uppercase tracking-tighter">
            PrecisionBOM | Terminal
          </h1>
          <p className="text-substrate-400 mt-1 text-[10px] uppercase tracking-widest">
            AI-Powered Forensic Sourcing Engine
          </p>
        </div>
        
        <div className="flex gap-4">
          <div className="flex bg-substrate-900 border border-substrate-800 rounded-lg p-1">
            <button 
              onClick={() => setActiveTab("sourcing")}
              className={`px-4 py-1 text-[10px] uppercase font-bold rounded transition-all ${
                activeTab === "sourcing" ? "bg-substrate-700 text-white" : "text-substrate-500 hover:text-substrate-300"
              }`}
            >
              Sourcing
            </button>
            <button 
              onClick={() => setActiveTab("payment")}
              className={`px-4 py-1 text-[10px] uppercase font-bold rounded transition-all ${
                activeTab === "payment" ? "bg-substrate-700 text-white" : "text-substrate-500 hover:text-substrate-300"
              }`}
            >
              Subscription
            </button>
          </div>

          {suggestionResult && (
            <button
              onClick={handleReset}
              className="px-4 py-2 text-xs font-mono text-substrate-400 hover:text-silkscreen hover:bg-substrate-800 rounded-lg transition-colors border border-substrate-700"
            >
              Reset Strike
            </button>
          )}
        </div>
      </div>

      {activeTab === "payment" ? (
        <div className="max-w-2xl mx-auto">
          <PaymentTab />
        </div>
      ) : (
        <>
          {!suggestionResult ? (
            <div className="max-w-xl mx-auto">
              <FileUpload onSuggestionsReady={handleSuggestionsReady} />
            </div>
          ) : (
            <BomSuggestions result={suggestionResult} />
          )}
        </>
      )}
    </div>
  );
}

