"use client";

import { useState } from 'react';

interface EthereumProvider {
  request: (args: { method: string; params?: unknown[] }) => Promise<unknown>;
}

export default function WalletConnect() {
  const [address, setAddress] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const checkAccess = async (userAddress: string) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/gatekeeper?address=${userAddress}`);
      const data = await response.json();

      if (response.status === 200) {
        setStatus(`Active (Until: ${data.expiration})`);
      } else if (response.status === 402) {
        setStatus(`Payment Required (x402)`);
      } else {
        setStatus(`Error: ${data.error}`);
      }
    } catch (error: unknown) {
      const err = error as Error;
      console.error("Access Check Error:", err);
      setStatus("Failed to check status");
    } finally {
      setLoading(false);
    }
  };

  const connectWallet = async () => {
    const ethereum = (window as { ethereum?: EthereumProvider }).ethereum;
    if (typeof window !== 'undefined' && ethereum) {
      try {
        // Force account selection dialog
        await ethereum.request({
          method: 'wallet_requestPermissions',
          params: [{ eth_accounts: {} }],
        });
        
        const accounts = await ethereum.request({ method: 'eth_requestAccounts' }) as string[];
        const userAddress = accounts[0];
        setAddress(userAddress);
        checkAccess(userAddress);
      } catch (error: unknown) {
        const err = error as Error;
        console.error("Connection Error:", err);
      }
    } else {
      alert("Please install a Web3 wallet (e.g., MetaMask)");
    }
  };

  const disconnectWallet = () => {
    setAddress(null);
    setStatus(null);
  };

  return (
    <div className="flex items-center gap-3">
      {address ? (
        <div className="flex items-center gap-3">
          <div className="flex flex-col items-end border-r border-substrate-800 pr-3">
            <span className="text-[10px] text-trace-500 uppercase tracking-widest font-bold">
              {loading ? "Verifying..." : status}
            </span>
            <span className="text-xs text-white opacity-70">
              {address.slice(0, 6)}...{address.slice(-4)}
            </span>
          </div>
          <button
            onClick={disconnectWallet}
            className="text-[10px] uppercase tracking-tighter text-substrate-500 hover:text-red-400 transition-colors"
          >
            Disconnect
          </button>
        </div>
      ) : (
        <button
          onClick={connectWallet}
          className="text-sm px-4 py-2 border border-trace-500/30 hover:border-trace-500 text-trace-500 rounded transition-all hover:bg-trace-500/10"
        >
          Connect Wallet
        </button>
      )}
    </div>
  );
}