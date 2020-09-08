# -- FILE: features/negative.feature
# See https://cucumber.io/docs/guides/overview/ if you're unfamiliar 
# with BDD, or https://cucumber.io/docs/gherkin/reference/ for more
# info on Gherkin syntax

Feature: Negative Testcases (those that should fail)

  Scenario: Negative testing with invalid prices
    Given we have enough funds
	When we sell currency from this table
	| amount | currency |  price |
	|    0.1 |   BTCUsd | 0.0001 |
	|    0.1 |   ethUSD | 0.0001 |
    Then the order will give the error InvalidPrice
    # {'result': 'error', 'reason': 'InvalidPrice', 'message': 'Invalid price for symbol BTCUSD: 0.0001'}
