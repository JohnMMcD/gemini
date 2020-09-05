# -- FILE: features/positive.feature
# See https://cucumber.io/docs/guides/overview/ if you're unfamiliar 
# with BDD, or https://cucumber.io/docs/gherkin/reference/ for more
# info on Gherkin syntax

Feature: Positive Testcases (those that should succeed)

  Scenario: Run a simple test
    Given we have enough funds
    When we buy 5.0 BTCUSD
    Then the order will succeed

    Given we have enough funds
    When we buy 5.0 ETHUSD
    Then the order will succeed

  Scenario: Table-driven exchange-limit maker-or-cancel buy order
    Given we have enough funds
	When we buy currency from this table
	| amount | currency | price |
	| 0.1 | BTCUsd | 3664 |
	| 1.1 | ethUSD | 1234 |
    Then the order will succeed

    Given we have enough funds
	When we sell currency from this table
	| amount | currency | price |
	| 0.1 | BTCUsd | 3665 |
	| 1.1 | ethUSD | 1235 |
    Then the order will succeed

    Given we have enough funds
	When we transact currency from this table
	| side | amount | currency | price |
	| buy | 0.1 | BTCUsd | 3666 |
	| sell | 1.1 | ethUSD | 1236 |
    Then the order will succeed
