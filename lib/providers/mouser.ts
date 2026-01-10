import { ProviderResult } from "@/types/bom";
import { PartProvider } from "./types";

const MOUSER_API_URL = "https://api.mouser.com/api/v1/search/keyword";

interface MouserSearchResponse {
  Errors: Array<{ Id: number; Code: string; Message: string }>;
  SearchResults: {
    NumberOfResult: number;
    Parts: MouserPart[];
  };
}

interface MouserPart {
  MouserPartNumber: string;
  ManufacturerPartNumber: string;
  Manufacturer: string;
  Description: string;
  DataSheetUrl: string;
  ProductDetailUrl: string;
  Availability: string;
  PriceBreaks: Array<{
    Quantity: number;
    Price: string;
    Currency: string;
  }>;
  Min: string;
  Mult: string;
}

export class MouserProvider implements PartProvider {
  name = "mouser";
  private apiKey: string;

  constructor() {
    this.apiKey = process.env.MOUSER_API_KEY || "";
  }

  async search(query: string): Promise<ProviderResult[]> {
    return this.executeSearch(query);
  }

  async searchByMPN(mpn: string, manufacturer?: string): Promise<ProviderResult[]> {
    // Mouser search works well with just MPN
    return this.executeSearch(mpn);
  }

  private async executeSearch(query: string): Promise<ProviderResult[]> {
    if (!this.apiKey) {
      throw new Error("Mouser API key not configured. Set MOUSER_API_KEY environment variable.");
    }

    const response = await fetch(`${MOUSER_API_URL}?apiKey=${this.apiKey}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        SearchByKeywordRequest: {
          keyword: query,
          records: 10,
          startingRecord: 0,
          searchOptions: "",
          searchWithYourSignUpLanguage: "",
        },
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Mouser API error: ${response.status} - ${errorText}`);
    }

    const data: MouserSearchResponse = await response.json();

    if (data.Errors && data.Errors.length > 0) {
      throw new Error(`Mouser API error: ${data.Errors[0].Message}`);
    }

    return this.transformResults(data);
  }

  private transformResults(data: MouserSearchResponse): ProviderResult[] {
    const results: ProviderResult[] = [];

    if (!data.SearchResults?.Parts) {
      return results;
    }

    for (const part of data.SearchResults.Parts) {
      // Parse availability (e.g., "2500 In Stock")
      const stockMatch = part.Availability.match(/(\d+)/);
      const stock = stockMatch ? parseInt(stockMatch[1], 10) : 0;

      // Get the lowest price from price breaks
      if (!part.PriceBreaks || part.PriceBreaks.length === 0) continue;

      const lowestPriceBreak = part.PriceBreaks[0]; // First is usually qty 1
      const price = parseFloat(lowestPriceBreak.Price.replace(/[^0-9.]/g, ""));

      if (isNaN(price)) continue;

      results.push({
        mpn: part.ManufacturerPartNumber,
        manufacturer: part.Manufacturer,
        description: part.Description,
        price,
        currency: lowestPriceBreak.Currency || "USD",
        stock,
        minQuantity: parseInt(part.Min, 10) || 1,
        provider: this.name,
        distributor: "Mouser",
        url: part.ProductDetailUrl,
      });
    }

    return results.sort((a, b) => a.price - b.price);
  }
}
