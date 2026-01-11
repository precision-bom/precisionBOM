const { ethers } = require("hardhat");

async function main() {
  const CONTRACT_ADDRESS = "0x6d9Deb320173e202fEEA60092cB29B64615fBb3e";
  const [deployer] = await ethers.getSigners();
  
  // Set the date from command line or default to today - 1 (expired)
  const newDate = process.argv[2] || "2026-01-01";
  const testAddress = deployer.address.toLowerCase();

  console.log(`--- 🖋️ ERC-7827 Write Strike: ${testAddress} ---`);
  console.log(`Setting expiration to: ${newDate}`);

  const ERC7827 = await ethers.getContractAt("ERC7827", CONTRACT_ADDRESS);
  const tx = await ERC7827.write([testAddress], [newDate]);
  
  console.log(`Transaction Hash: ${tx.hash}`);
  await tx.wait();
  console.log("✔ On-chain state updated.");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
