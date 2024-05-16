import requests
import time
base_url = "https://api-my.te.eg"
login_url = f"{base_url}/api/user/login"
freeunitusage_url = f"{base_url}/api/line/freeunitusage"

# Define the headers
token_headers = {
    "Host": "api-my.te.eg",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Jwt": "eyJraWQiOiIxIiwiYWxnIjoiUlMyNTYifQ.eyJpc3MiOiJ0ZS5jb20iLCJleHAiOjI2NjEwOTE3MTQsImp0aSI6Ik5ibUFWd3NHQzZKUjVGamcyeHZzWXciLCJpYXQiOjE3MTUwMTE3MTQsIm5iZiI6MTcxNTAxMTU5NCwic3ViIjoiQW5vbnltb3VzIiwicm9sZXMiOlsiUk9MRV9BTk9OWU1PVVMiXSwiSVAiOiIxNTYuMTkyLjIzOS42MywgMTAuMTYuMTQ2LjU2LCAxMC4xOS4yNDcuMjQwIiwiY2hhbm5lbElkIjoiV0VCX0FQUCJ9.ONM_vFHVcxn07AvmreT8IBxrudzrMfj7tjhy3I2s7NBOhVLWJ6sBgNKThWZZynRqm_j0d4z-XRJzShbPzvzV5m7BTKIuRueeY7lRdgyaka5C3mxtWyWLWwwdBj7bl5_1ryJeXFbFYWU0_J7vAy_pIg21KxQ1LeedvzTB18haHBgx-nxBdudqvzxP81DIf-VXyQ4SGxbPUeyVeOhMG9XWSdoo3DLrmxZOEnMW-XOiCHJdJa4Y9ZsvmszPrY8DyamNU9mN-IN_mspuei6Q-_4kFWBG-NTFL_1_K2rSABEJHOdjwaL12IQnHKMN_lcJECzXI3HPLrTEb_ZabiVB862aYw",
    "Content-Type": "application/json",
    "Content-Length": "105",
    "Origin": "https://my.te.eg",
    "Connection": "keep-alive",
    "Referer": "https://my.te.eg/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site"
}
token_payload = {
    "header": {
        "msisdn": "034341409",
        "numberServiceType": "FBB",
        "timestamp": str(int(time.time())),
        "locale": "en"
    },
    "body": {
        "password": "MlRP8zekObQDPvpsV32VtA=="
    }
}

def get_jwt():
    jwt_token = None
    token_response = requests.post(login_url, headers=token_headers, json=token_payload)
    if token_response.status_code == 200:
        token_body = token_response.json()["body"]
        jwt_token =  token_body["jwt"]
    return jwt_token

freeunitusage_payload = {
    "header": {
        "msisdn": "034341409",
        "numberServiceType": "FBB",
        "locale": "en"
    }
}

freeunitusage_headers = {
    "Host": "api-my.te.eg",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/json",
    "Content-Length": "105",
    "Origin": "https://my.te.eg",
    "Connection": "keep-alive",
    "Referer": "https://my.te.eg/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site"
}

def get_user_data(jwt):
    freeunitusage_headers["Jwt"] = jwt
    freeunitusage_response = requests.post(freeunitusage_url, headers=freeunitusage_headers, json=freeunitusage_payload)
    if freeunitusage_response.json()["body"] is None:
        return 
    return freeunitusage_response.json()["body"]["detailedLineUsageList"][0]["freeAmount"]

if __name__ == "__main__":
    print(get_user_data(get_jwt()))