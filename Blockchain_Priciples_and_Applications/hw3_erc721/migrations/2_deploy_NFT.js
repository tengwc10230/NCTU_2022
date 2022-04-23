const LAN_NFT = artifacts.require("LAN_NFT");

module.exports = function (deployer) {
	deployer.deploy(LAN_NFT);
};