import {
  BomItem,
  PartOffer,
  RealizedBom,
  RealizedLineItem,
  BomSuggestionResult,
} from "@/types/bom";
import { getAllConfiguredProviders, getConfiguredProviders } from "./providers";

interface PartOffersMap {
  [bomItemId: string]: PartOffer[];
}

/**
 * Search for offers for all BOM items across ALL configured providers
 */
export async function searchAllParts(items: BomItem[]): Promise<PartOffersMap> {
  const providers = getAllConfiguredProviders();
  const providerNames = getConfiguredProviders();

  console.log(`Searching across ${providers.length} providers: ${providerNames.join(", ")}`);

  const offersMap: PartOffersMap = {};

  // Initialize empty arrays for all items
  for (const item of items) {
    offersMap[item.id] = [];
  }

  // Search each provider in parallel
  const providerSearches = providers.map(async (provider) => {
    const itemSearches = items.map(async (item) => {
      const query = item.mpn || item.partNumber || item.description;
      try {
        const offers = item.manufacturer
          ? await provider.searchByMPN(query, item.manufacturer)
          : await provider.search(query);
        return { itemId: item.id, offers, provider: provider.name };
      } catch (error) {
        console.error(`[${provider.name}] Search failed for ${query}:`, error);
        return { itemId: item.id, offers: [], provider: provider.name };
      }
    });
    return Promise.all(itemSearches);
  });

  const allResults = await Promise.all(providerSearches);

  // Aggregate results from all providers
  for (const providerResults of allResults) {
    for (const { itemId, offers } of providerResults) {
      offersMap[itemId].push(...offers);
    }
  }

  // Log summary
  for (const item of items) {
    const query = item.mpn || item.partNumber || item.description;
    console.log(`  ${query}: ${offersMap[item.id].length} offers found`);
  }

  return offersMap;
}

/**
 * Generate a unique ID
 */
function generateId(): string {
  return `bom-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
}

/**
 * Create a realized line item from a BOM item and offer
 */
function createLineItem(bomItem: BomItem, offer: PartOffer): RealizedLineItem {
  return {
    bomItemId: bomItem.id,
    bomItem,
    offer,
    unitPrice: offer.price,
    lineTotal: bomItem.quantity * offer.price,
    inStock: offer.stock >= bomItem.quantity,
  };
}

/**
 * Calculate score for a realized BOM (0-100, higher is better)
 */
function calculateScore(bom: RealizedBom, totalItems: number): number {
  let score = 0;

  // Coverage score (up to 50 points)
  const coverage = bom.lineItems.length / totalItems;
  score += coverage * 50;

  // Bonus for all in stock (20 points)
  if (bom.allInStock) score += 20;

  // Bonus for fewer distributors (up to 15 points)
  if (bom.distributors.length === 1) score += 15;
  else if (bom.distributors.length === 2) score += 10;
  else if (bom.distributors.length <= 3) score += 5;

  // Bonus for complete BOM (15 points)
  if (coverage === 1) score += 15;

  return Math.round(Math.min(100, Math.max(0, score)));
}

/**
 * Create a realized BOM from line items
 */
function createRealizedBom(
  name: string,
  description: string,
  lineItems: RealizedLineItem[],
  totalItems: number
): RealizedBom {
  const totalCost = lineItems.reduce((sum, item) => sum + item.lineTotal, 0);
  const allInStock = lineItems.every((item) => item.inStock);
  const distributors = Array.from(new Set(lineItems.map((item) => item.offer.distributor)));

  const bom: RealizedBom = {
    id: generateId(),
    name,
    description,
    lineItems,
    totalCost,
    currency: "USD",
    allInStock,
    distributors,
    score: 0,
  };

  bom.score = calculateScore(bom, totalItems);
  return bom;
}

/**
 * Strategy: Pick lowest price for each item
 */
function lowestPriceStrategy(
  items: BomItem[],
  offersMap: PartOffersMap
): RealizedBom | null {
  const lineItems: RealizedLineItem[] = [];

  for (const item of items) {
    const offers = offersMap[item.id] || [];
    if (offers.length === 0) continue;

    // Sort by price and pick lowest
    const sortedOffers = [...offers].sort((a, b) => a.price - b.price);
    lineItems.push(createLineItem(item, sortedOffers[0]));
  }

  if (lineItems.length === 0) return null;

  return createRealizedBom(
    "Lowest Price",
    "Optimized for lowest total cost across all distributors",
    lineItems,
    items.length
  );
}

/**
 * Strategy: Prefer single distributor for shipping consolidation
 */
function singleDistributorStrategy(
  items: BomItem[],
  offersMap: PartOffersMap
): RealizedBom | null {
  // Count how many items each distributor can fulfill
  const distributorCoverage: { [distributor: string]: number } = {};
  const distributorOffers: { [distributor: string]: { [itemId: string]: PartOffer } } = {};

  for (const item of items) {
    const offers = offersMap[item.id] || [];
    for (const offer of offers) {
      if (!distributorCoverage[offer.distributor]) {
        distributorCoverage[offer.distributor] = 0;
        distributorOffers[offer.distributor] = {};
      }
      // Only count if we haven't already counted this item for this distributor
      if (!distributorOffers[offer.distributor][item.id]) {
        distributorCoverage[offer.distributor]++;
        distributorOffers[offer.distributor][item.id] = offer;
      } else {
        // Replace if this offer is cheaper
        if (offer.price < distributorOffers[offer.distributor][item.id].price) {
          distributorOffers[offer.distributor][item.id] = offer;
        }
      }
    }
  }

  // Find distributor with best coverage
  const sortedDistributors = Object.entries(distributorCoverage)
    .sort((a, b) => b[1] - a[1]);

  if (sortedDistributors.length === 0) return null;

  const bestDistributor = sortedDistributors[0][0];
  const lineItems: RealizedLineItem[] = [];

  for (const item of items) {
    const offer = distributorOffers[bestDistributor]?.[item.id];
    if (offer) {
      lineItems.push(createLineItem(item, offer));
    }
  }

  if (lineItems.length === 0) return null;

  const coverage = lineItems.length;
  const total = items.length;

  return createRealizedBom(
    `${bestDistributor} Only`,
    `${coverage}/${total} items from ${bestDistributor} - saves on shipping`,
    lineItems,
    items.length
  );
}

/**
 * Strategy: Only pick items that are in stock
 */
function inStockStrategy(
  items: BomItem[],
  offersMap: PartOffersMap
): RealizedBom | null {
  const lineItems: RealizedLineItem[] = [];

  for (const item of items) {
    const offers = offersMap[item.id] || [];
    // Filter to in-stock offers, then sort by price
    const inStockOffers = offers
      .filter((o) => o.stock >= item.quantity)
      .sort((a, b) => a.price - b.price);

    if (inStockOffers.length > 0) {
      lineItems.push(createLineItem(item, inStockOffers[0]));
    }
  }

  if (lineItems.length === 0) return null;

  return createRealizedBom(
    "All In Stock",
    "Only items currently available - fastest delivery",
    lineItems,
    items.length
  );
}

/**
 * Generate BOM suggestions with multiple strategies
 */
export async function suggestBoms(items: BomItem[]): Promise<BomSuggestionResult> {
  // Search for all parts across all providers
  const offersMap = await searchAllParts(items);

  // Find items with no offers
  const unmatchedItems = items.filter(
    (item) => !offersMap[item.id] || offersMap[item.id].length === 0
  );

  // Items that have offers
  const matchedItems = items.filter(
    (item) => offersMap[item.id] && offersMap[item.id].length > 0
  );

  // Generate suggestions using different strategies
  const suggestions: RealizedBom[] = [];

  const lowestPrice = lowestPriceStrategy(matchedItems, offersMap);
  if (lowestPrice) suggestions.push(lowestPrice);

  const singleDistributor = singleDistributorStrategy(matchedItems, offersMap);
  if (singleDistributor) suggestions.push(singleDistributor);

  const inStock = inStockStrategy(matchedItems, offersMap);
  if (inStock) suggestions.push(inStock);

  // Sort by score descending
  suggestions.sort((a, b) => b.score - a.score);

  return {
    originalItems: items,
    suggestions,
    unmatchedItems,
  };
}
