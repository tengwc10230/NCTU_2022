// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;
 
contract Arithmetic {
    function addition(int x, int y) public pure returns(int){
        return x + y;
    }

    function subtraction(int x, int y) public pure returns(int){
        return x - y;
    }

    function multiplication(int x, int y) public pure returns(int){
        return x * y;
    }

    function division(int x, int y) public pure returns(int){
        return x / y;
    }
}