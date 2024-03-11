# 中继模块
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

# 生成私钥，向监管模块申请证书
def get_privkey_and_cert():
    # logging = logging.getlogging("[relayer]")
    if os.path.exists("./relayer.crt"):
        logger.info("privkey, csr, cert exist")
    else:
        try:
            result = subprocess.run("openssl genrsa -out relayer.key", shell=True, capture_output=True, text=True)
            logger.info(result.stdout)
            logger.error(result.stderr)
            result = subprocess.run("openssl req -new -key relayer.key -out relayer.csr -config openssl.cnf -batch", shell=True, capture_output=True, text=True)
            logger.info(result.stdout)
            logger.error(result.stderr)
        except:
            logger.error(traceback.format_exc())
    
        time.sleep(2)
        ca_url = "http://127.0.0.1:5001"
        files = {"csr": open("./relayer.csr", "rb")}
        response = requests.post(ca_url+"/sign_cert", files=files)
        if response.status_code == 200:
            with open("./relayer.crt", "wb") as f:
                f.write(response.content)
            logger.info("succeed to create privkey, csr, cert")
        else:
            logger.error(response.text)

@app.route("/basic_info", methods=["GET"])
def get_base_info():
    result = subprocess.run("openssl req -in relayer.csr -subject -noout", shell=True, capture_output=True, text=True)
    basic_info = result.stdout
    # print(type(basic_info)) # str
    basic_info_list = re.findall(r"(\b\w+) = ([^,\n]+)", basic_info)
    basic_info_dict = {key: value for key, value in basic_info_list}
    return jsonify(basic_info_dict)

def stop_relayer(sig, frame):
    print("[relayer] STOP.")
    exit()

if __name__ == "__main__":
    logger.info("------------------")
    init_thread = Thread(target=get_privkey_and_cert, daemon=True)
    init_thread.start()
    signal.signal(signal.SIGINT, stop_relayer)
    print("[relayer] START listening at 127.0.0.1:6001")
    waitress.serve(app, host="127.0.0.1", port=6001)
