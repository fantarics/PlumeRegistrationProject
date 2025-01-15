import random
import time
from threading import Semaphore, Lock, Thread

import requests
import logging
from typing import Union
from urllib.parse import urlparse
from web3 import Web3
from eth_account.messages import encode_typed_data
from eth_account.signers.local import LocalAccount
from eth_account.messages import encode_defunct


# Function to parse proxy
def parse_proxy(proxy_string):
    parsed = urlparse(proxy_string)
    proxy_settings = {
        'server': f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
    }
    if parsed.username:
        proxy_settings['username'] = parsed.username
        proxy_settings['password'] = parsed.password
    return proxy_settings

def read_lines(path):
    return [i.strip() for i in open(path, "r").readlines() if "#" not in i]

def my_ip():
    return requests.get("https://api.myip.com").json().get("ip", "????")

proxies_semaphore = Semaphore(100)
proxy_lock = Lock()
def check_proxy(original_ip, proxy, good_proxies_list):
    with proxies_semaphore:
        proxies = {
            "http": proxy,
            "https": proxy
        }
        try:
            response = requests.get("https://api.myip.com", proxies=proxies, timeout=5)
            if response.status_code == 200:
                result = response.json()
                if result.get("ip") != original_ip:
                    with proxy_lock:
                        good_proxies_list.append(proxy)
                else:
                    return False
        except Exception as e:
            return False

def check_proxies(proxies):
    original_ip = my_ip()
    proxy_check_threads = []
    valid_proxies = []
    for proxy in proxies:
        check_proxy_thread = Thread(
            target=check_proxy,
            args=(original_ip, proxy, valid_proxies)
        )
        check_proxy_thread.start()
        proxy_check_threads.append(check_proxy_thread)
    for thread in proxy_check_threads:
        thread.join()
    print(f"Using {len(valid_proxies)} valid proxies / {len(proxies)} provided")
    return valid_proxies

def sign_message(account, msg: Union[dict, str]):
    if isinstance(msg, dict):
        encoded_msg = encode_typed_data(
            full_message=msg
        )
    elif isinstance(msg, str):
        encoded_msg = encode_defunct(
            text=msg
        )
    else:
        raise TypeError("No such type for signature")
    signed_msg = account.sign_message(encoded_msg)
    result = signed_msg.signature.hex()
    if not result.startswith("0x"):
        result = "0x" + result
    return result
