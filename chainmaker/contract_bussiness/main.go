package main

import (
	"log"

	"chainmaker.org/chainmaker/contract-sdk-go/v2/pb/protogo"
	"chainmaker.org/chainmaker/contract-sdk-go/v2/sandbox"
	"chainmaker.org/chainmaker/contract-sdk-go/v2/sdk"
)

type BussinessContract struct {
}

type Message struct {
	send_contract string
	recv_chainid  string
	recv_contract string
	content       string
}

// func NewMessage(send_contract, recv_chainid, recv_contract, message string) *Message {
// 	return &Message{
// 		send_contract: send_contract,
// 		recv_chainid:  recv_chainid,
// 		recv_contract: recv_contract,
// 		content:       message,
// 	}
// }

func (f *BussinessContract) InitContract() protogo.Response {
	return sdk.Success([]byte("Init contract success"))
}

func (f *BussinessContract) UpgradeContract() protogo.Response {
	return sdk.Success([]byte("Upgrade contract success"))
}

func (f *BussinessContract) InvokeContract(method string) protogo.Response {
	switch method {
	case "sendMessageToBridge":
		return f.sendMessageToBridge()
	default:
		return sdk.Error("invalid method")
	}
}

func (f *BussinessContract) sendMessageToBridge() protogo.Response {
	params := sdk.Instance.GetArgs()
	send_contract := string(params["send_contract"])
	recv_chainid := string(params["recv_chainid"])
	recv_contract := string(params["recv_contract"])
	content := string(params["content"])

	bridge_name := "contract_bridge"
	bridge_method := "chainToBridge"
	cross_args := make(map[string][]byte)
	cross_args["method"] = []byte(bridge_method)
	cross_args["send_contract"] = []byte(send_contract)
	cross_args["recv_chainid"] = []byte(recv_chainid)
	cross_args["recv_contract"] = []byte(recv_contract)
	cross_args["content"] = []byte(content)
	response := sdk.Instance.CallContract(bridge_name, bridge_method, cross_args)

	return response
}

func main() {
	err := sandbox.Start(new(BussinessContract))
	if err != nil {
		log.Fatal(err)
	}
}
