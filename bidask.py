import requests
import json
import base64
import hmac
import hashlib
import datetime, time

# Constant-ish attributes
BASE_URL = "https://api.sandbox.gemini.com"
MOCKISH_BASE_URL = "http://users.bestweb.net/~mcdonnel"

"""
MOCKISH_BASE_URL requires explanation. The solution said, 
"Do not invoke any other API endpoints (e.g., order status)". However, there are
a lot of scenarios where it's difficult to create realistic test orders without
access to data from these endpoints. E.g., if you don't know the bid
and ask from pubticker/MYSYMBOL, you won't know whether a fill-or-kill order
should be filled. So I hit a few of the public "do not invoke" APIs and saved
a few* of the outputs to a site I control, http://users.bestweb.net/~mcdonnel
and make requests to that instead of the public API. It's not perfect, because
the sandbox is dynamic, but it's better than hardcoding the bid/ask values everywhere. 

Another idea would be to use a mock. Yet another idea would be to use
text files and store the values in that, but the code which parses those
files is ugly. I implemented this for a few methods, and left the code below, but
commented it out. The data / text files are in the repository.

* currently, only btcusd, ethusd, and ethbtc are supported.
"""

ENDPOINT = "/v1/order/new"
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
