// client
package main

import (
	"fmt"
	"log"
	"os"

	sdk "chainmaker.org/chainmaker/sdk-go/v3"
)

const (
	sdk_config_path  = "/home/saraday/chainmaker/chainmaker-go/tools/cmc/testdata/sdk_config.yml"
	contract_name    = ""
	version          = ""
	dg_bytecode_path = ""
	dg_runtime       = ""
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

	// client, err := createClientWithConfig(sdk_config_path)
	// chain_config, err := client.GetChainConfig()
	// panicErr(err)
	// log.Printf("\nCreate client successfully! Chain configs are as follows:\n%v\n", chain_config)

	// create_contract_payload, err := client.CreateContractCreatePayload(contract_name, version, dg_bytecode_path, dg_runtime, nil)
	// panicErr(err)

	// endorser_list, err := examples.GetEndorsers(create_contract_payload, []string{"org1admin1", "org2admin2", "org2admin3"}...)
	// panicErr(err)

	// create_resp, err := client.SendContractManageRequest(create_contract_payload, endorser_list, -1, false)
	// panicErr(err)
	// log.Printf("\ncreate contract txid: %v\n", create_resp.TxId)

}

func panicErr(err error) {
	if err != nil {
		log.Fatalln(err.Error())
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
