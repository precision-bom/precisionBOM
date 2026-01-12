import { NextRequest } from "next/server";
import { ethers } from "ethers";

const CONTRACT_ADDRESS = "0x6d9Deb320173e202fEEA60092cB29B64615fBb3e";
const ABI = ["function json() external view returns (string memory)"];

const CLICKWRAP_MESSAGE = (nonce: string) => `PrecisionBOM Terminal Access & Sourcing Agreement: By signing this cryptographic strike, I acknowledge: 1. Authorization to interact with the PrecisionBOM forensic substrate. 2. Acceptance of the 0.001 ETH (Sepolia) monthly subscription fee. 3. Consent to the recording of all sourcing strikes within ERC-7827. NOTE: If no active substrate record is found for this identity, a transaction request for 0.001 Sepolia ETH will follow to initialize access. Session Nonce: ${nonce}`;

export async function verifySovereignAccess(request: NextRequest) {
  const address = request.headers.get("X-Forensic-Identity")?.toLowerCase();
  const signature = request.headers.get("X-Forensic-Signature");
  const nonce = request.headers.get("X-Forensic-Nonce");

  if (!address || !signature || !nonce) {
    throw new Error("Handshake Required: Missing forensic headers.");
  }

  // 1. Verify Signature
  const recoveredAddress = ethers.verifyMessage(CLICKWRAP_MESSAGE(nonce), signature);
  if (recoveredAddress.toLowerCase() !== address) {
    throw new Error("Identity Mismatch: Handshake failed.");
  }

  // 2. Verify Substrate (Tier 1)
  const provider = new ethers.JsonRpcProvider(process.env.SEPOLIA_RPC_URL || "https://ethereum-sepolia-rpc.publicnode.com");
  const contract = new ethers.Contract(CONTRACT_ADDRESS, ABI, provider);
  
  const jsonStateString = await contract.json();
  const state = JSON.parse(jsonStateString);
  const expirationDateStr = state[address];
  const now = new Date();

  if (!expirationDateStr || new Date(expirationDateStr) <= now) {
    const error = new Error("Subscription Required: No active substrate record found.") as any;
    error.status = 402;
    throw error;
  }

  return { address, expiration: expirationDateStr };
}
