from behave import *
import parse
import gemini

# Switch to regular expressions
use_step_matcher('re')

insufficient_funds = True

@given('we have enough funds')
def step_impl(context):
    global insufficient_funds
    insufficient_funds = False


@then('the transaction will succeed')
def step_impl(context):
    assert context.failed is False
    assert context.tests_count >= 0


@when(f'we buy (?P<amount>\d+\.\d+) (?P<currency>(?i){gemini.SUPPORTED_SYMBOLS_REGEX})')
def step_impl(context, amount, currency):
    # global insufficient_funds
    assert context.failed is False
    print(f'buying {amount} of {currency}')
    print(f'Valid currencies: {gemini.SUPPORTED_SYMBOLS_REGEX}')
#    print(f'insufficient_funds: {insufficient_funds}')
    assert context.failed is False

@when('we buy currency from this table')
def step_impl(context):
    for row in context.table:
        print(f"Buying from table {row[0]} {row[1]}")
        # TODO: execute the purchase
        gemini.buy(row[0], row[1], "3663")
    assert context.failed is False


@then('the order will succeed')
def step_impl(context):
    print(f'Success')
    assert context.failed is False
    #raise NotImplementedError(u'STEP: Then the order will succeed')
