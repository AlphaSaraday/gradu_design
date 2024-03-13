# 监管模块
import json
import logging
import os
import re
import requests
import signal
import subprocess
import traceback
import waitress
from flask import Flask, request, jsonify, send_file

# logger = logging.getLogger("[supervisor]")
# logger.setLevel(logging.DEBUG)
# hdr = logging.FileHandler("./supervisor.log")
# formatter = logging.Formatter('[%(asctime)s] %(name)s:%(levelname)s: %(message)s')
# hdr.setFormatter(formatter)
# logger.addHandler(hdr)
logging.basicConfig(level=logging.DEBUG,  
                    format='[%(asctime)s] %(name)s:%(levelname)s: %(message)s',  
                    filename='./supervisor.log',  
                    filemode='a') 
logger = logging.getLogger()

app = Flask(__name__)

# generate_root_cert：使用OpenSSL生成监管程序的私钥和自签名证书
def generate_root_cert():
    if os.path.exists("./demoCA/cacert.pem"):
        logger.info("CA's privkey, csr, cert exist")
    else:
        try:
            subprocess.run("mkdir demoCA ./demoCA/certs ./demoCA/crl ./demoCA/newcerts ./demoCA/private ./demoCA/csr ./demoCA/chainInfo", shell=True)
            subprocess.run("touch ./demoCA/index.txt; echo '01' > ./demoCA/serial", shell=True)
            result = subprocess.run("openssl genrsa -out ./demoCA/private/cakey.pem", shell=True, capture_output=True, text=True)
            logger.info(result.stdout)
            logger.error(result.stderr)
            subprocess.run("openssl req -new -key ./demoCA/private/cakey.pem -out ./demoCA/csr/ca.csr -config openssl.cnf -batch", shell=True)
            result = subprocess.run("openssl ca -selfsign -in ./demoCA/csr/ca.csr -config openssl.cnf -batch", shell=True, capture_output=True, text=True)
            logger.info(result.stdout)
            logger.error(result.stderr)
            subprocess.run("cp ./demoCA/newcerts/01.pem ./demoCA/cacert.pem", shell=True)
        except:
            logger.error(traceback.format_exc())


def sign_cert(csr_path):
    result = subprocess.run("openssl ca -in " + csr_path + " -config openssl.cnf -batch", shell=True, capture_output=True, text=True)
    logger.info(result.stdout)
    logger.error(result.stderr)
    with open("./demoCA/serial.old", "r") as f:
        serial = f.read()
        serial = serial.rstrip("\n")
    crt_path = "./demoCA/newcerts/" + serial + ".pem"
    return crt_path


@app.route('/test', methods=['GET'])
def test():
    return send_file("./supervisor.log")


@app.route('/sign_relayer_cert', methods=['POST'])
def sign_relayer_cert():
    csr_file = request.files["csr"]
    csr_path = os.path.join("./demoCA/csr/", csr_file.filename)
    csr_file.save(csr_path)
    # 验证csr中的信息
    result = subprocess.run("openssl req -in " + csr_path + " -subject -noout", shell=True, capture_output=True, text=True)
    verify_info = result.stdout
    verify_info_list = re.findall(r"(\b\w+) = ([^,\n]+)", verify_info)
    verify_info_dict = {key: value for key, value in verify_info_list}
    url = verify_info_dict["CN"] + "/basic_info"
    response = requests.get(url)
    real_info_dict = response.json()
    if verify_info_dict != real_info_dict:
        return "fail to verify the basic info", 400
    # 签署证书并传回
    crt_path = sign_cert(csr_path)
    return send_file(crt_path)


@app.route('/sign_chain_cert', methods=['POST'])
def sign_chain_cert():
    # 暂存csr, 保存链配置信息
    csr_file = request.files["csr"]
    csr_path = os.path.join("./demoCA/csr/", csr_file.filename)
    csr_file.save(csr_path)
    data = json.loads(request.form["json"])
    chain_info = json.loads(data["chainInfo"])
    with open("./demoCA/chainInfo/"+ chain_info["domainName"] + ".json", "w") as f:
        json.dump(chain_info, f)
    # 签署证书并传回
    crt_path = sign_cert(csr_path)
    subprocess.run("rm -f " + csr_path, shell=True)
    return send_file(crt_path)


def stop_supervisor(sig, frame):
    print("[supervisor] STOP.")
    exit()


if __name__ == '__main__':
    logger.info("------------------")
    generate_root_cert()
    signal.signal(signal.SIGINT, stop_supervisor)
    print("[supervisor] START listening at 127.0.0.1:5001")
    waitress.serve(app, host="127.0.0.1", port=5001)
