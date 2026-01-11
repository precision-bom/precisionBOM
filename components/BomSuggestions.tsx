"use client";

import { useState } from "react";
import {
  BomSuggestionResult,
  RealizedBom,
  RealizedLineItem,
} from "@/types/bom";

interface BomSuggestionsProps {
  result: BomSuggestionResult;
}

export default function BomSuggestions({ result }: BomSuggestionsProps) {
  const [expandedBom, setExpandedBom] = useState<string | null>(
    result.suggestions[0]?.id || null
  );
  const [showReasoning, setShowReasoning] = useState(false);

  const toggleExpand = (bomId: string) => {
    setExpandedBom(expandedBom === bomId ? null : bomId);
  };

  return (
    <div className="space-y-6">
      {/* Agent Reasoning */}
      {result.reasoning && result.reasoning.length > 0 && (
        <div className="bg-substrate-900 rounded-lg border border-trace-500/30 overflow-hidden">
          <button
            onClick={() => setShowReasoning(!showReasoning)}
            className="w-full p-4 flex items-center justify-between text-left hover:bg-substrate-800/50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-trace-500/20 flex items-center justify-center">
                <svg
                  className="w-4 h-4 text-trace-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                  />
                </svg>
              </div>
              <span className="font-mono font-semibold text-trace-400">
                Agent Reasoning
              </span>
              <span className="text-substrate-500 text-sm font-mono">
                ({result.reasoning.length} steps)
              </span>
            </div>
            <span
              className={`text-trace-500 transition-transform ${
                showReasoning ? "rotate-180" : ""
              }`}
            >
              <svg
                className="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </span>
          </button>

          {showReasoning && (
            <div className="px-4 pb-4">
              <div className="bg-substrate-950 rounded-lg p-4 max-h-64 overflow-y-auto border border-substrate-800">
                <ol className="space-y-2 text-sm">
                  {result.reasoning.map((step, index) => (
                    <li key={index} className="flex gap-3">
                      <span className="text-trace-500/60 font-mono text-xs mt-0.5 w-5 flex-shrink-0">
                        {String(index + 1).padStart(2, "0")}
                      </span>
                      <span className="text-substrate-300">{step}</span>
                    </li>
                  ))}
                </ol>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Summary */}
      <div className="bg-substrate-900 rounded-lg border border-substrate-700 p-6">
        <h2 className="text-lg font-mono font-semibold text-silkscreen mb-4">
          BOM Analysis
        </h2>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div className="bg-substrate-800 rounded-lg p-4 border border-substrate-700">
            <div className="text-2xl font-mono font-bold text-silkscreen">
              {result.originalItems.length}
            </div>
            <div className="text-sm text-substrate-500 font-mono">
              Total Items
            </div>
          </div>
          <div className="bg-trace-500/10 rounded-lg p-4 border border-trace-500/30">
            <div className="text-2xl font-mono font-bold text-trace-400">
              {result.originalItems.length - result.unmatchedItems.length}
            </div>
            <div className="text-sm text-trace-500 font-mono">Matched</div>
          </div>
          <div className="bg-copper-400/10 rounded-lg p-4 border border-copper-400/30">
            <div className="text-2xl font-mono font-bold text-copper-400">
              {result.unmatchedItems.length}
            </div>
            <div className="text-sm text-copper-500 font-mono">Unmatched</div>
          </div>
        </div>

        {result.unmatchedItems.length > 0 && (
          <div className="mt-4 p-3 bg-copper-400/10 border border-copper-400/30 rounded-lg">
            <div className="text-sm font-mono font-medium text-copper-400 mb-1">
              Unmatched items:
            </div>
            <ul className="text-sm text-copper-300/80 space-y-1 font-mono">
              {result.unmatchedItems.map((item) => (
                <li key={item.id}>
                  • {item.partNumber || item.mpn || item.description}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Suggested BOMs */}
      <div className="space-y-4">
        <h2 className="text-lg font-mono font-semibold text-silkscreen">
          Optimized Configurations ({result.suggestions.length})
        </h2>

        {result.suggestions.length === 0 ? (
          <div className="bg-substrate-900 border border-substrate-700 rounded-lg p-6 text-center text-substrate-500 font-mono">
            No BOM configurations could be generated. Check if the parts can be
            found in the distributor database.
          </div>
        ) : (
          result.suggestions.map((bom) => (
            <BomCard
              key={bom.id}
              bom={bom}
              isExpanded={expandedBom === bom.id}
              onToggle={() => toggleExpand(bom.id)}
            />
          ))
        )}
      </div>
    </div>
  );
}

interface BomCardProps {
  bom: RealizedBom;
  isExpanded: boolean;
  onToggle: () => void;
}

function BomCard({ bom, isExpanded, onToggle }: BomCardProps) {
  return (
    <div className="bg-substrate-900 border border-substrate-700 rounded-lg overflow-hidden hover:border-substrate-600 transition-colors">
      {/* Header */}
      <div
        className="p-4 cursor-pointer hover:bg-substrate-800/50 transition-colors"
        onClick={onToggle}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div
              className={`w-12 h-12 rounded-lg flex items-center justify-center font-mono font-bold text-lg ${
                bom.score >= 70
                  ? "bg-trace-500/20 text-trace-400 border border-trace-500/30"
                  : bom.score >= 50
                  ? "bg-copper-400/20 text-copper-400 border border-copper-400/30"
                  : "bg-substrate-700 text-substrate-400 border border-substrate-600"
              }`}
            >
              {bom.score}
            </div>
            <div className="flex-1">
              <h3 className="font-mono font-semibold text-silkscreen">
                {bom.name}
              </h3>
              <p className="text-sm text-substrate-400 line-clamp-2">
                {bom.description}
              </p>
            </div>
          </div>
          <div className="text-right ml-4">
            <div className="text-xl font-mono font-bold text-silkscreen">
              ${bom.totalCost.toFixed(2)}
            </div>
            <div className="flex items-center gap-2 text-sm font-mono">
              {bom.allInStock ? (
                <span className="text-trace-400">All in stock</span>
              ) : (
                <span className="text-copper-400">Partial stock</span>
              )}
              <span className="text-substrate-600">•</span>
              <span className="text-substrate-500">
                {bom.distributors.length} distributor
                {bom.distributors.length !== 1 ? "s" : ""}
              </span>
            </div>
          </div>
        </div>

        {/* Distributors badges */}
        <div className="mt-3 flex flex-wrap gap-2">
          {bom.distributors.map((dist) => (
            <span
              key={dist}
              className="px-2 py-1 bg-substrate-800 text-substrate-300 text-xs font-mono rounded border border-substrate-700"
            >
              {dist}
            </span>
          ))}
        </div>
      </div>

      {/* Expanded details */}
      {isExpanded && (
        <div className="border-t border-substrate-700">
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-substrate-800">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-mono font-medium text-substrate-400 uppercase tracking-wider">
                    Part
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-mono font-medium text-substrate-400 uppercase tracking-wider">
                    MPN
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-mono font-medium text-substrate-400 uppercase tracking-wider">
                    Qty
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-mono font-medium text-substrate-400 uppercase tracking-wider">
                    Distributor
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-mono font-medium text-substrate-400 uppercase tracking-wider">
                    Stock
                  </th>
                  <th className="px-4 py-2 text-right text-xs font-mono font-medium text-substrate-400 uppercase tracking-wider">
                    Unit
                  </th>
                  <th className="px-4 py-2 text-right text-xs font-mono font-medium text-substrate-400 uppercase tracking-wider">
                    Total
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-substrate-800">
                {bom.lineItems.map((item) => (
                  <LineItemRow key={item.bomItemId} item={item} />
                ))}
              </tbody>
              <tfoot className="bg-substrate-800">
                <tr>
                  <td
                    colSpan={6}
                    className="px-4 py-3 text-right font-mono font-semibold text-substrate-300"
                  >
                    Total:
                  </td>
                  <td className="px-4 py-3 text-right font-mono font-bold text-lg text-trace-400">
                    ${bom.totalCost.toFixed(2)}
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function LineItemRow({ item }: { item: RealizedLineItem }) {
  return (
    <tr className="hover:bg-substrate-800/50 transition-colors">
      <td className="px-4 py-2 text-sm">
        <div className="font-mono font-medium text-silkscreen">
          {item.bomItem.partNumber || item.bomItem.description}
        </div>
        <div className="text-xs text-substrate-500 truncate max-w-[200px]">
          {item.offer.description}
        </div>
      </td>
      <td className="px-4 py-2 text-sm font-mono text-substrate-400">
        {item.offer.mpn}
      </td>
      <td className="px-4 py-2 text-sm font-mono text-silkscreen">
        {item.bomItem.quantity}
      </td>
      <td className="px-4 py-2 text-sm">
        <a
          href={item.offer.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-trace-400 hover:text-trace-300 font-mono transition-colors"
        >
          {item.offer.distributor}
        </a>
      </td>
      <td className="px-4 py-2 text-sm font-mono">
        <span className={item.inStock ? "text-trace-400" : "text-copper-400"}>
          {item.offer.stock.toLocaleString()}
        </span>
      </td>
      <td className="px-4 py-2 text-sm text-right font-mono text-substrate-300">
        ${item.unitPrice.toFixed(2)}
      </td>
      <td className="px-4 py-2 text-sm text-right font-mono font-medium text-silkscreen">
        ${item.lineTotal.toFixed(2)}
      </td>
    </tr>
  );
}
