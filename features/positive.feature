# -- FILE: features/positive.feature
# See https://cucumber.io/docs/guides/overview/ if you're unfamiliar 
# with BDD, or https://cucumber.io/docs/gherkin/reference/ for more
# info on Gherkin syntax.

# This file shows how Gherkin can be used to create tables for simple transactions.
# People who don't write code could edit the table and execute the tests and get 
# results. There are other ways, of course (a HTML page sending REST requests would be
# more user friendly, for example), but this method has some nice logging and it doesn't
# need a lot of work on the client side because it reuses the objects and methods from
# the other testcases.

# If unspecified, the order is exchange-limit immediate-or-cancel.

# The ethusd market seems to be very illiquid, and I had trouble finding 
# prices and quantities that resulted in executed transactions, so I commented them,
# but the code supports any currency.

Feature: Positive Testcases (those that should succeed), mostly with exchange-limit immediate-or-cancel orders

  Scenario: Table-driven buys
    Given we have enough funds
	When we buy currency from this table
	| amount | currency |     price |
	|    0.1 |   BTCUsd |  14000.01 |
    |   0.05 |   BTCUsD |  13500.01 |
#	|    1.0 |   ethUSD |    200.01 |
    Then the order will be executed in full

  Scenario: Table-driven sells
    Given we have enough funds
	When we sell currency from this table
	| amount | currency |     price |
	|    0.1 |   BTCUsd |   8000.01 |
#	|    1.0 |   ethUSD |     75.01 |
    Then the order will be executed in full

  Scenario: Table-driven buy or sell
    Given we have enough funds
	When we transact currency from this table
	|  side | amount | currency |    price |
	|   buy |    0.1 |   BTCUsd | 14000.01 |
#	|  sell |    0.5 |   ethUSD |    75.01 |
    Then the order will be executed in full

  Scenario: Table-driven buy or sell that will be cancelled
    Given we have enough funds
	When we transact currency from this table
	|  side | amount | currency |    price |
	|   buy |    0.1 |   BTCUsd |  8000.01 |
#	|  sell |    0.5 |   ethUSD |   300.01 |
    Then the order will be cancelled with ImmediateOrCancelWouldPost

  Scenario: Table-driven buy or sell with Fill-or-kill (FOK) order type specified in when
    Given we have enough funds
	When we issue FOK orders from this table
	|  side | amount | currency |    price |
	|   buy |    0.1 |   BTCUsd | 14000.01 |
#	|  sell |    0.5 |   ethUSD |    75.01 |
    Then the order will be executed in full
	
  Scenario: Table-driven buy or sell with Immediate-or-cancel (IOC) order type specified in when
    Given we have enough funds
	When we issue IOC orders from this table
	|  side | amount | currency |    price |
	|   buy |    0.1 |   BTCUsd | 14000.01 |
#	|  sell |    0.5 |   ethUSD |    75.01 |
    Then the order will be executed in full

Scenario: Table-driven buy or sell with Fill-or-kill (FOK) order type that will be killed
    Given we have enough funds
	# case-insensitive (thanks, regexs!)
	When we issue foK orders from this table
	|  side | amount | currency |    price |
	|   buy |    0.1 |   BTCUsd |  8000.01 |
	|  sell |    0.1 |   BTCUsd | 20000.01 |
#	|  sell |    0.5 |   ethUSD |    75.01 |
Then the order will be cancelled with FillOrKillWouldNotFill
