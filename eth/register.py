# 申请者:身份是链的一个外部账户，提供区块链A的必要配置信息eth.json给中继模块，其中包含想要申请的域名名称
import hashlib
import json
import logging
import os
import requests
import subprocess
from web3 import *
from flask import Flask, request, jsonify
from threading import Thread

# logging.basicConfig(level=logging.DEBUG,  
#                     format='[%(asctime)s] %(name)s:%(levelname)s: %(message)s',  
#                     filename='./register.log',  
#                     filemode='a') 
# logger = logging.getLogger()

# 读取eht.json文件并发送 原文 & 签名 & 公钥，中继模块可以自行验证
# def gen_privkey():
#     privkey_path = "register.key"
#     pubkey_path = "register.pkey"
#     if os.path.exists(privkey_path):
#         print("privkey exist")
#     subprocess.run("openssl genrsa -out " + privkey_path, shell=True, capture_output=True, text=True)
#     subprocess.run("openssl rsa -in " + privkey_path + " -pubout -out " + pubkey_path, shell=True, capture_output=True, text=True)

def send_to_relayer(file_path, url):
    with open(file_path, "rb") as f:
        chain_info = f.read()
    file_hash = hashlib.sha256(chain_info).hexdigest()
    data = {"chainInfo": chain_info, "hash": file_hash}
    response = requests.post(url+"/register_chain", json=data)
    return response


if __name__ == "__main__":
    print("start to register domain and cert")
    # web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
    # if web3.is_connected() == False:
    #     print("fail to connect ganache")
    #     exit()
    response = send_to_relayer("eth.json", "http://127.0.0.1:6001")
    if response.status_code == 200:
        with open("./eth.crt", "wb") as f:
            f.write(response.content)
            print("succeed to register")
    else:
        print(response.text)
    