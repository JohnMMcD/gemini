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
SUPPORTED_SYMBOLS_REGEX =  "btcusd|ethbtc|ethusd|zecusd|zecbtc|zeceth|zecbch"
SUPPORTED_SYMBOLS_REGEX += "|zecltc|bchusd|bchbtc|bcheth|ltcusd|ltcbtc|ltceth"
SUPPORTED_SYMBOLS_REGEX += "|ltcbch|batusd|daiusd|linkusd|oxtusd|batbtc"
SUPPORTED_SYMBOLS_REGEX += "|linkbtc|oxtbtc|bateth|linketh|oxteth"
SIDE_REGEX = "buy|sell"

# Read the key and secret from files so you don't upload them to github
API_KEY = open("key.txt", "r").read()
API_SECRET = open("secret.txt", "r").read().encode()

class NSFError(Exception):
    pass


def transact_payload_WIP(order_payload, order_options):
    """ This is work in progress

    This is a lower-level way of generating orders, which can be used for positive or negative test cases.
    Keyword arguments:
    order_payload - a dictionary containing the payload to send to the
      API, probably excluding the nonce and request keys.
    options - a list of options from https://docs.gemini.com/rest-api/#order-execution-options

    """
    print("Payload:")
    print(order_payload)

    encoded_payload = json.dumps(order_payload).encode()
    b64 = base64.b64encode(encoded_payload)
    signature = hmac.new(API_SECRET, b64, hashlib.sha384).hexdigest()

    request_headers = { 'Content-Type': "text/plain",
                        'Content-Length': "0",
                        'X-GEMINI-APIKEY': API_KEY,
                        'X-GEMINI-PAYLOAD': b64,
                        'X-GEMINI-SIGNATURE': signature,
                        'Cache-Control': "no-cache" }
    print("Request headers:")
    print(request_headers)
    # Had to put a sleep in here so the nonces would change
    time.sleep(2.0)
    response = requests.post(URL,
                            data=None,
                            headers=request_headers)

    new_order_response = response.json()
    print("Response:")
    print(new_order_response)
    return(new_order_response)


def transact(amount, symbol, price, side, otype, options, stop_price=0.0):
    """ Execute an order with the amount/symbol etc. specified

    Keyword arguments:
    amount - the quantity of items to buy or sell
    symbol - the crypto's symbol (e.g., BTCUSD). Will be converted to lower case
    price - the requested transaction price
    side - whether to buy or sell
    type - "exchange limit" or "exchange stop limit"
    options - a list of options from https://docs.gemini.com/rest-api/#order-execution-options

    """

    t = datetime.datetime.now()
    # Things I didn't read before I started tweaking:
    # > The nonce associated with a request needs to be increasing with 
    # > respect to the session that the nonce is used on.
    # So I used random numbers as nonces, and these numbers got
    # to be fairly large. In order to have subsequent nonces be
    # increasing, I have to add the largest previous value to
    # the time-based one. I'm glad Python int is not limited.
    payload_nonce =  str(99999999999999999 + int(time.mktime(t.timetuple())*1000))
    payload = {
       "request": ENDPOINT,
        "nonce": payload_nonce,
        "symbol": symbol.lower(),
        "amount": amount,
        "price": price,
        "side": side.lower(),
        "type": otype,
        "options": options
    }
    print("Payload:")
    print(payload)

    encoded_payload = json.dumps(payload).encode()
    b64 = base64.b64encode(encoded_payload)
    signature = hmac.new(API_SECRET, b64, hashlib.sha384).hexdigest()

    request_headers = { 'Content-Type': "text/plain",
                        'Content-Length': "0",
                        'X-GEMINI-APIKEY': API_KEY,
                        'X-GEMINI-PAYLOAD': b64,
                        'X-GEMINI-SIGNATURE': signature,
                        'Cache-Control': "no-cache" }
    print("Request headers:")
    print(request_headers)
    # Had to put a sleep in here so the nonces would change
    time.sleep(2.0)
    response = requests.post(URL,
                            data=None,
                            headers=request_headers)

    new_order_response = response.json()
    print("Response:")
    print(new_order_response)
    return(new_order_response)
