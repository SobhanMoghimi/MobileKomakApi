import requests
from datetime import datetime as dt
import time
import hashlib
import hmac
import uuid
import json


api_key = 'c8opp8Ian7V4qEFC9E'
secret_key = 'qBcXgBcr9GxGgX5yuJKwVtMBgw0YYePx9uB5'
recv_window = "5000"
url = "https://api.bybit.com"


class BybitApi:
    httpClient = requests.Session()

    def __int__(self):
        self.httpClient = requests.Session()

    def http_request(self, end_point, method, params, info):
        global time_stamp
        time_stamp = str(int(time.time() * 10 ** 3))
        signature = gen_signature(params)
        headers = {
            'X-BAPI-API-KEY': api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': time_stamp,
            'X-BAPI-RECV-WINDOW': recv_window,
            'Content-Type': 'application/json'
        }
        if method == "POST":
            response = self.httpClient.request(method, url + end_point, headers=headers, data=params)
        else:
            response = self.httpClient.request(method, url + end_point + "?" + params, headers=headers)

        print(info + " Elapsed Time : " + str(response.elapsed))
        return response

    def get_wallet_balance(self):
        endpoint = "/contract/v3/private/account/wallet/balance"
        method = "GET"
        params = 'coin=USDT'
        response = self.http_request(endpoint, method, params, "Ballance")
        return response.json()

    def create_order(self, symbol, side:str,
                     order_price, stop_loss,
                     take_profit, qty):
        timeInForce = 'GoodTillCancel'
        triggerBy = 'IndexPrice'
        order_type = 'Limit'

        endpoint = "/contract/v3/private/order/create"
        method = "POST"
        if side.lower() == 'short':
            side = "Sell"
        elif side.lower() == 'long':
            side = "Buy"

        orderLinkId = uuid.uuid4().hex

        params = {"symbol": symbol,
                  "side": side,
                  "orderType": order_type,
                  "qty": qty,
                  "timeInForce": timeInForce
                  }
        response = self.http_request(endpoint, method, params, "Create")

        return response

def gen_signature(payload):
    param_str = str(time_stamp) + api_key + recv_window + payload
    hash = hmac.new(bytes(secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
    signature = hash.hexdigest()
    return signature

