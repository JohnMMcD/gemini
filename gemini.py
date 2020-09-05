import requests
import json
import base64
import hmac
import hashlib
import datetime, time

# Constant-ish attributes
BASE_URL = "https://api.sandbox.gemini.com"
ENDPOINT = "/v1/order/new"
URL = BASE_URL + ENDPOINT

# from https://docs.gemini.com/rest-api/#all-supported-symbols
# btcusd ethbtc ethusd zecusd zecbtc zeceth zecbch 
# zecltc bchusd bchbtc bcheth ltcusd ltcbtc ltceth 
# ltcbch batusd daiusd linkusd oxtusd batbtc 
# linkbtc oxtbtc bateth linketh oxteth
SUPPORTED_SYMBOLS_REGEX =  "btcusd|ethbtc|ethusd|zecusd|zecbtc|zeceth|zecbch"
SUPPORTED_SYMBOLS_REGEX += "|zecltc|bchusd|bchbtc|bcheth|ltcusd|ltcbtc|ltceth"
SUPPORTED_SYMBOLS_REGEX += "|ltcbch|batusd|daiusd|linkusd|oxtusd|batbtc"
SUPPORTED_SYMBOLS_REGEX += "|linkbtc|oxtbtc|bateth|linketh|oxteth"

API_KEY = open("key.txt", "r").read()
API_SECRET = open("secret.txt", "r").read().encode()

class NSFError(Exception):
    pass

def buy(amount, symbol, price):
    t = datetime.datetime.now()
    payload_nonce =  str(int(time.mktime(t.timetuple())*1000))

    payload = {
       "request": ENDPOINT,
        "nonce": payload_nonce,
        "symbol": symbol,
        "amount": amount,
        "price": price,
        "side": "buy",
        "type": "exchange limit",
        "options": ["maker-or-cancel"] 
    }

    encoded_payload = json.dumps(payload).encode()
    b64 = base64.b64encode(encoded_payload)
    signature = hmac.new(API_SECRET, b64, hashlib.sha384).hexdigest()

    request_headers = { 'Content-Type': "text/plain",
                        'Content-Length': "0",
                        'X-GEMINI-APIKEY': API_KEY,
                        'X-GEMINI-PAYLOAD': b64,
                        'X-GEMINI-SIGNATURE': signature,
                        'Cache-Control': "no-cache" }

    response = requests.post(URL,
                            data=None,
                            headers=request_headers)

    new_order = response.json()
    print(new_order)
