# -- FILE: features/positive.feature
# See https://cucumber.io/docs/guides/overview/ if you're unfamiliar 
# with BDD, or https://cucumber.io/docs/gherkin/reference/ for more
# info on Gherkin syntax

Feature: Positive Testcases (those that should succeed) with exchange-limit immediate-or-cancel orders

  Scenario: Table-driven buys
    Given we have enough funds
	When we buy currency from this table
	| amount | currency |     price |
	|    0.1 |   BTCUsd |  12000.01 |
	|    1.0 |   ethUSD |    300.01 |
    Then the order will be executed in full

  Scenario: Table-driven sells
    Given we have enough funds
	When we sell currency from this table
	| amount | currency |     price |
	|    0.1 |   BTCUsd |   9000.01 |
	|    1.0 |   ethUSD |    100.01 |
    Then the order will be executed in full

  Scenario: Table-driven buy or sell
    Given we have enough funds
	When we transact currency from this table
	|  side | amount | currency |    price |
	|   buy |    0.1 |   BTCUsd | 12000.01 |
	|  sell |    1.0 |   ethUSD |   100.01 |
    Then the order will be executed in full

  Scenario: Table-driven buy or sell that will be cancelled
    Given we have enough funds
	When we transact currency from this table
	|  side | amount | currency |    price |
	|   buy |    0.1 |   BTCUsd |  8000.01 |
	|  sell |    1.0 |   ethUSD |   300.01 |
    Then the order will be cancelled with ImmediateOrCancelWouldPost
