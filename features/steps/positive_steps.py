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
    assert context.failed is False


@when('we transact currency from this table')
def step_impl(context):
    for row in context.table:
        side = row['side'].lower()
        currency = row['currency'].lower()
        print(f"{side}ing from table {row['amount']} {currency} {row['price']} ")
        gemini.transact(row['amount'], currency, row['price'], side, "exchange limit", ["maker-or-cancel"] )
    assert context.failed is False


"""
The @when below is failing to match, and I don't know why. I've 
tried several regexs and the captured grouping was not 
recognized in each case. Setting aside for now.

@when('we (?P<order_side>(buy|sell)) currency from this table')
def step_impl(context):
    for row in context.table:
        print(f"{order_side}ing from table {row['amount']} {row['currency']} {row['price']} ")
        gemini.transact(row['amount'], row['currency'], row['price'], f"{order_side}", "exchange limit", ["maker-or-cancel"] )
    assert context.failed is False

"""

@when('we buy currency from this table')
def step_impl(context):
    order_side = "buy"
    for row in context.table:
        print(f"{order_side}ing from table {row['amount']} {row['currency']} {row['price']} ")
        gemini.transact(row['amount'], row['currency'], row['price'], f"{order_side}", "exchange limit", ["maker-or-cancel"] )
    assert context.failed is False

@when('we sell currency from this table')
def step_impl(context):
    order_side = "sell"
    for row in context.table:
        print(f"{order_side}ing from table {row['amount']} {row['currency']} {row['price']} ")
        gemini.transact(row['amount'], row['currency'], row['price'], f"{order_side}", "exchange limit", ["maker-or-cancel"] )
    assert context.failed is False

@then('the order will succeed')
def step_impl(context):
    # TODO: verify response matches request
    print(f'Success')
    assert context.failed is False
    #raise NotImplementedError(u'STEP: Then the order will succeed')
