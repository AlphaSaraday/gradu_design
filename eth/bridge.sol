// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ethBridge {
    struct MessageToOthers {
        string send_chainid;
        address send_contract;
        string recv_chainid;
        address recv_contract;
        string message;
    }
    MessageToOthers public msg_to_notary;
    event CrossChain(bool direction, string content, address sender);

    constructor() {
        msg_to_notary.send_chainid = "none";
        msg_to_notary.send_contract = address(0);
        msg_to_notary.recv_chainid = "none";
        msg_to_notary.recv_contract = address(0);
        msg_to_notary.message = "none";
    }

    // 跨链桥接收业务合约消息
    function chainToBridge(string memory recv_chainid, address recv_contract, string memory content) public {
        msg_to_notary.send_chainid = "ethereum";
        msg_to_notary.send_contract = msg.sender;
        msg_to_notary.recv_chainid = recv_chainid;
        msg_to_notary.recv_contract = recv_contract;
        msg_to_notary.message = content;
        bool direction = true;
        string memory messageStr = string(abi.encodePacked("sendid:",msg_to_notary.send_chainid,
                                                        ";recvid:",msg_to_notary.recv_chainid,
                                                        ";sendcon:",toString(msg_to_notary.send_contract),
                                                        ";recvcon:",toString(msg_to_notary.recv_contract),
                                                        ";message:",msg_to_notary.message));
        emit CrossChain(direction, messageStr, msg_to_notary.send_contract);
    }

    // 跨链桥接收公证人消息
    function notaryToBridge(string memory send_chainid, address send_contract, address recv_contract, string memory content) public {
        msg_to_notary.send_chainid = send_chainid;
        msg_to_notary.send_contract = send_contract;
        msg_to_notary.recv_chainid = "ethereum";
        msg_to_notary.recv_contract = recv_contract;
        msg_to_notary.message = content;
        bool direction = false;
        string memory messageStr = string(abi.encodePacked("sendid:",msg_to_notary.send_chainid,
                                                        ";recvid:",msg_to_notary.recv_chainid,
                                                        ";sendcon:",toString(msg_to_notary.send_contract),
                                                        ";recvcon:",toString(msg_to_notary.recv_contract),
                                                        ";message:",msg_to_notary.message));
        emit CrossChain(direction, messageStr, msg_to_notary.send_contract);
    }

    function toString(address addr) public pure returns (string memory) {
        bytes20 value = bytes20(uint160(addr));
        bytes memory alphabet = "0123456789abcdef";
        bytes memory str = new bytes(42);
        str[0] = '0';
        str[1] = 'x';
        for (uint256 i = 0; i < 20; i++) {
            str[2 + i * 2] = alphabet[uint8(value[i] >> 4)];
            str[3 + i * 2] = alphabet[uint8(value[i] & 0x0f)];
        }
        return string(str);
    }
}