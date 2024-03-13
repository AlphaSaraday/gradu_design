const { default: Web3 } = require("web3");

var web3 = new Web3('http://localhost:7545');

// 获取节点信息
web3.eth.getNodeInfo()
  .then(nodeInfo => {
    console.log('节点信息：', nodeInfo);
  })
  .catch(error => {
    console.error('获取节点信息失败：', error);
  });te