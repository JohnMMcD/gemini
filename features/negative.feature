# -- FILE: features/negative.feature
# See https://cucumber.io/docs/guides/overview/ if you're unfamiliar 
# with BDD, or https://cucumber.io/docs/gherkin/reference/ for more
# info on Gherkin syntax

# For BDD, I'm defining 'negative' to mean: 'those that throw an error', not 
# 'those that are syntactically invalid', because the latter don't lend themselves to
# a table format. Those that are cancelled are covered in the positive test cases.

Feature: Negative Testcases (those that should fail)

  Scenario: Negative testing with invalid prices
    Given we have enough funds
	When we sell currency from this table
	| amount | currency |   price |
	|    0.1 |   BTCUsd |  0.0001 |
	|    0.1 |   ethUSD |  0.0001 |
	|    0.1 |   btcusd | -0.0001 |
	|    0.1 |   btcusd |     0.0 |
    Then the order will give the error InvalidPrice
    # e.g., {'result': 'error', 'reason': 'InvalidPrice', 'message': 'Invalid price for symbol BTCUSD: 0.0001'}


  # Same scenario, with quantities. No code change was needed, just change the values and the expected error message.
  Scenario: Negative testing with invalid quantities
    Given we have enough funds
	When we sell currency from this table
	| amount | currency |  price |
	|     -1 |   BTCUsd |  13001 |
	|      0 |   ethUSD |    900 |
    Then the order will give the error InvalidQuantity
