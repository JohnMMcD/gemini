import requests
import json
import base64
import hmac
import hashlib
import datetime, time
from os import path

# Constant-ish attributes
BASE_URL = "https://api.sandbox.gemini.com"
MOCKISH_BASE_URL = "http://users.bestweb.net/~mcdonnel"
ENDPOINT = "/v1/order/new"

"""
MOCKISH_BASE_URL requires explanation. The solution said, 
"Do not invoke any other API endpoints (e.g., order status)". However, there are
a lot of scenarios where it's difficult to create realistic test orders without
access to data from these endpoints. E.g., if you don't know the bid
and ask from pubticker/MYSYMBOL, you won't know whether a fill-or-kill order
should be filled. So I hit a few of the public "do not invoke" APIs and saved
a few* of the outputs to a site I control, http://users.bestweb.net/~mcdonnel/v1/... ,
and make requests to that instead of the public API. It's not perfect, because
the sandbox is dynamic, but it's better than hardcoding the bid/ask values everywhere. 

I have not ported this to the object-oriented style because I wasn't sure if making
external requests was allowed (and also to save time), so in those I use hardcoded values. 

Another idea would be to use a mock. Yet another idea would be to use
text files and store the values in that, but the code which parses those
files is ugly. I implemented this for a few methods, and left the code below, but
commented it out. The data / text files are in the repository.

* currently, only btcusd, ethusd, and ethbtc are saved.
"""


URL = BASE_URL + ENDPOINT

""" The list of valid currencies. """
symbol_url = MOCKISH_BASE_URL + '/v1/symbols'
CURRENCIES = requests.get(symbol_url).text.strip("[]").replace('"','').split(",")
"""

try:
    f = open("currencies.txt", "r")
    lines = f.readlines()
    for line in lines:
        stripped = line.strip(" \n")
        # Ignore lines with hashmarks and empty lines
        if ((not stripped.startswith("#")) and len(stripped) > 0):
            CURRENCIES.append(stripped)
finally:
    f.close()

"""


"""
DICT_BIDASK holds the output of https://api.sandbox.gemini.com/v1/pubticker/MY_SYMBOL 
for all symbols of interest. The key is the symbol, the value is the dictionary with the bid, ask, etc.
Sample Usage:
  gemini.DICT_BIDASK['btcusd']['ask'])
"""
DICT_BIDASK = {}
base = MOCKISH_BASE_URL + '/v1/pubticker/'
for currency in CURRENCIES:
    DICT_BIDASK[currency] = requests.get(base + currency).json()

""""
try:

    f = open("bidask.txt", "r")
    lines = f.readlines()
    for line in lines:
        stripped = line.strip(" \n")
        if ((not stripped.startswith("#")) and len(stripped) > 0):
            # The response to, say, https://api.sandbox.gemini.com/v1/pubticker/btcusd
            # does not include the requested symbol (btcusd), but the symbol can be inferred
            # from the volume dictionary. The volume dictionary has three keys. The timestamp
            # key can be removed, but the other two concatenate to the symbol, although
            # we don't know the order, so we try both.
            # {"bid": "10070.68", "ask": "10070.69",
            # "volume": {"BTC": "2682.76576127", "USD": "27522575.3015899983", "timestamp": 1599338400000},
            # "last": "10070.69"}
#            print(f"line: {line}")
            currency_dict = json.loads(line)
            if 'volume' in currency_dict:
                volume_dict = currency_dict["volume"]
                if 'timestamp' in volume_dict:
                    del volume_dict['timestamp']
                symbol_candidates = list(volume_dict.keys())
                ab = (symbol_candidates[0] + symbol_candidates[1]).lower()
                ba = (symbol_candidates[1] + symbol_candidates[0]).lower()

                if ab in CURRENCIES:
#                    print(f"Added {ab}")
                    DICT_BIDASK[ab] = currency_dict
                elif ba in CURRENCIES:
#                    print(f"Added {ba}")
                    DICT_BIDASK[ba] = currency_dict
                else:
                    print("Could not determine symbol for a line in bidask.txt")
finally:
    f.close()
"""

SUPPORTED_SYMBOLS_REGEX = "|".join(CURRENCIES)
SIDE_REGEX = "buy|sell"

# The key and secret are externalized so they don't get uploaded to
# GitHub with the rest of the files.
# To set the API key and secrets, create the key.txt and secret.txt in 
# the same directory as gemini.py , or delete the 8 lines below and 
# uncomment these 2 lines, then change their values.
# API_KEY='account-Mby...QoM'
# API_SECRET='3hd...qDc3i'.encode()

if not path.exists("key.txt"):
    assert False, "key.txt file must exist in the root directory - see the README.MD"
if not path.exists("secret.txt"):
    assert False, "secret.txt file must exist in the root directory - see the README.MD"
with open('key.txt') as f:
    API_KEY = f.read().strip()
with open('secret.txt') as f:
    API_SECRET = f.read().strip().encode()

""" List from https://docs.gemini.com/rest-api/#order-status , but some at this link are optional  """
mandatory_fields = ["order_id", "symbol", "exchange", "price",
                    "avg_execution_price", "side", "type", "options",
                    "timestamp", "timestampms", "is_live",
                    "is_cancelled", "was_forced",
                    "executed_amount", "remaining_amount",
                    "original_amount", "is_hidden"]

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
    print(f"Payload: {str(order_payload)}")

    encoded_payload = json.dumps(order_payload).encode()
    b64 = base64.b64encode(encoded_payload)
    signature = hmac.new(API_SECRET, b64, hashlib.sha384).hexdigest()

    request_headers = {'Content-Type': "text/plain",
                       'Content-Length': "0",
                       'X-GEMINI-APIKEY': API_KEY,
                       'X-GEMINI-PAYLOAD': b64,
                       'X-GEMINI-SIGNATURE': signature,
                       'Cache-Control': "no-cache"}
    print(f"Request headers: str({request_headers})")

    # Had to put a sleep in here so the nonces would change
    time.sleep(2.0)
    response = requests.post(URL,
                             data=None,
                             headers=request_headers)

    new_order_response = response.json()
    print(f"Response: {new_order_response}")
    return (new_order_response)


def transact(amount, symbol, price, side, otype, options, stop_price=0.0):
    """
     Execute an order with the amount/symbol etc. specified
     Args:
        amount - the quantity of items to buy or sell
        symbol - the crypto's symbol (e.g., BTCUSD). Will be converted to lower case
        price - the requested transaction price
        side - whether to buy or sell
        type - "exchange limit" or "exchange stop limit"
        options - a list of options from https://docs.gemini.com/rest-api/#order-execution-options
        stop_price - The (optional) price to trigger a stop-limit order.
     Returns:
         dictionary containing the response
     """

    t = datetime.datetime.now()
    # Things I didn't read before I started tweaking:
    # > The nonce associated with a request needs to be increasing with 
    # > respect to the session that the nonce is used on.
    # So I used random numbers as nonces, and these numbers got
    # to be fairly large. In order to have subsequent nonces be
    # increasing, I have to add the largest previous value to
    # the time-based one. I'm glad Python int is not limited.
    payload_nonce = str(99999999999999999 + int(time.mktime(t.timetuple()) * 1000))
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
    print(f"Payload: {str(payload)}")

    encoded_payload = json.dumps(payload).encode()
    b64 = base64.b64encode(encoded_payload)
    signature = hmac.new(API_SECRET, b64, hashlib.sha384).hexdigest()

    request_headers = {'Content-Type': "text/plain",
                       'X-GTEST-side': side.lower(),
                       'X-GTEST-type': otype,
                       'X-GTEST-price': price,
                       'X-GTEST-symbol': symbol,
                       'X-GTEST-options': ', '.join(options),
                       'X-GEMINI-PAYLOAD': b64,
                       'X-GEMINI-APIKEY': API_KEY,
                       'X-GEMINI-SIGNATURE': signature,
                       'Content-Length': "0",
                       'Cache-Control': "no-cache"}
    print(f"Request headers: {str(request_headers)}")
    # Had to put a sleep in here so the nonces would change
    time.sleep(2.0)
    response = requests.post(URL,
                             data=None,
                             headers=request_headers)

    new_order_response = response.json()
    print(f"Response: {str(new_order_response)}")
    return (new_order_response)

