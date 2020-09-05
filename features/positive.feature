# -- FILE: features/positive.feature
# See https://cucumber.io/docs/guides/overview/ if you're unfamiliar 
# with BDD, or https://cucumber.io/docs/gherkin/reference/ for more
# info on Gherkin syntax

# WHAT ABOUT MARKET ORDERS?
# The API doesn't directly support market orders because they provide
# you with no price protection.
# Instead, use the “immediate-or-cancel” order execution option, coupled
# with an aggressive limit price (i.e. very high for a buy order or very
# low for a sell order), to achieve the same result.

Feature: Positive Testcases (those that should succeed)

  Scenario: Table-driven exchange-limit immediate-or-cancel buy order
    Given we have enough funds
	When we buy currency from this table
	| amount | currency |  price |
	|    0.1 |   BTCUsd | 999999 |
	|    0.1 |   ethUSD | 999999 |
    Then the order will not be cancelled

  Scenario: Table-driven exchange-limit immediate-or-cancel sell order
    Given we have enough funds
	When we sell currency from this table
	| amount | currency |  price |
	|    0.1 |   BTCUsd |   0.01 |
	|    0.1 |   ethUSD |   0.01 |
    Then the order will not be cancelled

  Scenario: Table-driven exchange-limit immediate-or-cancel buy or sell
    Given we have enough funds
	When we transact currency from this table
	|  side | amount | currency |  price |
	|   buy |    0.1 |   BTCUsd | 99999 |
	|  sell |    0.1 |   ethUSD |    0.1 |
    Then the order will not be cancelled
