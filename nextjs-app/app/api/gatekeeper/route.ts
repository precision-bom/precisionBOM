import { NextResponse } from 'next/server';
import { ethers } from 'ethers';

const CONTRACT_ADDRESS = "0x6d9Deb320173e202fEEA60092cB29B64615fBb3e";
const VAULT_ADDRESS = "0xd24fD54959A2303407505dC602e94BCdA5F4AcDD";
const SUBSCRIPTION_FEE = "0.001"; // ETH
const FEE_WEI = ethers.parseEther(SUBSCRIPTION_FEE);

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

const CLICKWRAP_MESSAGE = (nonce: string) => `PrecisionBOM Terminal Access & Sourcing Agreement: By signing this cryptographic strike, I acknowledge: 1. Authorization to interact with the PrecisionBOM forensic substrate. 2. Acceptance of the 0.001 ETH (Sepolia) monthly subscription fee. 3. Consent to the recording of all sourcing strikes within ERC-7827. NOTE: If no active substrate record is found for this identity, a transaction request for 0.001 Sepolia ETH will follow to initialize access. Session Nonce: ${nonce}`;

export async function POST(request: Request) {
  try {
    const { address, signature, nonce, action, amount } = await request.json();

    if (!address || !signature || !nonce) {
      return NextResponse.json({ error: 'Missing identity parameters' }, { status: 400 });
    }

    // 1. Identity Recovery
    const recoveredAddress = ethers.verifyMessage(CLICKWRAP_MESSAGE(nonce), signature);
    if (recoveredAddress.toLowerCase() !== address.toLowerCase()) {
      return NextResponse.json({ error: `Identity mismatch` }, { status: 401 });
    }

    const provider = new ethers.JsonRpcProvider(process.env.SEPOLIA_RPC_URL || "https://ethereum-sepolia-rpc.publicnode.com");
    const contract = new ethers.Contract(CONTRACT_ADDRESS, ABI, provider);
    
    // 2. Fetch Current State
    const jsonStateString = await contract.json();
    const state = JSON.parse(jsonStateString);
    const lowerAddress = address.toLowerCase();
    const expirationDateStr = state[lowerAddress];
    const tokenBalance = parseInt(state[`${lowerAddress}_tokens`] || "0");
    const now = new Date();

    // ACTION: DEDUCT (For AI Strikes)
    if (action === 'deduct' && amount) {
      if (tokenBalance < amount) {
        return NextResponse.json({ error: '402 Payment Required', message: 'Insufficient thermodynamic capital.', tokens: tokenBalance.toString() }, { status: 402 });
      }

      if (process.env.PRIVATE_KEY) {
        const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);
        const contractWithSigner = contract.connect(wallet) as any;
        const newTokenBalance = Math.max(0, tokenBalance - amount).toString();
        const tokenKey = `${lowerAddress}_tokens`;

        // Background write strike
        contractWithSigner.write([tokenKey], [newTokenBalance])
          .then((tx: any) => console.log(`[STRIKE DEDUCT] -${amount} Tokens for ${address}: ${tx.hash}`))
          .catch((err: any) => console.error(`[DEDUCT ERROR]`, err));

        return NextResponse.json({ 
          status: '200 OK', 
          message: 'Strike Deducted',
          tokens: newTokenBalance
        });
      }
    }

    // DEFAULT ACTION: VERIFY/SYNC
    if (expirationDateStr && new Date(expirationDateStr) > now) {
      return NextResponse.json({ 
        status: '200 OK', 
        message: 'Access Granted: Registry Verified',
        expiration: expirationDateStr,
        tokens: tokenBalance.toString()
      });
    }

    // Tier 2: Ledger Audit
    console.log(`[LEDGER AUDIT] Scanning Sepolia for ${address}...`);
    const apiKey = process.env.ETHERSCAN_API_KEY || "YourApiKeyToken";
    const etherscanUrl = `https://api-sepolia.etherscan.io/api?module=account&action=txlist&address=${address}&startblock=0&endblock=99999999&sort=desc&apikey=${apiKey}`;
    
    const ethResponse = await fetch(etherscanUrl);
    const ethData = await ethResponse.json();

    let validTx: EtherscanTx | undefined;
    if (ethData.status === "1" && Array.isArray(ethData.result)) {
      validTx = (ethData.result as EtherscanTx[]).find((tx) => 
        tx.to.toLowerCase() === VAULT_ADDRESS.toLowerCase() && 
        BigInt(tx.value) >= FEE_WEI &&
        tx.isError === "0"
      );
    }

    if (validTx) {
      const paymentDate = new Date(parseInt(validTx.timeStamp) * 1000);
      const newExpiration = new Date(paymentDate.getTime() + 30 * 24 * 60 * 60 * 1000);
      const newExpirationStr = newExpiration.toISOString().split('T')[0];

      if (process.env.PRIVATE_KEY) {
        const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);
        const contractWithSigner = contract.connect(wallet) as any;
        const tokenKey = `${lowerAddress}_tokens`;
        contractWithSigner.write([lowerAddress, tokenKey], [newExpirationStr, "1000"])
          .then((tx: any) => console.log(`[SYNC STRIKE] ${tx.hash}`))
          .catch((err: any) => console.error(`[SYNC ERROR]`, err));
      }

      return NextResponse.json({ 
        status: '200 OK', 
        message: 'Access Granted: Ledger Verified',
        expiration: newExpirationStr,
        tokens: "1000"
      });
    }

    return NextResponse.json({ 
      error: '402 Payment Required', 
      message: 'Subscription strike required.',
      tokens: tokenBalance.toString()
    }, { status: 402 });

  } catch (error: any) {
    console.error('PrecisionBOM Gatekeeper Error:', error);
    return NextResponse.json({ error: 'Internal Error', details: error.message }, { status: 500 });
  }
}