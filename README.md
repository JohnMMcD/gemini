# Purpose

Testing the order_new API without involving any other API endpoints.

# Notes

This project uses three different coding / testing styles. In decreasing order of completeness, they are:
* object-oriented (OO): execute with run_oo_all.cmd/sh
* behavior-driven (BDD): execute with run_bdd.cmd. Re-uses the object-oriented classes, but adds BDD syntactic sugar.
* old-school "one big module": execute with python -m unittest test_fill_or_kill or test_order_side.

I prioritized creating interesting testcases over getting the highest count. I didn't repeat the testcases for the different currencies, for example, nor did I create testcases with a bunch of different quantities or prices that are functionally equivalent. The BDD 

# Dependencies

I externalized the API key and secret and put them in files key.txt and secret.txt in the root directory, so these files will need to be re-created before any testcases can be run. Alternatively, you can edit the order.py and gemini.py files to add the key and secret (search for API_KEY). I externalized them because I uploaded this to GitHub and wanted to exclude them from the upload. It's a private repository, but I still didn't feel comfortable uploading them. Please let me know if you want access to the repository so you can see the commit history.

Non-default modules used:
* behave (for Behavior Driven Development testing)

Modules from the sample:
* requests, json, base64, hmac, hashlib, datetime, time

Default modules:
* unittest, logging, os, system

Also, the "one big module" style retrieves data from a third-party web site; see MOCKISH_BASE_URL in gemini.py for details.

# Assumptions

* That the account has sufficient funds and the market has sufficient liquidity to execute transactions of a reasonable size. There are no checks for volume because the relevant endpoints are prohibited. No attempt was made to use realistic prices. E.g., for an immediate-or-cancel buy order, I will use a very high price if the expected outcome is a filled order, and a very low price if the expected outcome is a cancellation.
* An exception to the previous assumption is that, for 2 partial buy/sell testcases using the immediate-or-cancel execution option, I attempt to determine the market price by doing a small buy order and extracting the execution price. However, the tests usually fail because the price moves and/or my quantity is incorrect.
* That these areas are out of scope:
 * anything related to high transaction volumes which could risk system stability (yes, I know one laptop won't stress the backend, but it seems impolite to appear to try). So whole classes of tests, such as memory leak, uptime, response time, stability, and anything else involving concurrent users, are out of scope. These aren't typically considered functional tests anyway, but I wanted to make it explicit that I wouldn't try to execute them.
  * session creation and validity. This is because the "If you wish orders to be automatically cancelled when your session ends, see the require heartbeat section, or manually send the cancel all session orders message" note combined with the "no other endpoints" restriction, makes session creation and validity difficult to test, so I'll assume a valid session exists and does not expire for the duration of the test.
 * security-related tests (SQL injection, probing nginx exploits, etc).
 * anything specific to master API keys, exchange accounts, and basically anything account-privilege related. The 'given' says that the user's account has the Trader role, and that the OAuth scope has orders:create assigned, and I assume these are correct.

# Unknowns

* In addition to the contents, I don't know the theoretical depth of the order book. If it's a fixed size, what are the prices at which a transaction would be rejected? I see some orders are rejected due to invalid prices, so the order book is not unlimited, but I can't determine its size.

# Issues

* Auctions were not open, so all those testcases failed. Similarly, indication of interest order testcases are failing for 0.1 BTC with the message "Invalid quantity for symbol BTCUSD: 0.1."
* The order-status doc lists statuses for market buy/sell but the new-order doc says these don't exist; see response.py
* Rate limiting is not working; I ran a testcase to check this and never got a 429 error.
* The session is making testing the test scripts harder. I'm getting unwanted SelfCrossPrevented errors due to running the same test repeatedly. I want a way to clear out the session state but I can't because /order/cancel/session is prohibited. Allowing this endpoint might make it easier for folks to write and test their tests.
* My choice of language and libraries limits my characters to those in the latin-1 set; I'm getting an error, "UnicodeEncodeError: 'latin-1' codec can't encode characters in position 0-1: ordinal not in range(256)", which is [well-known](https://stackoverflow.com/questions/34618149/post-unicode-string-to-web-service-using-python-requests-library), and encoding the values in UTF-8 makes them not serializable. So I'm omitting positive and negative tests for non-Latin-1 characters.

# TODOs / Backlog

* Add more testcases from the https://docs.sandbox.gemini.com/rest-api/#error-payload section. I actually started my own list of testcases and worked from that before I came across this section. There are many testcases that I didn't automate due to time constraints.
* To work around the endpoint availability issues, add [mocking from here](https://realpython.com/testing-third-party-apis-with-mocks/) or [here](https://mydeveloperplanet.com/2020/03/11/how-to-mock-a-rest-api-in-python/) 
