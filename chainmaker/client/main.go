// client
package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"time"

	"chainmaker.org/chainmaker/pb-go/v3/common"
	sdk "chainmaker.org/chainmaker/sdk-go/v3"
	"chainmaker.org/chainmaker/sdk-go/v3/examples"
)

const (
	sdk_config_path = "../sdk_config_for_code.yml"
	contract_name   = "contract_bridge"
	version         = "1.0.0"
	bytecode_path   = "../contract_bridge/contract_bridge.7z"
	runtime         = common.RuntimeType_DOCKER_GO
)

func main() {
	// open logfile
	log_file, err := os.OpenFile("cc.log", os.O_WRONLY|os.O_CREATE|os.O_APPEND, 0644)
	if err != nil {
		fmt.Println("Error opening logfile:", err)
		return
	}
	defer log_file.Close()
	log.SetOutput(log_file)
	log.SetPrefix("[cc_client] ")
	log.SetFlags(log.LstdFlags)
	log.Println("log begin.")

	client, err := createClientWithConfig(sdk_config_path)
	panicErr(err, "---createClientWithConfig")
	defer client.Stop()

	create_contract_payload, err := client.CreateContractCreatePayload(contract_name, version, bytecode_path, runtime, nil)
	panicErr(err, "---CreateContractCreatePayload")
	endorser_list, err := examples.GetEndorsers(create_contract_payload, []string{"org1admin1", "org2admin2", "org2admin3"}...)
	panicErr(err, "---GetEndorsers")
	log.Printf("\ncreate contract endorser_list: %v\n", endorser_list)
	create_resp, err := client.SendContractManageRequest(create_contract_payload, endorser_list, -1, false)
	panicErr(err, "---SendContractManageRequest")
	log.Printf("\ncreate contract txid: %v\n", create_resp.TxId)

	// subscribe event
	dg_ctx, dg_cancel_func := context.WithTimeout(context.Background(), time.Duration(time.Second*30))
	defer dg_cancel_func()
	sub_result, _ := client.SubscribeContractEvent(dg_ctx, -1, -1, contract_name, "CrossChain")

	params := genParams()
	invoke_resp, err := client.InvokeContract(contract_name, "chainToBridge", "", params, -1, true)
	panicErr(err, "---InvokeContract")
	log.Printf("\ninvoke contract success: %v\n", invoke_resp)

	if sub_result != nil {
		log.Printf("sub_result: %v\n", sub_result)
	}

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
