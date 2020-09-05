# -- FILE: features/negative.feature
# See https://cucumber.io/docs/guides/overview/ if you're unfamiliar 
# with BDD, or https://cucumber.io/docs/gherkin/reference/ for more
# info on Gherkin syntax

Feature: Negative Testcases (those that should fail)

  Scenario: Run a simple test
    Given we have insufficient funds
    When we buy 5.0 BTCUSD
    Then the order will fail

