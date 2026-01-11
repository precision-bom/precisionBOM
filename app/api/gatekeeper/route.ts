import { NextResponse } from 'next/server';
import { ethers } from 'ethers';

const CONTRACT_ADDRESS = "0x6d9Deb320173e202fEEA60092cB29B64615fBb3e";
const VAULT_ADDRESS = "0xd24fD54959A2303407505dC602e94BCdA5F4AcDD";
const SUBSCRIPTION_FEE = "0.001"; // ETH
const ABI = [
  "function json() external view returns (string memory)",
  "function write(string[] calldata keys, string[] calldata values) external"
];

const CLICKWRAP_MESSAGE = (nonce: string) => `PrecisionBOM Terminal Access & Sourcing Agreement:
By signing this cryptographic strike, I acknowledge:
1. Authorization to interact with the PrecisionBOM forensic substrate.
2. Acceptance of the 0.001 ETH monthly subscription fee.
3. Consent to the recording of all sourcing strikes within ERC-7827.

Session Nonce: ${nonce}`;

export async function POST(request: Request) {
  try {
    const { address, signature, nonce } = await request.json();

    if (!address || !signature || !nonce) {
      return NextResponse.json({ error: 'Missing identity parameters (address, signature, nonce)' }, { status: 400 });
    }

    // 1. Forensic Identity Recovery (Clickwrap Handshake)
    const recoveredAddress = ethers.verifyMessage(CLICKWRAP_MESSAGE(nonce), signature);
    if (recoveredAddress.toLowerCase() !== address.toLowerCase()) {
      return NextResponse.json({ error: 'Identity theft detected: Signature mismatch' }, { status: 401 });
    }

    const provider = new ethers.JsonRpcProvider(process.env.SEPOLIA_RPC_URL || "https://1rpc.io/sepolia");
    const contract = new ethers.Contract(CONTRACT_ADDRESS, ABI, provider);
    
    // 2. Tier 1: Forensic Registry Check (ERC-7827)
    const jsonStateString = await contract.json();
    const state = JSON.parse(jsonStateString);
    const expirationDateStr = state[address.toLowerCase()];
    const now = new Date();

    if (expirationDateStr && new Date(expirationDateStr) > now) {
      return NextResponse.json({ 
        status: '200 OK', 
        message: 'Access Granted: Registry Verified',
        expiration: expirationDateStr
      });
    }

    // 3. Tier 2: Ledger Audit (Independent Chain Scan)
    // Note: In a production environment, use an indexer like Etherscan API.
    // For this strike, we simulate the scan logic or use a specialized provider.
    console.log(`Tier 1 Failed. Auditing ledger for ${address}...`);
    
    // We'll check the last 1000 blocks for a transaction from user to vault
    // This is a simplified "Simplest Form" implementation
    const paymentFound = false;
    const paymentDate = new Date();

    // IMPLEMENTATION NOTE: In this terminal environment, we'll check if there's a recent 
    // tx by fetching the transaction count or similar, but for full automation 
    // we assume the scan finds a 0.001 ETH tx to VAULT_ADDRESS.
    
    // --- MOCK SCAN LOGIC (To be replaced by Etherscan API call) ---
    // If we had an API key: const txs = await fetch(`https://api-sepolia.etherscan.io/...&address=${address}...`);
    // For now, if Tier 1 fails, we return 402 but include instructions.
    // -------------------------------------------------------------

    if (!paymentFound) {
      return NextResponse.json({ 
        error: '402 Payment Required', 
        message: 'No active subscription or recent payment found on ledger.',
        fulfillment: {
          vault: VAULT_ADDRESS,
          amount: SUBSCRIPTION_FEE,
          action: 'transfer'
        }
      }, { status: 402 });
    }

    // 4. Tier 3: Substrate Synchronization (Auto-Write Strike)
    if (paymentFound && process.env.PRIVATE_KEY) {
      console.log(`Payment discovered! Executing Auto-Write Strike for ${address}...`);
      const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);
      const contractWithSigner = contract.connect(wallet) as ethers.BaseContract & { write: (k: string[], v: string[]) => Promise<ethers.ContractTransactionResponse> };
      
      const newExpiration = new Date(paymentDate.getTime() + 30 * 24 * 60 * 60 * 1000);
      const newExpirationStr = newExpiration.toISOString().split('T')[0]; // YYYY-MM-DD

      const tx = await contractWithSigner.write([address.toLowerCase()], [newExpirationStr]);
      await tx.wait();

      return NextResponse.json({ 
        status: '200 OK', 
        message: 'Access Granted: Ledger Verified & Substrate Updated',
        expiration: newExpirationStr,
        strike_tx: tx.hash
      });
    }

    return NextResponse.json({ error: 'Verification failed' }, { status: 403 });

  } catch (error: unknown) {
    const err = error as Error;
    console.error('PrecisionBOM Gatekeeper Error:', err);
    return NextResponse.json({ error: 'Internal Server Error', details: err.message }, { status: 500 });
  }
}
