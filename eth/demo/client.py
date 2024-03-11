from web3 import *
from eth_event import decode_logs, get_topic_map
import json
# 连接到以太坊节点
web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
# 打印当前区块链信息 设置并解锁默认账户
print("Connected to Ethereum network:", web3.is_connected())
print("Current block number:", web3.eth.block_number)
web3.eth.default_account = web3.eth.accounts[0]
web3.geth.personal.unlock_account(web3.eth.default_account, "1234")

with open("bytecode.json", "r") as f:
    bytecode = json.load(f)
    bridge_bytecode = bytecode["bridge"]
    bussiness_bytecode = bytecode["bussiness"]

with open("bridge.json", "r") as f:
    bridge_abi = json.load(f)

with open("bussiness.json", "r") as f:
    bussiness_abi = json.load(f)

#region
# bridge = web3.eth.contract(abi = bridge_abi, bytecode = bridge_bytecode)
# txhash = bridge.constructor().transact()
# tx_receipt = web3.eth.wait_for_transaction_receipt(txhash)
# bridge_addr = tx_receipt.contractAddress
# print("bridge_addr:", bridge_addr)

# bussiness = web3.eth.contract(abi = bussiness_abi, bytecode= bussiness_bytecode)
# txhash = bussiness.constructor(bridge_addr).transact()
# tx_receipt = web3.eth.wait_for_transaction_receipt(txhash)
# bussiness_addr = tx_receipt.contractAddress
# print("bussiness_addr:", bussiness_addr)
#endregion

bridge_addr = '''0xA8df466aA54fff29Db5338BfE0AA766Ba79B622c'''
bussiness_addr = '''0xEcf835C55e4D77348DD6BB46a3c18d71fd1E3aF8'''

# 测试跨合约调用是否有日志(有)
# bussiness = web3.eth.contract(address=bussiness_addr, abi=bussiness_abi)
# bridge = web3.eth.contract(address = bridge_addr, abi = bridge_abi)

# txhash = bussiness.functions.fillMessage('''aaaaaa''').transact()
# tx_receipt = web3.eth.wait_for_transaction_receipt(txhash)
# txhash = bussiness.functions.sendMessageToBridge().transact()
# tx_receipt = web3.eth.wait_for_transaction_receipt(txhash)


# 查看区块的日志
logfilter = {}
logfilter['fromBlock'] = 68
logfilter['toBlock'] = 118
logs = web3.eth.get_logs(logfilter)
real_logs = decode_logs(logs=logs, topic_map=get_topic_map(bridge_abi))
with open("logs.json", "w") as f:
    for log in real_logs:
        json.dump(log, f, indent=4)
print("OK")
