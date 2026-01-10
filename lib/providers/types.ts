import { ProviderResult } from "@/types/bom";

/**
 * Generic part provider interface - implement this for each distributor/aggregator
 */
export interface PartProvider {
  name: string;

  /**
   * Search for parts by a general query string
   */
  search(query: string): Promise<ProviderResult[]>;

  /**
   * Search for parts by manufacturer part number (more precise)
   */
  searchByMPN(mpn: string, manufacturer?: string): Promise<ProviderResult[]>;
}

/**
 * Generic offer from any provider - normalized structure
 */
export interface PartOffer {
  // Part identification
  mpn: string;
  manufacturer: string;
  description: string;

  // Pricing
  price: number;
  currency: string;
  priceBreaks?: PriceBreak[];

  // Availability
  stock: number;
  minOrderQuantity: number;
  leadTimeDays?: number;

  // Source
  provider: string;
  distributor: string;
  distributorPartNumber?: string;
  url: string;
}

/**
 * Price break for volume pricing
 */
export interface PriceBreak {
  quantity: number;
  price: number;
}

/**
 * Search results from a provider - groups offers by part
 */
export interface PartSearchResult {
  query: string;
  offers: PartOffer[];
}
