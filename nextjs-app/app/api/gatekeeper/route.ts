import { NextResponse } from 'next/server';
import { ethers } from 'ethers';

const CONTRACT_ADDRESS = "0x6d9Deb320173e202fEEA60092cB29B64615fBb3e";
const VAULT_ADDRESS = "0xd24fD54959A2303407505dC602e94BCdA5F4AcDD";
const SUBSCRIPTION_FEE = "0.001"; // ETH
const ABI = [
  "function json() external view returns (string memory)",
  "function write(string[] calldata keys, string[] calldata values) external"
];

interface EtherscanTx {
  to: string;
  value: string;
  isError: string;
  timeStamp: string;
  hash: string;
}

const CLICKWRAP_MESSAGE = (nonce: string) => `PrecisionBOM Terminal Access & Sourcing Agreement:
By signing this cryptographic strike, I acknowledge:
1. Authorization to interact with the PrecisionBOM forensic substrate.
2. Acceptance of the 0.001 ETH monthly subscription fee.
3. Consent to the recording of all sourcing strikes within ERC-7827.
NOTE: If no active substrate record is found for this identity, 
a transaction request for 0.001 ETH will follow to initialize access.

Session Nonce: ${nonce}`;

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const address = searchParams.get('address')?.toLowerCase();

  if (!address) {
    return NextResponse.json({ error: 'Address required' }, { status: 400 });
  }

  try {
    const provider = new ethers.JsonRpcProvider(process.env.SEPOLIA_RPC_URL || "https://1rpc.io/sepolia");
    const contract = new ethers.Contract(CONTRACT_ADDRESS, ABI, provider);
    
    const jsonStateString = await contract.json();
    const state = JSON.parse(jsonStateString);
    const expirationDateStr = state[address];
    const now = new Date();

    if (expirationDateStr && new Date(expirationDateStr) > now) {
      return NextResponse.json({ 
        status: '200 OK', 
        message: 'Access Granted',
        expiration: expirationDateStr
      });
    }

    return NextResponse.json({ 
      error: '402 Payment Required', 
      message: 'No active subscription found. POST signature to /api/gatekeeper for tiered check.'
    }, { status: 402 });

  } catch (error: unknown) {
    const err = error as Error;
    console.error('PrecisionBOM Gatekeeper GET Error:', err);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}

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

    console.log(`[FORENSIC VERIFIED] Identity ${recoveredAddress} confirmed as secret holder of signed Clickwrap strike.`);

    const provider = new ethers.JsonRpcProvider(process.env.SEPOLIA_RPC_URL || "https://1rpc.io/sepolia");
    const contract = new ethers.Contract(CONTRACT_ADDRESS, ABI, provider);
    
    // 2. Tier 1: Forensic Registry Check (ERC-7827)
    const jsonStateString = await contract.json();
    const state = JSON.parse(jsonStateString);
    const expirationDateStr = state[address.toLowerCase()];
    const now = new Date();

    if (expirationDateStr && new Date(expirationDateStr) > now) {
      console.log(`[SUBSTRATE MATCH] Active record found for ${address}: ${expirationDateStr}`);
      return NextResponse.json({ 
        status: '200 OK', 
        message: 'Access Granted: Registry Verified',
        expiration: expirationDateStr
      });
    }

    // 3. Tier 2: Ledger Audit (Independent Chain Scan)
    console.log(`[LEDGER AUDIT] Tier 1 Failed. Scanning Sepolia for ${address}...`);
    
    const etherscanUrl = `https://api-sepolia.etherscan.io/api?module=account&action=txlist&address=${address}&startblock=0&endblock=99999999&sort=desc&apikey=${process.env.ETH_SCAN_API_KEY || "YourApiKeyToken"}`;
    
    const ethResponse = await fetch(etherscanUrl);
    const ethData = await ethResponse.json();

    let paymentFound = false;
    let paymentDate = new Date();

    if (ethData.status === "1" && Array.isArray(ethData.result)) {
      const validTx = (ethData.result as EtherscanTx[]).find((tx) => 
        tx.to.toLowerCase() === VAULT_ADDRESS.toLowerCase() && 
        parseFloat(ethers.formatEther(tx.value)) >= parseFloat(SUBSCRIPTION_FEE) &&
        tx.isError === "0"
      );

      if (validTx) {
        paymentFound = true;
        paymentDate = new Date(parseInt(validTx.timeStamp) * 1000);
        console.log(`[PAYMENT DISCOVERED] Matching transaction found: ${validTx.hash}`);
      }
    }

    if (!paymentFound) {
      console.log(`[PAYMENT REQUIRED] No valid transaction found for ${address}. Escalating to client.`);
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
      console.log(`[SYNC STRIKE] Payment verified! Synchronizing substrate for ${address}...`);
      const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);
      const contractWithSigner = contract.connect(wallet) as ethers.BaseContract & { write: (k: string[], v: string[]) => Promise<ethers.ContractTransactionResponse> };
      
      const newExpiration = new Date(paymentDate.getTime() + 30 * 24 * 60 * 60 * 1000);
      const newExpirationStr = newExpiration.toISOString().split('T')[0]; // YYYY-MM-DD

      const tx = await contractWithSigner.write([address.toLowerCase()], [newExpirationStr]);
      await tx.wait();

      console.log(`[SUBSTRATE SYNCED] ${address} updated to ${newExpirationStr}. Strike TX: ${tx.hash}`);

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
    console.error('PrecisionBOM Gatekeeper POST Error:', err);
    return NextResponse.json({ error: 'Internal Server Error', details: err.message }, { status: 500 });
  }
}