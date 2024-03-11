# 申请者:提供1)区块链A的必要配置信息eth.jsond的哈希作为CN，2)自定义的string类型的域名作为OU   发送给中继模块
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

logging.basicConfig(level=logging.DEBUG,  
                    format='[%(asctime)s] %(name)s:%(levelname)s: %(message)s',  
                    filename='./apply.log',  
                    filemode='a') 
logger = logging.getLogger()

if __name__ == "__main__":
    logger.info("start to apply domain and cert")
    