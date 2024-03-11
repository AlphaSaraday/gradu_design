// 跨链合约模块
package main

import (
	"log"

	"chainmaker.org/chainmaker/contract-sdk-go/v2/pb/protogo"
	"chainmaker.org/chainmaker/contract-sdk-go/v2/sandbox"
	"chainmaker.org/chainmaker/contract-sdk-go/v2/sdk"
)

type BridgeContract struct {
}

type MessageToOthers struct {
	send_chainid  string
	send_contract string
	recv_chainid  string
	recv_contract string
	message       string
}

func NewMessageToOthers(send_chainid, send_contract, recv_chainid, recv_contract, message string) *MessageToOthers {
	return &MessageToOthers{
		send_chainid:  send_chainid,
		send_contract: send_contract,
		recv_chainid:  recv_chainid,
		recv_contract: recv_contract,
		message:       message,
	}
}

func (f *BridgeContract) InitContract() protogo.Response {
	return sdk.Success([]byte("Init contract success"))
}

func (f *BridgeContract) UpgradeContract() protogo.Response {
	return sdk.Success([]byte("Upgrade contract success"))
}

func (f *BridgeContract) InvokeContract(method string) protogo.Response {
	switch method {
	case "chainToBridge":
		return f.chainToBridge()
	default:
		return sdk.Error("invalid method")
	}
}

func (f *BridgeContract) chainToBridge() protogo.Response {
	params := sdk.Instance.GetArgs()
	send_contract := string(params["send_contract"])
	recv_chainid := string(params["recv_chainid"])
	recv_contract := string(params["recv_contract"])
	content := string(params["content"])
	// msg_to_notary := NewMessageToOthers("chainmaker", send_contract, recv_chainid, recv_contract, content)
	msg_to_notary := []string{"chainmaker", send_contract, recv_chainid, recv_contract, content}
	sdk.Instance.EmitEvent("CrossChain", msg_to_notary)
	sdk.Instance.Infof("[chainToBridge] chainmaker " + send_contract + recv_chainid + recv_contract + content)
	return sdk.Success([]byte("func chainToBridge success"))
}

func main() {
	err := sandbox.Start(new(BridgeContract))
	if err != nil {
		log.Fatal(err)
	}
}
