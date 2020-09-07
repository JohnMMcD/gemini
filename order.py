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

    """ Parameters from https://docs.gemini.com/rest-api/#new-order , but not in order here """
    side = ""
    amount = ""
    symbol = ""
    price = ""
    order_type = ""  # use order_prefix to avoid confusion with built-in
    options = []
    request = "/v1/order/new"
    nonce = 0
    client_order_id = ""
    min_amount = ""
    stop_price = ""
    # not bothering with account since that is only for master API keys
    API_KEY = open("key.txt", "r").read()
    API_SECRET = open("secret.txt", "r").read().encode()

    def __init__(self, side, amount, symbol, price, order_type, options, min_amount='', stop_price='',
                 client_order_id=''):
        self.side = side.lower()
        self.amount = amount
        self.symbol = symbol.lower()
        self.price = price
        self.order_type = order_type.lower()
        self.options = options
        self.min_amount = min_amount
        self.stop_price = stop_price
        self.client_order_id = client_order_id

    def execute_payload(self, payload):
        """ Executes the order with the given payload. This is at a lower level compared to
         the 'execute' method and can be called directly when non-standard or
         non-compliant payloads are required.

        Args:
            payload: dictionary to send

        Returns:
            A dictionary containing the response.
        """
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


class Response():
    """
    Parent class for responses. Note that error responses have very different formats than other responses.
    """
    raw = {}
    def __init__(self, dict_response):
        self.raw = dict_response

"""
    
    result = ""
    reason = ""
    message = ""
    order_id = ""
    client_order_id = ""
    id = ""
    symbol = ""
    exchange = "gemini"
    avg_execution_price = ""
    side = ""
    order_type = ""
    timestamp = ""
    timestampms = ""
    is_live = ""
    is_cancelled = ""
    is_hidden = ""
    was_forced = ""
    executed_amount = ""
    options = []
    price = ""
    original_amount = ""
    remaining_amount = ""
"""

class ErrorResponse(Response):
    def __init__(self, dict_response):
        Response.__init__(self, dict_response)

    mandatory_error_fields = ["result", "reason", "message"]

    def verify(self, reason):
        """
        Verifies the response was an error, and the reason matched.
        Args:
            reason: the text of the reason. This is not the 'message'!
        Returns:
            True if everything went OK, throws assertion otherwise
        """
#        print(f"verifying error was due to {reason}")
        for key in self.mandatory_error_fields:
            assert key in self.raw, f"Missing {key} key in response"
        assert self.raw["result"] == "error", f"Result mismatch! Expected error, was {self.raw['result']}"
        assert self.raw["reason"] == reason, f"Reason mismatch! Expected {reason}, was {self.raw['reason']}"
        # Errors shouldn't have the is_cancelled element. If this element exists, then we want to know the reason.
        assert "is_cancelled" not in self.raw, f"Unexpected cancellation because of {self.raw['reason']}"
        return True


class CancelledInFullResponse(Response):
    def __init__(self, dict):
        Response.__init__(self, dict)
    
    def verify(self, reason):
        """
        Verifies the response was cancelled and the reason matched. 
        Cancelled responses do not have any errors.
        TODO: Determine other tests.
        Args:
            reason: the reason for the cancellation
        Returns:
            True if everything went OK, throws assertion otherwise.
        """
        # The 'result' key is only present if there is an error, which shouldn't be the case
        # Also log the reason for the error, because it's good to know and the reason is always given,
        # unless there's a KeyError.
        assert "result" not in self.raw, \
            f"Unexpected result in response: {self.raw['result']} with reason {self.raw['reason']}"
        # is_cancelled should be True.
        assert self.raw["is_cancelled"], f"Response should have been cancelled but was not"
        assert self.raw["reason"] == reason, f"Reason mismatch: expected {reason}, got {self.raw['reason']}"

        # executed_amount must be zero, or a very small value (never test floats for equality).
        f_expected = float(self.raw['executed_amount'])
        assert f_expected < 0.001 and f_expected > -0.001, f"Non-zero executed_amount: {self.raw['executed_amount']}"
        # Checking the literal '0' string in addition to the floating point inequality
        assert self.raw['executed_amount'] == '0', f"Non-zero executed_amount: {self.raw['executed_amount']}"

        return True


class ExecutedInFullResponse(Response):
    def __init__(self, dict):
        Response.__init__(self, dict)

    def verify(self, response, amount, currency, price, side, order_type, options):
        """
        Verifies the response did not have any errors, was not cancelled, and
        had a positive execution amount. Other test may be added.
        Args:
            response: the dictionary containing the response to be checked
            amount: the quantity that should have been executed
            currency: the currency symbol
            price: the price. Might need to tweak this because best effort means
            that buys might be at a lower price than requested
            order_type: type of order
            side: buy or sell
            options:

        Returns:
            True if everything went OK, throws assertion otherwise
        """
        # The 'result' key is only present if there is an error.
        assert "result" not in  response, "Unexpected result in response: self.raw['result']}"
        # is_cancelled should be false.
        assert not self.raw["is_cancelled"], f"Response was unexpectedly cancelled"
        # executed_amount must be positive
        assert float(self.raw['executed_amount']) > 0, f"Non-positive executed_amount: {self.raw['executed_amount']}"
        assert self.raw['executed_amount'] == amount, f"Amount mismatch! Expected {amount}, was {self.raw['executed_amount']}"
        assert self.raw['symbol'] == currency, f"Symbol mismatch! Expected {currency}, was {self.raw['symbol']}"
        f_price = float(self.raw['price'])
        assert abs(f_price - float(price)) < 0.001,  f"Executed prices differ: Expected {str(price)}), was {str(f_price)}"
        assert self.raw['side'] ==  side, f"Side mismatch! Expected {side}, was {self.raw['side']}"
        f_executed = float(self.raw['executed_amount'])
        assert abs(f_executed - float(amount)) < 0.001, f"Executed amounts differ: Expected {amount}, was {self.raw['executed_amount']}"
        assert self.raw['type'] == order_type, f"Type mismatch! Expected {order_type}, was {self.raw['type']}"
        assert self.raw['options'] == options, f"Options mismatch! Expected {options}, was {self.raw['options']}"

        return True

    def verify(self, order):
        """
        Verifies the response did not have any errors, was not cancelled, was executed in full, and
        matches the order submitted. Also some sanity checks for things like a positive execution
        amount. Other tests may be added.
        Args:
            order: the order to check against.
        Returns:
            True if everything went OK, throws assertion otherwise.
        """
        # The 'result' key is only present if there is an error.
        assert "result" not in  self.raw, "Unexpected result in response: self.raw['result']}"
        # is_cancelled should be false.
        assert not self.raw["is_cancelled"], f"Response was unexpectedly cancelled"
        # executed_amount must be positive
        assert float(self.raw['executed_amount']) > 0, \
            f"Non-positive executed_amount: {self.raw['executed_amount']}"
        assert self.raw['executed_amount'] == order.amount, \
            f"Amount mismatch! Expected {order.amount}, was {self.raw['executed_amount']}"
        assert self.raw['symbol'] == order.symbol, \
            f"Symbol mismatch! Expected {order.symbol}, was {self.raw['symbol']}"
        f_price = float(self.raw['price'])
        assert abs(f_price - float(order.price)) < 0.001,  \
            f"Executed prices differ: Expected {str(order.price)}), was {str(f_price)}"
        assert self.raw['side'] == order.side, f"Side mismatch! Expected {order.side}, was {self.raw['side']}"
        f_executed = float(self.raw['executed_amount'])
        assert abs(f_executed - float(order.amount)) < 0.001, \
            f"Executed amounts differ: Expected {order.amount}, was {self.raw['executed_amount']}"
        assert self.raw['type'] == order.order_type, \
            f"Type mismatch! Expected {order.order_type}, was {self.raw['type']}"
        assert self.raw['options'] == order.options, \
            f"Options mismatch! Expected {order.options}, was {self.raw['options']}"

        return True
