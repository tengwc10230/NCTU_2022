const Custom = artifacts.require("Custom_ERC20");

module.exports = function (deployer) {
  deployer.deploy(Custom, 1000000);
};