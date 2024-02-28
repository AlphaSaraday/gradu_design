// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface bridgeInterface {
    function chainToBridge(string memory recv_chainid, address recv_contract, string memory content) external;
}

contract ethBussiness {
    struct Message {
        string recv_chainid;
        address recv_contract;
        string content;
    }
    Message public message;
    bridgeInterface public bridgeContract;
    address public bridge_addr;
    string public result;
    constructor(address bridgeAddr) {
        bridgeContract = bridgeInterface(bridgeAddr);
        bridge_addr = bridgeAddr;
        result = "none";
        message.recv_chainid = "none";
        message.recv_contract = address(0);
        message.content = "none";
    }

    function fillMessage(string memory recv_chainid, address recv_contract, string memory content) public {
        message.recv_chainid = recv_chainid;
        message.recv_contract = recv_contract;
        message.content = content;
    }

    function sendMessageToBridge() public {
        bridgeContract.chainToBridge(message.recv_chainid, message.recv_contract, message.content);
    }

    function verify(string memory content) public only_bridge  {
        result = content;
    }

    modifier only_bridge() { 
        require (msg.sender == bridge_addr, "Only the signer can call this function.");
        _;
    }
}