import OpenAI from "openai";
import {
  BomItem,
  PartOffer,
  RealizedBom,
  RealizedLineItem,
  BomSuggestionResult,
} from "@/types/bom";
import {
  pythonClient,
  ProviderResult,
  getConfiguredProviders,
} from "./python-client";

const STRIKE_COST = 50;

interface AgentState {
  bomItems: BomItem[];
  offersMap: { [bomItemId: string]: PartOffer[] };
  reasoning: string[];
  suggestions: RealizedBom[];
  unmatchedItems: BomItem[];
}

interface PartAnalysis {
  bomItemId: string;
  query: string;
  isAmbiguous: boolean;
  suggestedSearchTerms: string[];
  notes: string;
}

interface OptimizationStrategy {
  name: string;
  description: string;
  selections: { [bomItemId: string]: number };
  reasoning: string;
}

export class BomAgent {
  private openai: OpenAI | null = null;
  private state: AgentState;

  constructor() {
    this.state = {
      bomItems: [],
      offersMap: {},
      reasoning: [],
      suggestions: [],
      unmatchedItems: [],
    };
  }

  private getOpenAI(): OpenAI {
    if (!this.openai) {
      const apiKey = process.env.OPENAI_API_KEY;
      if (!apiKey) throw new Error("OPENAI_API_KEY not configured");
      this.openai = new OpenAI({ apiKey });
    }
    return this.openai;
  }

  private log(message: string) {
    console.log(`[BomAgent] ${message}`);
    this.state.reasoning.push(message);
  }

  /**
   * Authorize and Deduct thermodynamic capital for the strike
   */
  private async executeThermodynamicStrike(): Promise<boolean> {
    const address = localStorage.getItem('forensic_identity');
    const signature = localStorage.getItem('forensic_signature');
    const nonce = localStorage.getItem('forensic_nonce');

    if (!address || !signature || !nonce) {
      this.log("IDENTITY REQUIRED: No forensic signature found. Please connect wallet.");
      return false;
    }

    try {
      this.log(`Authorizing strike for ${address.slice(0,6)}... (-${STRIKE_COST} T)`);
      const response = await fetch('/api/gatekeeper', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ address, signature, nonce, action: 'deduct', amount: STRIKE_COST })
      });

      const data = await response.json();
      if (response.status === 200) {
        this.log(`STRIKE GRANTED: Remaining Capital: ${data.tokens} T`);
        return true;
      } else {
        this.log(`STRIKE REJECTED: ${data.message || 'Insufficient funds'}. Please refill at the Subscription tab.`);
        return false;
      }
    } catch (error) {
      this.log("FORENSIC ERROR: Gateway unreachable.");
      return false;
    }
  }

  async suggestBoms(items: BomItem[]): Promise<BomSuggestionResult & { reasoning: string[] }> {
    this.state.bomItems = items;
    this.log(`Initiating Thermodynamic Sourcing Strike for ${items.length} items...`);

    // GATING: Enforce strike cost
    const authorized = await this.executeThermodynamicStrike();
    if (!authorized) {
      return {
        originalItems: items,
        suggestions: [],
        unmatchedItems: items,
        reasoning: this.state.reasoning,
      };
    }

    // PROCEED WITH INTELLIGENCE
    const analysis = await this.analyzeBomItems(items);
    await this.searchAllParts(items, analysis);
    const strategies = await this.generateOptimizationStrategies();
    this.state.suggestions = this.realizeStrategies(strategies);
    this.state.unmatchedItems = items.filter(
      (item) => !this.state.offersMap[item.id] || this.state.offersMap[item.id].length === 0
    );

    this.log(`Strike Complete. Generated ${this.state.suggestions.length} configurations.`);

    return {
      originalItems: items,
      suggestions: this.state.suggestions,
      unmatchedItems: this.state.unmatchedItems,
      reasoning: this.state.reasoning,
    };
  }

  private async analyzeBomItems(items: BomItem[]): Promise<PartAnalysis[]> {
    this.log("Step 1: AI Ambiguity Scan...");
    const openai = this.getOpenAI();
    const bomSummary = items.map((item) => ({
      id: item.id,
      partNumber: item.partNumber,
      description: item.description,
      manufacturer: item.manufacturer,
      mpn: item.mpn,
      quantity: item.quantity,
    }));

    const response = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        {
          role: "system",
          content: `You are an electronics sourcing expert. Analyze the BOM items and return optimal search terms in JSON format.`,
        },
        {
          role: "user",
          content: JSON.stringify(bomSummary),
        },
      ],
      response_format: { type: "json_object" },
      temperature: 0.3,
    });

    const result = JSON.parse(response.choices[0]?.message?.content || "{}");
    return result.analysis || items.map((item) => ({
      bomItemId: item.id,
      query: item.mpn || item.partNumber || item.description,
      isAmbiguous: false,
      suggestedSearchTerms: [],
      notes: "",
    }));
  }

  private toPartOffer(result: ProviderResult): PartOffer {
    return {
      mpn: result.mpn,
      manufacturer: result.manufacturer,
      description: result.description,
      price: result.price,
      currency: result.currency,
      stock: result.stock,
      minQuantity: result.min_quantity,
      provider: result.provider,
      distributor: result.distributor,
      url: result.url,
    };
  }

  private async searchAllParts(items: BomItem[], analysis: PartAnalysis[]): Promise<void> {
    const providerNames = await getConfiguredProviders();
    this.log(`Step 2: Cross-Provider Pulse (${providerNames.join(", ")})`);

    for (const item of items) {
      this.state.offersMap[item.id] = [];
    }

    const itemSearches = items.map(async (item) => {
      const itemAnalysis = analysis.find((a) => a.bomItemId === item.id);
      const query = itemAnalysis?.query || item.mpn || item.partNumber || item.description;
      try {
        const response = await pythonClient.searchParts({ query });
        return { itemId: item.id, offers: response.results.map((r) => this.toPartOffer(r)) };
      } catch (error) {
        return { itemId: item.id, offers: [] };
      }
    });

    const results = await Promise.all(itemSearches);
    for (const { itemId, offers } of results) {
      this.state.offersMap[itemId].push(...offers);
    }
  }

  private async generateOptimizationStrategies(): Promise<OptimizationStrategy[]> {
    this.log("Step 3: Joint Reasoning Strike...");
    const openai = this.getOpenAI();
    const bomWithOffers = this.state.bomItems
      .filter((item) => this.state.offersMap[item.id].length > 0)
      .map((item) => ({
        bomItemId: item.id,
        quantity: item.quantity,
        offers: this.state.offersMap[item.id].slice(0, 3).map((o, i) => ({
          index: i, mpn: o.mpn, distributor: o.distributor, price: o.price, stock: o.stock
        })),
      }));

    if (bomWithOffers.length === 0) return [];

    const response = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: "Optimize the BOM sourcing strategy. Return JSON." },
        { role: "user", content: JSON.stringify(bomWithOffers) },
      ],
      response_format: { type: "json_object" },
      temperature: 0.5,
    });

    const result = JSON.parse(response.choices[0]?.message?.content || "{}");
    return result.strategies || [];
  }

  private realizeStrategies(strategies: OptimizationStrategy[]): RealizedBom[] {
    const realizedBoms: RealizedBom[] = [];
    for (const strategy of strategies) {
      const lineItems: RealizedLineItem[] = [];
      for (const item of this.state.bomItems) {
        const offers = this.state.offersMap[item.id];
        if (!offers || offers.length === 0) continue;
        const offer = offers[Math.min(strategy.selections[item.id] ?? 0, offers.length - 1)];
        lineItems.push({
          bomItemId: item.id, bomItem: item, offer, unitPrice: offer.price,
          lineTotal: item.quantity * offer.price, inStock: offer.stock >= item.quantity,
        });
      }
      if (lineItems.length === 0) continue;
      realizedBoms.push({
        id: `bom-${Math.random().toString(36).slice(2)}`,
        name: strategy.name, description: strategy.reasoning || strategy.description,
        lineItems, totalCost: lineItems.reduce((sum, i) => sum + i.lineTotal, 0),
        currency: "USD", allInStock: lineItems.every((i) => i.inStock),
        distributors: Array.from(new Set(lineItems.map((i) => i.offer.distributor))),
        score: Math.round(Math.random() * 100),
      });
    }
    return realizedBoms.sort((a, b) => b.score - a.score);
  }
}

export async function suggestBomsWithAgent(
  items: BomItem[]
): Promise<BomSuggestionResult & { reasoning: string[] }> {
  const agent = new BomAgent();
  return agent.suggestBoms(items);
}