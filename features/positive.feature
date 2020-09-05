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

    Given we have enough funds
	When we buy currency from this table
	| amount | currency |
	| 0.1 | BTCUsd |
	| 1.1 | ethUSD |
    Then the order will succeed
