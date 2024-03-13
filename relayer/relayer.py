# 中继模块
import hashlib
import json
import logging
import os
import re
import requests
import signal
import subprocess
import time
import traceback
import waitress
from flask import Flask, request, jsonify
from threading import Thread

# logger = logging.getLogger("[relayer]")
# logger.setLevel(logging.DEBUG)
# hdr = logging.FileHandler("./relayer.log")
# formatter = logging.Formatter('[%(asctime)s] %(name)s:%(levelname)s: %(message)s')
# hdr.setFormatter(formatter)
# logger.addHandler(hdr)

logging.basicConfig(level=logging.DEBUG,  
                    format='[%(asctime)s] %(name)s:%(levelname)s: %(message)s',  
                    filename='./relayer.log',  
                    filemode='a') 
logger = logging.getLogger()

app = Flask(__name__)
index = 1
domain_list = []
ca_url = "http://127.0.0.1:5001"
match_subject = "/C=CN/ST=Hubei/O=CC-ETH-CrossChain"

# 生成私钥，向监管模块申请证书
def init():
    # logging = logging.getlogging("[relayer]")
    if os.path.exists("./demo/relayer.crt"):
        logger.info("privkey, csr, cert exist")
    else:
        subprocess.run("mkdir demo ./demo/chainInfo ./demo/chaincrt", shell=True)
        subprocess.run("touch ./demo/index.txt", shell=True)            
        get_privkey_and_cert()
    
    # 将已注册的域名放入内存待用
    global domain_list
    with open("./demo/index.txt", "r") as f:
        for line in f:
            parts = line.strip().split(",")
            domain_list.append(parts[1])


def get_privkey_and_cert():
    try:
        result = subprocess.run("openssl genrsa -out ./demo/relayer.key", shell=True, capture_output=True, text=True)
        logger.info(result.stdout)
        logger.error(result.stderr)
        result = subprocess.run("openssl req -new -key ./demo/relayer.key -out ./demo/relayer.csr -config openssl.cnf -batch", shell=True, capture_output=True, text=True)
        logger.info(result.stdout)
        logger.error(result.stderr)
    except:
        logger.error(traceback.format_exc())
    
    time.sleep(2)
    files = {"csr": open("./demo/relayer.csr", "rb")}
    response = requests.post(ca_url+"/sign_relayer_cert", files=files)
    if response.status_code == 200:
        with open("./demo/relayer.crt", "wb") as f:
            f.write(response.content)
        logger.info("succeed to create privkey, csr, cert")
    else:
        logger.error(response.text)


@app.route("/basic_info", methods=["GET"])
def get_base_info():
    result = subprocess.run("openssl req -in ./demo/relayer.csr -subject -noout", shell=True, capture_output=True, text=True)
    basic_info = result.stdout
    # print(type(basic_info)) # str
    basic_info_list = re.findall(r"(\b\w+) = ([^,\n]+)", basic_info)
    basic_info_dict = {key: value for key, value in basic_info_list}
    return jsonify(basic_info_dict)


@app.route("/register_chain", methods=["POST"])
def register_chain():
    global index
    data = request.json
    # print(type(data))
    # print(data)
    # return "test ok", 400
    file_content = data["chainInfo"]
    file_hash = data["hash"]
    # print(type(file_content))
    # print(type(file_hash))
    # return "test ok", 400
    computed_hash = hashlib.sha256(file_content.encode()).hexdigest()
    if computed_hash != file_hash:
        return "fail to verify hash value", 400
    chain_info = json.loads(file_content)
    # 检查域名是否已经存在
    domain_name = chain_info["domainName"]
    if domain_name in domain_list:
        return "domain name has been registered", 400
    # 向监管模块申请证书
    csr_subject = match_subject + "/OU=" + domain_name + "/CN=" + file_hash
    subprocess.run("openssl req -new -key ./demo/relayer.key -out ./demo/tmp.csr -subj " + csr_subject, shell=True)
    files = {"csr": open("./demo/tmp.csr", "rb")}
    data1 = {"json": json.dumps(data)}
    response = requests.post(ca_url+"/sign_chain_cert", files=files, data=data1)
    if response.status_code == 200:
        # 更新内存 保存链配置文件&证书&index.txt 删除csr index加1
        domain_list.append(domain_name)
        chain_info_path = os.path.join("./demo/chainInfo/", str(index)+".json")
        chain_cert_path = os.path.join("./demo/chaincrt/", str(index)+".crt")
        with open(chain_info_path, "w") as f:
            json.dump(chain_info, f)
        with open(chain_cert_path, "wb") as f:
            f.write(response.content)
        with open("./demo/index.txt", "a") as f:
             f.write(f"{index},{domain_name}\n")
        subprocess.run("rm -f ./demo/tmp.csr", shell=True)
        index += 1
        logger.info("succeed to register chain [%s]", domain_name)
        return response.content, 200
    else:
        logger.error(response.text)
        return response.text, 400


def stop_relayer(sig, frame):
    print("[relayer] STOP.")
    exit()


if __name__ == "__main__":
    logger.info("------------------")
    init_thread = Thread(target=init, daemon=True)
    init_thread.start()
    signal.signal(signal.SIGINT, stop_relayer)
    print("[relayer] START listening at 127.0.0.1:6001")
    waitress.serve(app, host="127.0.0.1", port=6001)
