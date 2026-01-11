const { ethers } = require("hardhat");

async function main() {
  const CONTRACT_ADDRESS = "0x6d9Deb320173e202fEEA60092cB29B64615fBb3e";

  console.log(`Executing write strike on ERC7827 at ${CONTRACT_ADDRESS}...`);

  const ERC7827 = await ethers.getContractAt("ERC7827", CONTRACT_ADDRESS);

  const keys = ["hello"];
  const values = ["frontier"];

  console.log(`Writing: ${keys[0]} => ${values[0]}`);
  
  const tx = await ERC7827.write(keys, values);
  console.log(`Transaction hash: ${tx.hash}`);

  await tx.wait();
  console.log("Transaction confirmed.");

  const jsonState = await ERC7827.json();
  console.log("Current JSON state:", jsonState);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
