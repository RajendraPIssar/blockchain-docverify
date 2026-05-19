const { ethers } = require("hardhat");

async function main() {
  console.log("\n Deploying DocumentRegistry contract...\n");

  const [deployer] = await ethers.getSigners();
  console.log("Deployer address :", deployer.address);

  const balance = await deployer.provider.getBalance(deployer.address);
  console.log("Account balance  :", ethers.formatEther(balance), "ETH\n");

  const Factory  = await ethers.getContractFactory("DocumentRegistry");
  const contract = await Factory.deploy();
  await contract.waitForDeployment();

  const address = await contract.getAddress();
  console.log("✅  Contract deployed to:", address);
  console.log("\n──────────────────────────────────────────────────");
  console.log("📋  Copy these two lines into backend/.env:\n");
  console.log(`CONTRACT_ADDRESS=${address}`);
  console.log(`PRIVATE_KEY=<paste Account #0 private key from hardhat node output>`);
  console.log("──────────────────────────────────────────────────\n");
}

main()
  .then(() => process.exit(0))
  .catch((err) => { console.error(err); process.exit(1); });
