import { ProviderResult } from "@/types/bom";
import {
  PartProvider,
  OctopartSearchResponse,
} from "./types";

const NEXAR_TOKEN_URL = "https://identity.nexar.com/connect/token";
const NEXAR_API_URL = "https://api.nexar.com/graphql";

// Token cache for OAuth
let cachedToken: { token: string; expiresAt: number } | null = null;

export class OctopartProvider implements PartProvider {
  name = "octopart";
  private clientId: string;
  private clientSecret: string;

  constructor() {
    this.clientId = process.env.OCTOPART_CLIENT_ID || "";
    this.clientSecret = process.env.OCTOPART_CLIENT_SECRET || "";
  }

  private async getAccessToken(): Promise<string> {
    // Check if we have a valid cached token (with 60s buffer)
    if (cachedToken && cachedToken.expiresAt > Date.now() + 60000) {
      return cachedToken.token;
    }

    if (!this.clientId || !this.clientSecret) {
      throw new Error("Octopart OAuth credentials not configured");
    }

    const response = await fetch(NEXAR_TOKEN_URL, {
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
      throw new Error(`OAuth token request failed: ${response.status} - ${errorText}`);
    }

    const data = await response.json();

    // Cache the token
    cachedToken = {
      token: data.access_token,
      expiresAt: Date.now() + (data.expires_in * 1000),
    };

    console.log("Obtained new Octopart OAuth token");
    return cachedToken.token;
  }

  async search(query: string): Promise<ProviderResult[]> {
    return this.executeSearch(query);
  }

  async searchByMPN(mpn: string, manufacturer?: string): Promise<ProviderResult[]> {
    const query = manufacturer ? `${manufacturer} ${mpn}` : mpn;
    return this.executeSearch(query);
  }

  private async executeSearch(query: string): Promise<ProviderResult[]> {
    if (!this.clientId || !this.clientSecret) {
      console.warn("No Octopart OAuth credentials configured, returning mock data");
      return this.getMockResults(query);
    }

    const graphqlQuery = `
      query Search($q: String!) {
        supSearch(q: $q, limit: 10) {
          results {
            part {
              mpn
              manufacturer {
                name
              }
              shortDescription
              sellers {
                company {
                  name
                }
                offers {
                  clickUrl
                  inventoryLevel
                  moq
                  prices {
                    price
                    currency
                    quantity
                  }
                }
              }
            }
          }
        }
      }
    `;

    try {
      const token = await this.getAccessToken();

      const response = await fetch(NEXAR_API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          query: graphqlQuery,
          variables: { q: query },
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Nexar API error: ${response.status} - ${errorText}`);
      }

      const data = await response.json();

      if (data.errors) {
        console.error("GraphQL errors:", data.errors);
        throw new Error(data.errors[0]?.message || "GraphQL error");
      }

      return this.transformResults(data);
    } catch (error) {
      console.error("Octopart search failed:", error);
      return this.getMockResults(query);
    }
  }

  private transformResults(data: { data: { supSearch: { results: Array<{ part: {
    mpn: string;
    manufacturer: { name: string };
    shortDescription: string;
    sellers: Array<{
      company: { name: string };
      offers: Array<{
        clickUrl: string;
        inventoryLevel: number;
        moq: number | null;
        prices: Array<{ price: number; currency: string; quantity: number }>;
      }>;
    }>;
  } }> } } }): ProviderResult[] {
    const results: ProviderResult[] = [];

    if (!data.data?.supSearch?.results) {
      return results;
    }

    for (const result of data.data.supSearch.results) {
      const part = result.part;
      if (!part.sellers) continue;

      for (const seller of part.sellers) {
        for (const offer of seller.offers) {
          if (!offer.prices || offer.prices.length === 0) continue;

          // Get the lowest price tier
          const lowestPrice = offer.prices.reduce((min, p) =>
            p.price < min.price ? p : min
          );

          results.push({
            partNumber: part.mpn,
            manufacturer: part.manufacturer?.name || "Unknown",
            description: part.shortDescription || "",
            price: lowestPrice.price,
            currency: lowestPrice.currency,
            stock: offer.inventoryLevel || 0,
            minQuantity: offer.moq || 1,
            provider: this.name,
            distributor: seller.company?.name || "Unknown",
            url: offer.clickUrl || "",
          });
        }
      }
    }

    // Sort by price
    return results.sort((a, b) => a.price - b.price);
  }

  private getMockResults(query: string): ProviderResult[] {
    // Return mock data when credentials are not configured
    return [
      {
        partNumber: query.toUpperCase(),
        manufacturer: "Example Mfg",
        description: `Mock result for "${query}"`,
        price: 1.25,
        currency: "USD",
        stock: 1000,
        minQuantity: 1,
        provider: this.name,
        distributor: "DigiKey",
        url: "https://www.digikey.com",
      },
      {
        partNumber: query.toUpperCase(),
        manufacturer: "Example Mfg",
        description: `Mock result for "${query}"`,
        price: 1.15,
        currency: "USD",
        stock: 500,
        minQuantity: 10,
        provider: this.name,
        distributor: "Mouser",
        url: "https://www.mouser.com",
      },
      {
        partNumber: query.toUpperCase(),
        manufacturer: "Example Mfg",
        description: `Mock result for "${query}"`,
        price: 0.95,
        currency: "USD",
        stock: 2500,
        minQuantity: 100,
        provider: this.name,
        distributor: "Arrow",
        url: "https://www.arrow.com",
      },
    ];
  }
}
