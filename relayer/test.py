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

# ca_url = "http://127.0.0.1:6001"
# response = requests.get(ca_url+"/basic_info")
# print(response)
# print(response.status_code)
# print(response.content)
# print(response.text)

# text = "V	250311085647Z		01	unknown	/C=CN/ST=Hubei/O=CC-ETH-CrossChain/OU=supervisor/CN=http://127.0.0.1:5001"

# with open("../supervisor/demoCA/index.txt", "r") as f:
#     text = f.read()
# print(text)
# match = re.findall(r'/OU=(\w+)/CN=', text)
# print(match)