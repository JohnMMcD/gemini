# Purpose
Testing the order_new API without involving any other API endpoints.

# Dependencies

These modules are used:
* behave
* unittest

As well as these modules, as used in the sample:
* requests
* json
* base64
* hmac
* hashlib
* datetime, time

Also, this retrieves data from a third-party web site; see MOCKISH_BASE_URL for details.

# Assumptions

* That the account has sufficient funds and the market has sufficient liquidity to execute transactions of arbitrary size, except for those negative testcases marked NSF.
* That since other API endpoints should not be invoked, including /v1/pubticker/SYMBOL, the order book is not visible, so no attempt will be made to use realistic prices. E.g., for an immediate-or-cancel order, I will use a very high price for buys if the expected outcome is a filled order, and a very low price if the expected outcome is a cancellation.
* That the [rate limits](https://docs.gemini.com/rest-api/#rate-limits) have been disabled, so I don't have to add time.sleep(1) before each request. However, I ended up adding in the sleep anyway so that the nonce (which was based on time) would increase.
* That these areas are out of scope:
 * anything related to high transaction volumes which could risk system stability (yes, I know one laptop won't stress the backend, but it seems impolite to appear to try). So whole classes of tests, such as memory leak, uptime, response time, stability, and anything else involving concurrent users, are out of scope.
  * session creation and validity. This is because the "If you wish orders to be automatically cancelled when your session ends, see the require heartbeat section, or manually send the cancel all session orders message" note combined with the "no other endpoints" restriction, makes session creation and validity difficult to test, so I'll assume a valid session exists and does not expire for the duration of the test.
 * security-related tests (SQL injection, probing nginx exploits, etc). 
 * anything specific to master API keys, exchange accounts, and basically anything account-privilege related. E.g., that the user's account has the Trader role, and that the OAuth scope has orders:create assigned.

# Unknowns

* Depth of the order book. If it's a fixed size, what are the prices at which a transaction would be rejected? I see some orders are rejected due to invalid prices, so the order book is not unlimited, but it may be large nonetheless.

# Issues

* The session is making testing the test scripts harder. I'm getting unwanted SelfCrossPrevented errors due to running the same test repeatedly. I want a way to clear out the session state but I can't because /order/cancel/session is prohibited.
* My choice of language and libraries limits my characters to those in the latin-1 set; I'm getting a "UnicodeEncodeError: 'latin-1' codec can't encode characters in position 0-1: ordinal not in range(256)", which is [well-known](https://stackoverflow.com/questions/34618149/post-unicode-string-to-web-service-using-python-requests-library), and encoding the values in UTF-8 makes them not serializable. So I'm omitting positive and negative tests for non-Latin-1 characters.

# TODOs

* Add [mocking from here](https://realpython.com/testing-third-party-apis-with-mocks/) or [here](https://mydeveloperplanet.com/2020/03/11/how-to-mock-a-rest-api-in-python/) 

