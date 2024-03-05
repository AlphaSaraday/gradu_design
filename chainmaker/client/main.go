// client
package main

import (
	"context"
	"log"
	"os"
	"time"

	"chainmaker.org/chainmaker/pb-go/v3/common"
	sdk "chainmaker.org/chainmaker/sdk-go/v3"
)

const (
	sdk_config_path = "../sdk_config_for_code.yml"
	contract_name   = "contract_bridge"
	version         = "1.0.0"
	bytecode_path   = "../contract_bridge/contract_bridge.7z"
	runtime         = common.RuntimeType_DOCKER_GO
)

func main() {
	// 日志
	log_file, err := os.OpenFile("cc.log", os.O_WRONLY|os.O_CREATE|os.O_APPEND, 0644)
	panicErr(err, "Error opening logfile")
	defer log_file.Close()
	log.SetOutput(log_file)
	log.SetFlags(0)
	log.Println("")
	log.SetPrefix("[cc_client] ")
	log.SetFlags(log.LstdFlags)
	log.Println("log begin.")
	// 创建客户端
	client, err := createClientWithConfig(sdk_config_path)
	panicErr(err, "---createClientWithConfig")
	defer client.Stop()
	// // 部署跨链桥合约上链
	// // 1.生成[创建合约待签名的payload]
	// create_contract_payload, err := client.CreateContractCreatePayload(contract_name, version, bytecode_path, runtime, nil)
	// panicErr(err, "---CreateContractCreatePayload")
	// endorser_list, err := examples.GetEndorsers(create_contract_payload, []string{"org1admin1", "org2admin1", "org3admin1"}...)
	// panicErr(err, "---GetEndorsers")
	// // 2.订阅创建合约的交易
	// dg_ctx, dg_cancel_func := context.WithTimeout(context.Background(), time.Duration(time.Second*30))
	// defer dg_cancel_func()
	// var dg_txids []string
	// dg_sub, _ := client.SubscribeTx(dg_ctx, -1, -1, "", dg_txids)
	// // 3.发送合约管理请求
	// create_resp, err := client.SendContractManageRequest(create_contract_payload, endorser_list, -1, false)
	// panicErr(err, "---SendContractManageRequest")
	// log.Printf("create contract txid: %v\n", create_resp.TxId)
	// // 4.接收订阅的交易消息
	// dg_txids = append(dg_txids, create_resp.TxId)
	// select {
	// case txI, ok := <-dg_sub:
	// 	if !ok {
	// 		log.Fatalln("rpc connect failed")
	// 	}
	// 	tx, _ := txI.(*common.Transaction)
	// 	log.Printf("subscribe create contract %v message: \n%v\n", create_resp.TxId, tx.GetResult())
	// case <-dg_ctx.Done():
	// 	log.Fatalln("subscribe message time out")
	// }
	// time.Sleep(time.Duration(2) * time.Second)
	// 5.查询合约状态
	// contract_info, err := client.GetContractInfo(contract_name)
	// panicErr(err, "---GetContractInfo")
	// log.Printf("contract %v status: \n%v\n", contract_info.Name, contract_info)

	// 订阅事件
	dg_ctx1, dg_cancel_func1 := context.WithTimeout(context.Background(), time.Duration(time.Second*20))
	defer dg_cancel_func1()
	dg_sub1, _ := client.SubscribeContractEvent(dg_ctx1, -1, -1, contract_name, "CrossChain")

	// 调用chainToBridge函数
	params := genParams()
	invoke_resp, err := client.InvokeContract(contract_name, "chainToBridge", "", params, -1, true)
	panicErr(err, "---InvokeContract")
	log.Printf("invoke contract success: \n%v\n", invoke_resp)

	select {
	case con_events, ok := <-dg_sub1:
		if !ok {
			log.Fatalln("rpc connect failed")
		}
		con_event, _ := con_events.(*common.ContractEventInfo)
		log.Printf("subscribe contract event message: \nblock height: %v\nchainid: %v\ntopic: %v\n"+
			"txid: %v\neventindex: %v\ncontract name: %v\ncontract version: %v\neventdata: %v\nindexcount: %v\n",
			con_event.GetBlockHeight(), con_event.GetChainId(), con_event.GetTopic(), con_event.GetTxId(), con_event.GetEventIndex(),
			con_event.GetContractName(), con_event.GetContractVersion(), con_event.GetEventData(), con_event.GetIndexCount())
	case <-dg_ctx1.Done():
		log.Fatalln("subscribe message time out")
	}
	time.Sleep(time.Duration(2) * time.Second)
}

func panicErr(err error, msg string) {
	if err != nil {
		log.Fatalln(err.Error(), msg)
	}
}

func createClientWithConfig(sdk_config_Path string) (*sdk.ChainClient, error) {
	cc, err := sdk.NewChainClient(sdk.WithConfPath(sdk_config_Path))
	if err != nil {
		return nil, err
	}
	if cc.GetAuthType() == sdk.PermissionedWithCert {
		if err := cc.EnableCertHash(); err != nil {
			return nil, err
		}
	}
	return cc, err
}

func genParams() []*common.KeyValuePair {
	params := []*common.KeyValuePair{
		{
			Key:   "send_contract",
			Value: []byte("test-contract"),
		},
		{
			Key:   "recv_chainid",
			Value: []byte("ethereum"),
		},
		{
			Key:   "recv_contract",
			Value: []byte("0xA8df466aA54fff29Db5338BfE0AA766Ba79B622c"),
		},
		{
			Key:   "content",
			Value: []byte("hello i am lzl"),
		},
	}
	return params
}
