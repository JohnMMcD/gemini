import requests
import json
import base64
import hmac
import hashlib
import datetime, time
import unittest


class TestHTTPErrorCode(unittest.TestCase):
    """
    This class tests the HTTP Error Code at https://docs.gemini.com/rest-api/#http-error-codes
    There are a lot of them, and many of them are out of scope, but I'll implement as many as I can.
    Many of these methods don't use the objects because the objects were designed for valid requests, and
    many of these methods were designed to create invalid requests.
    """

    amount = "0.01"
    symbol = "btcusd"
    buy_price = "16000"
    buy_stop_price = "15999"
    sell_price = "10001"
    sell_stop_price = "10002"
    # An amount that is impossible to fill in one order
    amount_way_too_high = "9999999999"
    VALID_BASE_URL = "https://api.sandbox.gemini.com"
    ENDPOINT = "/v1/order/new"

    def testHTTP30x(self):
        """ Executes an order using HTTP, not HTTPS. Might show a bug because the
        doc says HTTP 30x codes mean:

        API entry point has moved, see Location: header. Most likely an http: to https: redirect.

        and this gives a 404 header, not a 30x header. Maybe a sand-box only issue (I didn't try the production site).
        This testcase copy-and-pastes from other methods to an unfortunate degree.
        """
        http_base_url = "http://api.sandbox.gemini.com"
        url = http_base_url + self.ENDPOINT
        with open('key.txt') as f:
            API_KEY = f.read()
        with open('secret.txt') as f:
            API_SECRET = f.read().encode()

        t = datetime.datetime.now()
        payload_nonce = str(99999999999999999 + int(time.mktime(t.timetuple()) * 1000))
        payload = {
            "request": self.ENDPOINT,
            "nonce": payload_nonce,
            "symbol": self.symbol,
            "amount": self.amount,
            "price": self.buy_price,
            "side": 'buy',
            "type": 'exchange limit',
            "options": ['fill-or-kill']
        }

        encoded_payload = json.dumps(payload).encode()
        b64 = base64.b64encode(encoded_payload)
        signature = hmac.new(API_SECRET, b64, hashlib.sha384).hexdigest()

        # Add some extra request headers for debugging
        request_headers = {'Content-Type': "text/plain",
                           'X-GTEST-side': 'buy',
                           'X-GTEST-type': 'exchange limit',
                           'X-GTEST-price': self.buy_price,
                           'X-GTEST-symbol': self.symbol,
                           'X-GTEST-amount': self.amount,
                           'X-GTEST-options': "['fill-or-kill']",
                           'X-GEMINI-PAYLOAD': b64,
                           'X-GEMINI-APIKEY': API_KEY,
                           'X-GEMINI-SIGNATURE': signature,
                           'Content-Length': "0",
                           'Cache-Control': "no-cache"}
        print(f"Sending request to HTTP URL {url}")
        # Had to put a sleep in here so the nonces would change
        time.sleep(2.0)
        response = requests.post(url,
                                 data=None,
                                 headers=request_headers)
        print(f"Response code should be 301 or 302 but is {response.status_code}.")
        new_order_response = response.json()
        assert new_order_response['reason'] == 'EndpointNotFound', "Incorrect error message"

    def testHTTP400MalformedAuthenticationHeaders(self):
        """ Malformed requests should cause HTTP 400 errors:
        'in the case of a private API request, missing or malformed Gemini private API authentication headers'
        """

        url = self.VALID_BASE_URL + self.ENDPOINT
        with open('key.txt') as f:
            API_KEY = f.read()
        # Not doing secret because this about malformed authentication headers

        t = datetime.datetime.now()
        payload_nonce = str(99999999999999999 + int(time.mktime(t.timetuple()) * 1000))
        payload = {
            "request": self.ENDPOINT,
            "nonce": payload_nonce,
            "symbol": self.symbol,
            "amount": self.amount,
            "price": self.buy_price,
            "side": 'buy',
            "type": 'exchange limit',
            "options": ['fill-or-kill']
        }

        encoded_payload = json.dumps(payload).encode()
        b64 = base64.b64encode(encoded_payload)

        # Add some extra request headers for debugging
        request_headers = {'Content-Type': "text/plain",
                           'X-GTEST-side': 'buy',
                           'X-GTEST-type': 'exchange limit',
                           'X-GTEST-price': self.buy_price,
                           'X-GTEST-symbol': self.symbol,
                           'X-GTEST-amount': self.amount,
                           'X-GTEST-options': "['fill-or-kill']",
                           'X-GEMINI-PAYLOAD': b64,
                           'X-GEMINI-APIKEY': API_KEY,
                           'X-GEMINI-SIGNATURE': "jmcdonne_was_here",
                           'Content-Length': "0",
                           'Cache-Control': "no-cache"}
        print(f"Sending request to HTTP URL {url}")
        # Had to put a sleep in here so the nonces would change
        time.sleep(2.0)
        response = requests.post(url,
                                 data=None,
                                 headers=request_headers)

        assert response.status_code == 400, \
            f"Response code should be 400 but is {response.status_code}."

    def testHTTP400MissingAPISignature(self):
        """ 'in the case of a private API request, missing or malformed Gemini private API authentication headers' """

        URL = self.VALID_BASE_URL + self.ENDPOINT
        with open('key.txt') as f:
            API_KEY = f.read()
        # secret is missing by design

        t = datetime.datetime.now()
        payload_nonce = str(99999999999999999 + int(time.mktime(t.timetuple()) * 1000))
        payload = {
            "request": self.ENDPOINT,
            "nonce": payload_nonce,
            "symbol": self.symbol,
            "amount": self.amount,
            "price": self.buy_price,
            "side": 'buy',
            "type": 'exchange limit',
            "options": ['fill-or-kill']
        }

        encoded_payload = json.dumps(payload).encode()
        b64 = base64.b64encode(encoded_payload)

        # Add some extra request headers for debugging
        request_headers = {'Content-Type': "text/plain",
                           'X-GTEST-side': 'buy',
                           'X-GTEST-type': 'exchange limit',
                           'X-GTEST-price': self.buy_price,
                           'X-GTEST-symbol': self.symbol,
                           'X-GTEST-amount': self.amount,
                           'X-GTEST-options': "['fill-or-kill']",
                           'X-GEMINI-PAYLOAD': b64,
                           'X-GEMINI-APIKEY': API_KEY, # signature removed
                           'Content-Length': "0",
                           'Cache-Control': "no-cache"}
        # Had to put a sleep in here so the nonces would change
        time.sleep(2.0)
        response = requests.post(URL,
                                 data=None,
                                 headers=request_headers)

        assert response.status_code == 400, \
            f"Response code should be 400 but is {response.status_code}."

    @unittest.skip("because you only have one API key.")
    def testHTTP403MissingRole(self):
        """Verify that missing roles throw HTTP 403 error."""
        pass

    @unittest.skip("because only one entry point is allowed and order status isn't it.")
    def testHTTP404UnknownEntryPointOrOrderNotFound(self):
        """Verify that unknown entry points throw HTTP 404 error."""
        bad_endpoint = "/v1/order/foo"
        # ...
        pass

    @unittest.skip("because there doesn't seem to be a way of triggering this.")
    def testHTTP406InsufficientFunds(self):
        """Verify that 'insufficient funds' gives a 406 error"""
        pass

    def testHTTP429RateLimiting(self):
        """Verify that rate limiting happens and gives a useful error. Does not seem to be kicking in.

        Per https://docs.gemini.com/rest-api/#rate-limits :
        If you send 20 requests in close succession over two seconds, then you could expect:

        * the first ten requests are processed
        * the next five requests are queued
        * the next five requests receive a 429 response, meaning the rate limit for this group
        of endpoints has been exceeded
        * any further incoming request immediately receive a 429 response
        * after a short period of inactivity, the five queued requests are processed
        * following that, incoming requests begin to be processed at the normal rate again

        But I'm sending up to 40 requests as fast as possible and not getting
        a 429 error, though I cut it short.
        """
        url = self.VALID_BASE_URL + self.ENDPOINT
        with open('key.txt') as f:
            API_KEY = f.read()
        with open('secret.txt') as f:
            API_SECRET = f.read().encode()
        nonce_offset = 99999999999999000

        for i in range(40):

            t = datetime.datetime.now()
            nonce_offset = nonce_offset + 1
            payload_nonce = str(nonce_offset + int(time.mktime(t.timetuple()) * 1000))
            payload = {
                "request": self.ENDPOINT,
                "nonce": payload_nonce,
                "symbol": self.symbol,
                "amount": self.amount,
                "price": self.buy_price,
                "side": 'buy',
                "type": 'exchange limit',
                "options": ['fill-or-kill']
            }

            encoded_payload = json.dumps(payload).encode()
            b64 = base64.b64encode(encoded_payload)
            signature = hmac.new(API_SECRET, b64, hashlib.sha384).hexdigest()

            # Add some extra request headers for debugging
            request_headers = {'Content-Type': "text/plain",
                               'X-GTEST-side': 'buy',
                               'X-GTEST-type': 'exchange limit',
                               'X-GTEST-price': self.buy_price,
                               'X-GTEST-symbol': self.symbol,
                               'X-GTEST-amount': self.amount,
                               'X-GTEST-options': "['fill-or-kill']",
                               'X-GEMINI-PAYLOAD': b64,
                               'X-GEMINI-APIKEY': API_KEY,
                               'X-GEMINI-SIGNATURE': signature,
                               'Content-Length': "0",
                               'Cache-Control': "no-cache"}
            print(f"Sending request {i} to {url} at {datetime.datetime.now()}")
            response = requests.post(url,
                                     data=None,
                                     headers=request_headers)
            print(f"Response code {i} is: {response.status_code} at {datetime.datetime.now()}")
            # print(response.text)
            if i > 30:
                assert response.status_code == 429, f"Status should be 429 but is {response.status_code} "
        print("Sleep 30 seconds to cool off after triggering the rate limiting")
        time.sleep(30)

    @unittest.skip("because there doesn't seem to be a way of triggering this.")
    def testHTTP500UnknownError(self):
        """Verify that 'an unknown error' gives a 500 error"""
        pass

    @unittest.skip("because there doesn't seem to be a way of triggering this.")
    def testHTTP502TechnicalDifficulties(self):
        """Verify that 'technical difficulties' gives a 502 error"""
        pass

    @unittest.skip("because there doesn't seem to be a way of triggering this.")
    def testHTTP503ExchangeDown(self):
        """Verify that 'exchange down' gives a 503 error"""
        pass

    @classmethod
    def setUpClass(cls):
        print("Start me up! Testing HTTP Error Codes.")

    @classmethod
    def tearDownClass(cls):
        print("Fini! Close your session, take a deep breath, and relax.")


if __name__ == '__main__':
    unittest.main()
