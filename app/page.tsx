"use client";

import { useState } from "react";
import FileUpload from "@/components/FileUpload";
import BomSuggestions from "@/components/BomSuggestions";
import { BomSuggestionResult } from "@/types/bom";

export default function Home() {
  const [suggestionResult, setSuggestionResult] = useState<BomSuggestionResult | null>(null);

  const handleSuggestionsReady = (result: BomSuggestionResult) => {
    setSuggestionResult(result);
  };

  const handleReset = () => {
    setSuggestionResult(null);
  };

  return (
    <main className="container mx-auto px-4 py-8 max-w-5xl">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            BOM Sourcing Tool
          </h1>
          <p className="text-gray-500 mt-1">
            Upload a BOM and get concrete sourcing suggestions
          </p>
        </div>
        {suggestionResult && (
          <button
            onClick={handleReset}
            className="px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
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
    </main>
  );
}
