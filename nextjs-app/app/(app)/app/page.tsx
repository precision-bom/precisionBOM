"use client";

import { useState } from "react";
import FileUpload from "@/components/FileUpload";
import BomSuggestions from "@/components/BomSuggestions";
import { BomSuggestionResult } from "@/types/bom";

export default function AppDashboard() {
  const [suggestionResult, setSuggestionResult] =
    useState<BomSuggestionResult | null>(null);

  const handleSuggestionsReady = (result: BomSuggestionResult) => {
    setSuggestionResult(result);
  };

  const handleReset = () => {
    setSuggestionResult(null);
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-mono font-semibold text-silkscreen">
            BOM Sourcing
          </h1>
          <p className="text-substrate-400 mt-1 text-sm">
            Upload a BOM and get AI-powered sourcing suggestions
          </p>
        </div>
        {suggestionResult && (
          <button
            onClick={handleReset}
            className="px-4 py-2 text-sm font-mono text-substrate-400 hover:text-silkscreen hover:bg-substrate-800 rounded-lg transition-colors border border-substrate-700"
          >
            Start Over
          </button>
        )}
      </div>

      {!suggestionResult ? (
        <div className="max-w-xl mx-auto">
          <FileUpload onSuggestionsReady={handleSuggestionsReady} />
        </div>
      ) : (
        <BomSuggestions result={suggestionResult} />
      )}
    </div>
  );
}
