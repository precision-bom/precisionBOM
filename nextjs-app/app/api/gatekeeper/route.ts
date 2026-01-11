import { NextResponse } from 'next/server';
import { ethers } from 'ethers';

const CONTRACT_ADDRESS = "0x6d9Deb320173e202fEEA60092cB29B64615fBb3e";
const ABI = [
  "function json() external view returns (string memory)"
];

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

    if (!expirationDateStr) {
      return NextResponse.json({ 
        error: '402 Payment Required', 
        message: 'Address not found in registry',
        fulfillment: {
          contract: CONTRACT_ADDRESS,
          action: 'write',
          required_key: address
        }
      }, { status: 402 });
    }

    const expirationDate = new Date(expirationDateStr);
    
    if (expirationDate > now) {
      return NextResponse.json({ 
        status: '200 OK', 
        message: 'Access Granted',
        expiration: expirationDateStr
      });
    } else {
      return NextResponse.json({ 
        error: '402 Payment Required', 
        message: 'Subscription Expired',
        expiration: expirationDateStr,
        fulfillment: {
          contract: CONTRACT_ADDRESS,
          action: 'write',
          required_key: address
        }
      }, { status: 402 });
    }
  } catch (error: any) {
    console.error('Gatekeeper Error:', error);
    return NextResponse.json({ error: 'Internal Server Error', details: error.message }, { status: 500 });
  }
}
