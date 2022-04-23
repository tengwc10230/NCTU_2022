// to interact with the contract
const Arithmetic = artifacts.require("Arithmetic");

contract('Arithmetic', () => {
 
	// initialise the contract instance before running tests
	let contractInstance = null;
	before(async () => {
		contractInstance = await Arithmetic.deployed();
	});
 
	// Addition
	it('Addition Test: 31083 + 2019 should be 33102', async () => {
		let result = await contractInstance.addition(31083, 2019);
		// console.log(result)
		assert.equal(result, 33102, "Addition wrong");
	});

	// Subtraction
	it('Subtraction Test: 31083 - 2019 should be 29064', async () => {
		let result = await contractInstance.subtraction(31083, 2019);
		// console.log(result)
		assert.equal(result, 29064, "Subtraction wrong");
	});

	// Multiplication
	it('Multiplication Test: 31083 * 2019 should be 62756577', async () => {
		let result = await contractInstance.multiplication(31083, 2019);
		// console.log(result)
		assert.equal(result, 62756577, "Multiplication wrong");
	});

	// Division 
	it('Division Test: 31083 / 2019 should be 15', async () => {
		let result = await contractInstance.division(31083, 2019);
		// console.log(result)
		assert.equal(result, 15, "Division wrong");
	});

});