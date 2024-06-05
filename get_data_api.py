import requests
import logging
import time
import json
import os
PATH = os.path.dirname(os.path.realpath(__file__)) + "/"

with open(PATH + "user_data.json", "r") as file:
    user_data = json.load(file)
    user_data["msisdn"] = int(user_data["msisdn"])
    print(user_data)
tokens_url = "https://my.te.eg/echannel/service/besapp/base/rest/busiservice/v1/auth/userAuthenticate"

tokens_headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9,ar-EG;q=0.8,ar;q=0.7",
    "Connection": "keep-alive",
    "Content-Length": "120",
    "Content-Type": "application/json",
    "Host": "my.te.eg",
    "Origin": "https://my.te.eg",
    "Referer": "https://my.te.eg/echannel/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "channelId": "702",
    "csrftoken": "",
    "delegatorSubsId": "",
    "isCoporate": "false",
    "isMobile": "false",
    "isSelfcare": "true",
    "languageCode": "en-US",
    "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Linux\""
}

tokens_payload = {
    "acctId": f"FBB{user_data['msisdn']}",
    "password": user_data["password"],
    "appLocale": "en-US",
    "isSelfcare": "Y",
    "isMobile": "N",
    "recaptchaToken": "",
}

def get_request_params():
    response = requests.post(tokens_url, headers=tokens_headers, json=tokens_payload)
    data = response.json()
    # print(json.dumps(data, indent=4))
    if data.get("body") is not None:
        csrftoken = data["body"]["token"]
        indiv_login_token = data["body"]["utoken"]
        subscriber_id = data["body"]["subscriber"]["subscriberId"]
        return csrftoken, indiv_login_token, subscriber_id
    return None, None, None


data_url = "https://my.te.eg/echannel/service/besapp/base/rest/busiservice/cz/cbs/bb/queryFreeUnit"
request_headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9,ar-EG;q=0.8,ar;q=0.7",
    "Channelid": "702",
    "Connection": "keep-alive",
    "Content-Length": "27",
    "Content-Type": "application/json",
    "Delegatorsubsid": "",
    "Host": "my.te.eg",
    "Iscoporate": "false",
    "Ismobile": "false",
    "Isselfcare": "true",
    "Languagecode": "en-US",
    "Origin": "https://my.te.eg",
    "Referer": "https://my.te.eg/echannel/",
    "Sec-Ch-Ua": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Linux"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
}

generate_request_coockies = lambda indiv_login_token:f"_ga=GA1.3.939407918.1692936222; _tt_enable_cookie=1; _ttp=rX1m-nGXsuVxGYk59Bwv5d7jDU4; _ga=GA1.1.939407918.1692936222; _gcl_au=1.1.383667643.1715546338; _fbp=fb.1.1715546338174.1288707767; _ga_233C94050H=GS1.1.1715583508.5.0.1715583508.60.0.0; _ga_P78FD21ZQ7=GS1.3.1715583508.2.0.1715583508.60.0.0; route=9f505a74cf9b5ad798559070a0d61dde; indiv_login_token={indiv_login_token}; TS01fa9144=010aa23b1df9276a16f0e633e20fbcd95dad200d2939a1020a02098e708a3624d2379b5e49fc16c0576549b5be40b90e6501ccd5964134cb31f9e502029542be298f38eefe7f816a996021e6ed28300de49315f0c7; TS01bba117=010aa23b1db65fdc8c8e5a289be8cd79dc05d5354539a1020a02098e708a3624d2379b5e49fc16c0576549b5be40b90e6501ccd59684ad7bf49d32d2925cd4f0d5351a24d80a6ef9779035dcaaa867c1f4f0ece5e15d666f0ef0888618ef20ed97ff6e237d; dtCookie=v_4_srv_52_sn_6BA6CE10D56CDBECEFEC0076C71CECB0_perc_100000_ol_0_mul_1_app-3A6032d7aeebe38554_1"

def get_user_data():
    csrftoken, indiv_login_token, subscriber_id = get_request_params()
    logging.info(f"csrftoken: {csrftoken}")
    logging.info(f"indiv_login_token: {indiv_login_token}")
    logging.info(f"subscriber_id: {subscriber_id}")
    request_payload = {"subscriberId": subscriber_id}
    request_headers["Csrftoken"] = csrftoken
    request_headers["Cookie"] = generate_request_coockies(indiv_login_token)
    try:
        response = requests.post(data_url, headers=request_headers, json=request_payload)
        data = response.json()
        if data["body"] is not None:
            # print(json.dumps(data, indent=4))
            remaining = data["body"][0]["freeUnitBeanDetailList"][0]["currentAmount"]
            logging.info(f"remaining: {remaining}")
            return remaining
    except:
        return None



if __name__ == "__main__":
    print(get_user_data())
