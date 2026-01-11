const { ethers } = require("hardhat");

async function main() {
  const CONTRACT_ADDRESS = "0x6d9Deb320173e202fEEA60092cB29B64615fBb3e";
  const [deployer] = await ethers.getSigners();
  const testAddress = deployer.address.toLowerCase();

  console.log("--- 🛡️ x402 Temporal Gatekeeper Test ---");
  console.log(`Checking access for: ${testAddress}`);

  const ERC7827 = await ethers.getContractAt("ERC7827", CONTRACT_ADDRESS);
  const jsonStateString = await ERC7827.json();
  const state = JSON.parse(jsonStateString);

  const expirationDateStr = state[testAddress];
  const now = new Date();

  console.log(`Current System Date: ${now.toISOString().split('T')[0]}`);

  if (!expirationDateStr) {
    console.log("❌ Result: 402 Payment Required (Address not found in registry)");
    return;
  }

  const expirationDate = new Date(expirationDateStr);
  console.log(`On-Chain Expiration: ${expirationDateStr}`);

  if (expirationDate > now) {
    console.log("✅ Result: 200 OK (Access Granted)");
  } else {
    console.log("❌ Result: 402 Payment Required (Subscription Expired)");
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
