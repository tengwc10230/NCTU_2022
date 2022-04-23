const Arithmetic = artifacts.require("Arithmetic");

module.exports = function (deployer) {
	deployer.deploy(Arithmetic);
};