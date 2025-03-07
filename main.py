import utils
import requests
import sys
import time

from web3 import Account
from fake_useragent import UserAgent

privates = utils.read_lines("privates.txt")
proxies = utils.read_lines("proxies.txt")

if input("Check proxies? y/n: ") == "y":
    good_proxies = utils.check_proxies(proxies)

    if len(good_proxies) < len(privates):
        print(f"Not enough valid proxies. [{len(good_proxies)} / {len(privates)}]")
        sys.exit()
    proxies = good_proxies

message_to_sign = "By signing this message, I confirm that I have read and agreed to Plume's Airdrop Terms of Service. This does not cost any gas to sign."

sleep_time = int(input("Sleep time between requests in seconds: "))
start_from_address = input("Address to start from (enter if start from beginning): ").lower()

start = False
for private, proxy in zip(privates, proxies):
    account = Account.from_key(private)
    if start_from_address and start_from_address in account.address.lower():
        start = True
    elif start_from_address and not start:
        continue
    elif start_from_address and start:
        pass

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://registration.plumenetwork.xyz',
        'priority': 'u=1, i',
        'referer': 'https://registration.plumenetwork.xyz/',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': UserAgent().random,
    }

    json_data = {
        'message': message_to_sign,
        'signature': utils.sign_message(account, message_to_sign),
        'address': account.address,
        'twitterEncryptedUsername': None,
        'twitterEncryptedId': None,
        'discordEncryptedUsername': None,
        'discordEncryptedId': None,
    }

    response = requests.post(
        'https://registration.plumenetwork.xyz/api/sign-write',
        headers=headers,
        json=json_data,
        proxies={
            "http": proxy,
            "https": proxy
        }
    )
    print(account.address, response.status_code, response.text)
    time.sleep(sleep_time)
