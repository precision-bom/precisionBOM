import { PartProvider } from "./types";
import { OctopartProvider } from "./octopart";
import { MouserProvider } from "./mouser";
import { DigiKeyProvider } from "./digikey";

export type ProviderName = "octopart" | "mouser" | "digikey";

const providers: Record<ProviderName, () => PartProvider> = {
  octopart: () => new OctopartProvider(),
  mouser: () => new MouserProvider(),
  digikey: () => new DigiKeyProvider(),
};

/**
 * Check if a provider is configured (has required env vars)
 */
export function isProviderConfigured(name: ProviderName): boolean {
  switch (name) {
    case "octopart":
      return !!(process.env.OCTOPART_CLIENT_ID && process.env.OCTOPART_CLIENT_SECRET);
    case "mouser":
      return !!process.env.MOUSER_API_KEY;
    case "digikey":
      return !!(process.env.DIGIKEY_CLIENT_ID && process.env.DIGIKEY_CLIENT_SECRET);
    default:
      return false;
  }
}

/**
 * Get a provider instance by name
 */
export function getProvider(name: ProviderName): PartProvider {
  const factory = providers[name];
  if (!factory) {
    throw new Error(`Unknown provider: ${name}`);
  }
  return factory();
}

/**
 * Get the default provider (first configured one)
 */
export function getDefaultProvider(): PartProvider {
  const configured = getConfiguredProviders();
  if (configured.length === 0) {
    throw new Error("No providers configured. Set API credentials in environment variables.");
  }
  return getProvider(configured[0]);
}

/**
 * Get all configured provider names
 */
export function getConfiguredProviders(): ProviderName[] {
  return (Object.keys(providers) as ProviderName[]).filter(isProviderConfigured);
}

/**
 * Get all available provider names
 */
export function getAvailableProviders(): ProviderName[] {
  return Object.keys(providers) as ProviderName[];
}

/**
 * Get all configured provider instances
 */
export function getAllConfiguredProviders(): PartProvider[] {
  return getConfiguredProviders().map(getProvider);
}

export { OctopartProvider, MouserProvider, DigiKeyProvider };
export type { PartProvider } from "./types";
