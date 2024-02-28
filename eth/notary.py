from web3 import *
from eth_event import decode_logs, get_topic_map
import json
# 两个公证人发消息可以通过ip:port
# 连接到以太坊节点
web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
# 打印当前区块链信息 设置并解锁默认账户
print("Connected to Ethereum network:", web3.is_connected())
print("Current block number:", web3.eth.block_number)
web3.eth.default_account = web3.eth.accounts[0]
web3.geth.personal.unlock_account(web3.eth.default_account, "1234")

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