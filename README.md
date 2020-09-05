# gemini


Dependencies:
* behave module

Assumptions:
* Re: “If you wish orders to be automatically cancelled when your session ends, see the require heartbeat section, or manually send the cancel all session orders message”, and given the “no other endpoints” restriction, I’ll assume that session creation and validity is out of scope, and therefore that a valid session exists and does not expire for the duration of the test.
* That the rate limits described at https://docs.gemini.com/rest-api/#rate-limits have been disabled, so I don’t have to build time.sleep(1) before each request.
* That performance testing is out of scope, including issues such as ensuring that multiple concurrent users can get their orders filled, etc.
* That the account has sufficient funds to execute transactions of arbitrary size, except in those testcases marked NSF.

