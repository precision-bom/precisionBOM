import { ProviderResult } from "@/types/bom";
import { PartProvider } from "./types";

const DIGIKEY_TOKEN_URL = "https://api.digikey.com/v1/oauth2/token";
const DIGIKEY_SEARCH_URL = "https://api.digikey.com/products/v4/search/keyword";

// Token cache for OAuth
let cachedToken: { token: string; expiresAt: number } | null = null;

interface DigiKeySearchResponse {
  Products: DigiKeyProduct[];
  ProductsCount: number;
}

interface DigiKeyProduct {
  DigiKeyPartNumber: string;
  ManufacturerPartNumber: string;
  Manufacturer: { Name: string };
  ProductDescription: string;
  DetailedDescription: string;
  ProductUrl: string;
  QuantityAvailable: number;
  UnitPrice: number;
  MinimumOrderQuantity: number;
  StandardPricing: Array<{
    BreakQuantity: number;
    UnitPrice: number;
  }>;
}

export class DigiKeyProvider implements PartProvider {
  name = "digikey";
  private clientId: string;
  private clientSecret: string;

  constructor() {
    this.clientId = process.env.DIGIKEY_CLIENT_ID || "";
    this.clientSecret = process.env.DIGIKEY_CLIENT_SECRET || "";
  }

  private async getAccessToken(): Promise<string> {
    // Check if we have a valid cached token (with 60s buffer)
    if (cachedToken && cachedToken.expiresAt > Date.now() + 60000) {
      return cachedToken.token;
    }

    if (!this.clientId || !this.clientSecret) {
      throw new Error("DigiKey OAuth credentials not configured");
    }

    const response = await fetch(DIGIKEY_TOKEN_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        grant_type: "client_credentials",
        client_id: this.clientId,
        client_secret: this.clientSecret,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`DigiKey OAuth token request failed: ${response.status} - ${errorText}`);
    }

    const data = await response.json();

    // Cache the token
    cachedToken = {
      token: data.access_token,
      expiresAt: Date.now() + (data.expires_in * 1000),
    };

    console.log("Obtained new DigiKey OAuth token");
    return cachedToken.token;
  }

  async search(query: string): Promise<ProviderResult[]> {
    return this.executeSearch(query);
  }

  async searchByMPN(mpn: string, manufacturer?: string): Promise<ProviderResult[]> {
    return this.executeSearch(mpn);
  }

  private async executeSearch(query: string): Promise<ProviderResult[]> {
    if (!this.clientId || !this.clientSecret) {
      throw new Error("DigiKey OAuth credentials not configured. Set DIGIKEY_CLIENT_ID and DIGIKEY_CLIENT_SECRET.");
    }

    const token = await this.getAccessToken();

    const response = await fetch(DIGIKEY_SEARCH_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        "X-DIGIKEY-Client-Id": this.clientId,
      },
      body: JSON.stringify({
        Keywords: query,
        RecordCount: 10,
        RecordStartPosition: 0,
        ExcludeMarketPlaceProducts: true,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`DigiKey API error: ${response.status} - ${errorText}`);
    }

    const data: DigiKeySearchResponse = await response.json();
    return this.transformResults(data);
  }

  private transformResults(data: DigiKeySearchResponse): ProviderResult[] {
    const results: ProviderResult[] = [];

    if (!data.Products) {
      return results;
    }

    for (const product of data.Products) {
      // Get the best price (qty 1 or lowest tier)
      let price = product.UnitPrice;
      if (product.StandardPricing && product.StandardPricing.length > 0) {
        price = product.StandardPricing[0].UnitPrice;
      }

      if (!price || price <= 0) continue;

      results.push({
        mpn: product.ManufacturerPartNumber,
        manufacturer: product.Manufacturer?.Name || "Unknown",
        description: product.ProductDescription || product.DetailedDescription || "",
        price,
        currency: "USD",
        stock: product.QuantityAvailable || 0,
        minQuantity: product.MinimumOrderQuantity || 1,
        provider: this.name,
        distributor: "DigiKey",
        url: product.ProductUrl || `https://www.digikey.com/products/en?keywords=${encodeURIComponent(product.ManufacturerPartNumber)}`,
      });
    }

    return results.sort((a, b) => a.price - b.price);
  }
}
