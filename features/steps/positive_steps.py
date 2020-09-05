from behave import *
import gemini

# Use the regular expression matcher
use_step_matcher('re')

@given('we have enough funds')
def step_impl(context):
    pass

@when(f'we buy (?P<amount>\d+\.\d+) (?P<currency>(?i){gemini.SUPPORTED_SYMBOLS_REGEX})')
def step_impl(context, amount, currency):
    price = "3663"
    print(f"Buying {amount} {currency} at {price}")
    context.response = gemini.transact(amount, currency, price, "buy",
                                       "exchange limit", ["maker-or-cancel"])
    context.price = price
    print(f"Price is {context.price}")
    assert context.failed is False


@when('we transact currency from this table')
def step_impl(context):
    for row in context.table:
        price = row['price']
        side = row['side'].lower()
        currency = row['currency'].lower()
        print(f"{side}ing from table {row['amount']} {currency} {price} ")
        context.response = gemini.transact(row['amount'], currency, price, side, "exchange limit", ["maker-or-cancel"] )
        context.price = price
        print(f"Price is {context.price}")
    assert context.failed is False


@when('we buy currency from this table')
def step_impl(context):
    order_side = "buy"
    for row in context.table:
        print(f"{order_side}ing from table {row['amount']} {row['currency']} {row['price']} ")
        context.response = gemini.transact(row['amount'], row['currency'], row['price'], f"{order_side}", "exchange limit", ["maker-or-cancel"] )
        context.price = row['price']
        print(f"Price is {context.price}")
    assert context.failed is False


@when('we sell currency from this table')
def step_impl(context):
    order_side = "sell"
    for row in context.table:
        print(f"{order_side}ing from table {row['amount']} {row['currency']} at {row['price']} ")
        context.response = gemini.transact(row['amount'], row['currency'], row['price'], f"{order_side}", "exchange limit", ["maker-or-cancel"] )
        context.price = row['price']
        print(f"Price is {context.price}")
        print(context.response)
    assert context.failed is False


@then('the order will succeed')
def step_impl(context):
    # TODO: Verify that is_cancelled is the correct key to examine
    is_cancelled = context.response["is_cancelled"]
    if is_cancelled:
        print(f"This was cancelled because {context.response['reason']}")
        # print(context.response["reason"])
    else:
        print("This went through!")
    assert context.failed is is_cancelled


"""
The @when below is failing to match, and I don't know why. I've 
tried several regexs and the captured grouping was not 
recognized in each case. Setting aside for now.

@when('we (?P<order_side>(buy|sell)) currency from this table')
def step_impl(context):
    for row in context.table:
        print(f"{order_side}ing from table {row['amount']} {row['currency']} {row['price']} ")
        context.response = gemini.transact(row['amount'], row['currency'], row['price'], f"{order_side}", "exchange limit", ["maker-or-cancel"] )
    assert context.failed is False

"""
