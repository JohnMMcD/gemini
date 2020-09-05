# Purpose
If you're reading this, you should know this repository's purpose.

# Dependencies

* behave module

# Assumptions

* That the account has sufficient funds and the market has sufficient liquidity to execute transactions of arbitrary size, except for those negative testcases marked NSF.
* That the user's account has the Trader role specified
* That the OAuth scope has orders:create assigned to access this endpoint.
* That the [rate limits](https://docs.gemini.com/rest-api/#rate-limits) have been disabled, so I don't have to add time.sleep(1) before each request.
* That these areas are out of scope:
 * anything related to high transaction volumes which could risk system stability (yes, I know one laptop won't stress the backend, but it seems impolite to appear to try). So whole classes of tests, such as memory leak, uptime, response time, stability, and anything else involving concurrent users, are out of scope.
 * session creation and validity. This is because the "If you wish orders to be automatically cancelled when your session ends, see the require heartbeat section, or manually send the cancel all session orders message" note combined with the "no other endpoints" restriction, makes session creation and validity difficult to test, so I'll assume a valid session exists and does not expire for the duration of the test.
 * anything specific to master API keys and exchange accounts


# Unknowns

* Depth of the order book. If fixed, what are the prices at which a book would be rejected


# TODOs

# Add mocking from https://realpython.com/testing-third-party-apis-with-mocks/ and https://mydeveloperplanet.com/2020/03/11/how-to-mock-a-rest-api-in-python/ 

