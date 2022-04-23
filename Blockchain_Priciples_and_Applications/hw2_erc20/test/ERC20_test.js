const CT_ERC20 = artifacts.require("Custom_ERC20")

contract("CT_ERC20", (accounts) => {
    before(async() => {
        deployed_contract = await CT_ERC20.deployed()
    })

    it("give the owner of the token 1M tokens", async() => {
        let balance = await deployed_contract.balanceOf(accounts[0])
        // console.log(web3.utils.fromWei(balance))
        // 1M * 10^18 -> 1M
        balance = web3.utils.fromWei(balance)
        assert.equal(balance, '1000000', 'Balance should be 1M tokens for account 0')
    })

    it("can transfer tokens between accounts", async ()=>{
        let amount = web3.utils.toWei('1000', 'ether')
        await deployed_contract.transfer(accounts[1], amount, { from: accounts[0] })

        let balance = await deployed_contract.balanceOf(accounts[1])
        balance = web3.utils.fromWei(balance, 'ether')
        assert.equal(balance, '1000', 'Balance should be 1K tokens for contract creator')
    })

})
