const { ethers } = require("hardhat");

async function main() {
  const CONTRACT_ADDRESS = "0x6d9Deb320173e202fEEA60092cB29B64615fBb3e";
  const TARGET_ADDRESS = "0x1116Da5d8ef835228eff6f01D03c486098D1bFB9".toLowerCase();
  const EXPIRATION_DATE = "2026-12-31";

  console.log(`--- 🖋️ ERC-7827 Authorization Strike ---`);
  console.log(`Target: ${TARGET_ADDRESS}`);
  console.log(`Granting access until: ${EXPIRATION_DATE}`);

  const ERC7827 = await ethers.getContractAt("ERC7827", CONTRACT_ADDRESS);
  
  const tx = await ERC7827.write([TARGET_ADDRESS], [EXPIRATION_DATE]);
  console.log(`Transaction Hash: ${tx.hash}`);

  await tx.wait();
  console.log("✅ On-chain permission granted.");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
