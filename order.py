import requests
import json
import base64
import hmac
import hashlib
import datetime, time

class Order:
    # Constant-ish attributes
    BASE_URL = "https://api.sandbox.gemini.com"
    MOCKISH_BASE_URL = "http://users.bestweb.net/~mcdonnel"
    ENDPOINT = "/v1/order/new"
    URL = BASE_URL + ENDPOINT
    API_KEY = open("key.txt", "r").read()
    API_SECRET = open("secret.txt", "r").read().encode()

    # Class variables which don't change
    request = "/v1/order/new"

    def __init__(self, side, amount, symbol, price, order_type, options, min_amount='', stop_price='',
                 client_order_id=''):
        """ Parameters from https://docs.gemini.com/rest-api/#new-order , but not in order here """
        self.side = side.lower()
        self.amount = amount
        self.symbol = symbol.lower()
        self.price = price
        self.order_type = order_type.lower()
        self.options = options
        self.min_amount = min_amount
        self.stop_price = stop_price
        self.client_order_id = client_order_id
        self.payload = {} # gets populated when executed

    def execute_payload(self, payload):
        """ Executes the order with the given payload. This is at a lower level compared to
         the 'execute' method and can be called directly when non-standard or
         non-compliant payloads are required.

        Args:
            payload: dictionary to send

        Returns:
            A dictionary containing the response.
        """
        self.payload = payload
        encoded_payload = json.dumps(payload).encode()
        b64 = base64.b64encode(encoded_payload)
        signature = hmac.new(self.API_SECRET, b64, hashlib.sha384).hexdigest()

        # Add some extra request headers for debugging
        request_headers = {'Content-Type': "text/plain",
                           'X-GTEST-side': self.side,
                           'X-GTEST-type': self.order_type,
                           'X-GTEST-price': self.price,
                           'X-GTEST-symbol': self.symbol,
                           'X-GTEST-amount': self.amount,
                           'X-GTEST-options': ', '.join(self.options),
                           'X-GEMINI-PAYLOAD': b64,
                           'X-GEMINI-APIKEY': self.API_KEY,
                           'X-GEMINI-SIGNATURE': signature,
                           'Content-Length': "0",
                           'Cache-Control': "no-cache"}
        #print(f"Request headers: {str(request_headers)}")
        # Had to put a sleep in here so the nonces would change
        time.sleep(2.0)
        response = requests.post(self.URL,
                                 data=None,
                                 headers=request_headers)

        new_order_response = response.json()
        #print(f"Response: {str(new_order_response)}")
        return (new_order_response)

    def execute(self):
        """ Executes an order with the current object.

         Returns:
             A dictionary containing the response.
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
            "request": self.ENDPOINT,
            "nonce": payload_nonce,
            "symbol": self.symbol,
            "amount": self.amount,
            "price": self.price,
            "side": self.side,
            "type": self.order_type,
            "options": self.options
        }
#        print(f"Payload: {str(payload)}")
        return self.execute_payload(payload)


class ExchangeLimitOrder(Order):
    def __init__(self, side, amount, symbol, price, options):
        Order.__init__(self, side, amount, symbol, price, "exchange limit", options)


class MakerOrCancelOrder(ExchangeLimitOrder):
    def __init__(self, side, amount, symbol, price):
        ExchangeLimitOrder.__init__(self, side, amount, symbol, price, ['maker-or-cancel'])


class ImmediateOrCancelOrder(ExchangeLimitOrder):
    def __init__(self, side, amount, symbol, price):
        ExchangeLimitOrder.__init__(self, side, amount, symbol, price, ['immediate-or-cancel'])


class FillOrKillOrder(ExchangeLimitOrder):
    def __init__(self, side, amount, symbol, price):
        ExchangeLimitOrder.__init__(self, side, amount, symbol, price, ['fill-or-kill'])


class AuctionOnlyOrder(ExchangeLimitOrder):
    def __init__(self, side, amount, symbol, price):
        ExchangeLimitOrder.__init__(self, side, amount, symbol, price, ['auction-only'])


class IndicationOfInterestOrder(ExchangeLimitOrder):
    def __init__(self, side, amount, symbol, price):
        ExchangeLimitOrder.__init__(self, side, amount, symbol, price, ['indication-of-interest'])

