"use client";

import { useState } from 'react';
import { ethers } from 'ethers';

const VAULT_ADDRESS = "0xd24fD54959A2303407505dC602e94BCdA5F4AcDD";
const SUBSCRIPTION_FEE = "0.001"; // ETH

const CLICKWRAP_MESSAGE = (nonce: string) => `PrecisionBOM Terminal Access & Sourcing Agreement: By signing this cryptographic strike, I acknowledge: 1. Authorization to interact with the PrecisionBOM forensic substrate. 2. Acceptance of the 0.001 ETH (Sepolia) monthly subscription fee. 3. Consent to the recording of all sourcing strikes within ERC-7827. NOTE: If no active substrate record is found for this identity, a transaction request for 0.001 Sepolia ETH will follow to initialize access. Session Nonce: ${nonce}`;

export default function PaymentTab() {
  const [address, setAddress] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("Disconnected");
  const [expiration, setExpiration] = useState<string | null>(null);
  const [tokens, setTokens] = useState<string>("0");
  const [loading, setLoading] = useState(false);

  const getProvider = () => {
    if (typeof window !== 'undefined' && (window as { ethereum?: ethers.Eip1193Provider }).ethereum) {
      return new ethers.BrowserProvider((window as { ethereum: ethers.Eip1193Provider }).ethereum);
    }
    return null;
  };

  const checkAccess = async (userAddress: string, triggerPayment: boolean = false) => {
    setLoading(true);
    try {
      const provider = getProvider();
      if (!provider) return;

      const nonce = Date.now().toString();
      const signer = await provider.getSigner();
      const signature = await signer.signMessage(CLICKWRAP_MESSAGE(nonce));

      const response = await fetch('/api/gatekeeper', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ address: userAddress, signature, nonce })
      });

      const data = await response.json();

      if (response.status === 200) {
        setStatus("Access Granted");
        setExpiration(data.expiration);
        setTokens(data.tokens || "0");
      } else if (response.status === 402) {
        setStatus("Payment Required");
        setExpiration(null);
        setTokens(data.tokens || "0");
        if (triggerPayment) {
          await paySubscription(userAddress, provider);
        }
      } else {
        setStatus(`Error: ${data.error}`);
      }
    } catch (error: unknown) {
      const err = error as Error;
      console.error("Access Check Error:", err);
      setStatus("Verification Failed");
    } finally {
      setLoading(false);
    }
  };

  const paySubscription = async (userAddress: string, provider: ethers.BrowserProvider) => {
    try {
      setStatus("Escalating to Payment Strike...");
      const signer = await provider.getSigner();
      const tx = await signer.sendTransaction({
        to: VAULT_ADDRESS,
        value: ethers.parseEther(SUBSCRIPTION_FEE)
      });

      setStatus("Processing Transaction...");
      await tx.wait();
      setStatus("Payment Confirmed. Syncing...");
      
      await checkAccess(userAddress, false);
    } catch (error: unknown) {
      const err = error as Error;
      console.error("Payment Error:", err);
      setStatus("Strike Cancelled");
    }
  };

  const connect = async () => {
    const provider = getProvider();
    if (!provider) {
      alert("Web3 Wallet Not Found");
      return;
    }
    const accounts = await provider.send("eth_requestAccounts", []) as string[];
    setAddress(accounts[0]);
    await checkAccess(accounts[0], false);
  };

  return (
    <div className="bg-substrate-900 border border-substrate-800 rounded-xl p-6 font-mono text-white">
      <div className="flex justify-between items-center mb-6 border-b border-substrate-800 pb-4">
        <div>
          <h2 className="text-silkscreen text-lg uppercase tracking-tighter font-bold">Forensic Ledger</h2>
          <p className="text-[10px] text-substrate-500 uppercase tracking-widest mt-1">Multi-Source Proof of Payment (MSPP)</p>
        </div>
        <div className={`px-3 py-1 rounded text-[10px] uppercase font-bold ${
          status === "Access Granted" ? "bg-green-500/20 text-green-400 border border-green-500/30" : "bg-red-500/20 text-red-400 border border-red-500/30"
        }`}>
          {status}
        </div>
      </div>

      {!address ? (
        <button 
          onClick={connect}
          className="w-full py-4 border border-trace-500 text-trace-500 hover:bg-trace-500/10 transition-all rounded-lg uppercase tracking-widest text-sm font-bold shadow-trace"
        >
          Anchor Forensic Identity
        </button>
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-substrate-800/50 p-4 rounded-lg border border-substrate-700">
              <div className="text-[10px] text-substrate-500 uppercase font-bold mb-1">Identity</div>
              <div className="text-xs text-white truncate font-mono">{address}</div>
            </div>
            <div className="bg-substrate-800/50 p-4 rounded-lg border border-substrate-700">
              <div className="text-[10px] text-substrate-500 uppercase font-bold mb-1">Expiry</div>
              <div className="text-xs text-white font-mono">{expiration || "None"}</div>
            </div>
            <div className="bg-substrate-800/50 p-4 rounded-lg border border-substrate-700 shadow-[0_0_10px_rgba(16,185,129,0.1)]">
              <div className="text-[10px] text-trace-500 uppercase font-bold mb-1">Agentic Capital</div>
              <div className="text-xs text-trace-400 font-bold font-mono">{tokens} Tokens</div>
            </div>
          </div>

          <div className="bg-substrate-950 border border-substrate-800 p-4 rounded-lg">
            <h3 className="text-[10px] text-substrate-400 uppercase mb-3 tracking-widest border-b border-substrate-800 pb-2">Thermodynamic Rules</h3>
            <div className="space-y-2">
              <div className="flex justify-between text-[10px]">
                <span className="text-substrate-500">Vault Destination:</span>
                <span className="text-trace-400 font-mono">{VAULT_ADDRESS.slice(0,10)}...{VAULT_ADDRESS.slice(-8)}</span>
              </div>
              <div className="flex justify-between text-[10px]">
                <span className="text-substrate-500">Subscription Fee:</span>
                <span className="text-white font-bold">{SUBSCRIPTION_FEE} Sepolia ETH / Month</span>
              </div>
              <div className="flex justify-between text-[10px]">
                <span className="text-substrate-500">Auto-Write Protocol:</span>
                <span className="text-green-500/70">Enabled (Tier 3)</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-3">
            <button 
              disabled={loading}
              onClick={() => address && checkAccess(address, true)}
              className="w-full py-3 bg-trace-500 text-substrate-950 hover:bg-white transition-all rounded font-bold uppercase text-xs"
            >
              {loading ? "Executing Strike..." : "Initialize Access Strike (0.001 Sepolia ETH)"}
            </button>
            
            <button 
              disabled={loading}
              onClick={() => address && checkAccess(address, false)}
              className="w-full py-3 border border-substrate-700 text-substrate-400 hover:text-white hover:border-substrate-500 transition-all rounded font-bold uppercase text-[10px]"
            >
              Re-Verify Forensic Substrate
            </button>
          </div>

          <div className="bg-substrate-800/30 p-3 rounded text-[9px] text-substrate-500 leading-relaxed italic border-l-2 border-trace-500/30">
            &quot;The server scans the Sepolia ledger autonomously. If a payment strike is discovered, the PrecisionBOM Gateway will execute an automatic write to the ERC-7827 substrate to anchor your access.&quot;
          </div>
        </div>
      )}
    </div>
  );
}
