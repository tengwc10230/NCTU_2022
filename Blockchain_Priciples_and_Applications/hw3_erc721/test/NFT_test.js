const LAN_NFT = artifacts.require("LAN_NFT");
contract("LAN_NFT", () => {
    // initialise the contract instance before running tests
	let NFTcontractInstance = null;
	before(async () => {
		NFTcontractInstance = await LAN_NFT.deployed();
	});
    
    it("mint our NFT with tokenURI", async () => {
        const tokenURI = "https://ipfs.io/ipfs/QmNmZGRP8EoD6FtzFpp8v7J9GiAqBc4DgHPhHcyeCFndtw";
        await NFTcontractInstance.mint(tokenURI);
    });
})
