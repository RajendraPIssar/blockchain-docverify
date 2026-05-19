const { expect } = require("chai");
const { ethers }  = require("hardhat");

describe("DocumentRegistry", function () {
  let contract;
  let owner, addr1;

  const SAMPLE_HASH = ethers.id("test-document-content"); // fake bytes32 hash

  beforeEach(async () => {
    [owner, addr1] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory("DocumentRegistry");
    contract = await Factory.deploy();
    await contract.waitForDeployment();
  });

  it("registers a document and emits an event", async () => {
    await expect(contract.registerDocument(SAMPLE_HASH, "test.pdf"))
      .to.emit(contract, "DocumentRegistered")
      .withArgs(SAMPLE_HASH, owner.address, await ethers.provider.getBlock("latest").then(b => b.timestamp + 1));
  });

  it("verifies a registered document returns exists = true", async () => {
    await contract.registerDocument(SAMPLE_HASH, "test.pdf");
    const [exists, , uploader] = await contract.verifyDocument(SAMPLE_HASH);
    expect(exists).to.be.true;
    expect(uploader).to.equal(owner.address);
  });

  it("returns exists = false for an unregistered hash", async () => {
    const fakeHash = ethers.id("never-registered");
    const [exists] = await contract.verifyDocument(fakeHash);
    expect(exists).to.be.false;
  });

  it("reverts if the same hash is registered twice", async () => {
    await contract.registerDocument(SAMPLE_HASH, "test.pdf");
    await expect(
      contract.registerDocument(SAMPLE_HASH, "test.pdf")
    ).to.be.revertedWith("Document already registered");
  });

  it("reverts on a zero hash", async () => {
    await expect(
      contract.registerDocument(ethers.ZeroHash, "test.pdf")
    ).to.be.revertedWith("Hash cannot be zero");
  });

  it("increments totalDocuments counter", async () => {
    expect(await contract.totalDocuments()).to.equal(0);
    await contract.registerDocument(SAMPLE_HASH, "doc1.pdf");
    expect(await contract.totalDocuments()).to.equal(1);
    await contract.registerDocument(ethers.id("doc2"), "doc2.pdf");
    expect(await contract.totalDocuments()).to.equal(2);
  });
});
