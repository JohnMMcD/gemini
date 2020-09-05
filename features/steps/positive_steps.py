from behave import *
import gemini

# Use the regular expression matcher
use_step_matcher('re')


@given('we have enough funds')
def step_impl(context):
    pass


@when('we (?P<order_side>buy|sell) currency from this table')
def step_impl(context, order_side):
    for row in context.table:
        print(f"{order_side}ing {row['amount']} {row['currency']} at {row['price']} ")
        context.response = gemini.transact(row['amount'], row['currency'], row['price'],
                                           f"{order_side}", "exchange limit",
                                           ["immediate-or-cancel"])
        context.price = row['price']
        print(context.response)


@when('we transact currency from this table')
def step_impl(context):
    for row in context.table:
        price = row['price']
        context.price = price
        side = row['side'].lower()
        currency = row['currency'].lower()
        print(f"{side}ing from table {row['amount']} {currency} {price} in transaction")
        context.response = gemini.transact(row['amount'], currency, price, side,
                                           "exchange limit", ["immediate-or-cancel"])

@then('the order will not be cancelled')
def step_impl(context):
    if "result" in context.response:
        if context.response["result"] == "error":
            assert False, f"Unexpected error because of {context.response['reason']}"
    if context.response["is_cancelled"]:
        assert False, (f"This should not have been cancelled, but it was"
                       f" because {context.response['reason']}")
    else:
        print("This went through!")


@then('the order will be cancelled')
def step_impl(context):
    if "result" in context.response:
        if context.response["result"] == "error":
            assert False, (f"This was supposed to be cancelled, but it "
                           f"threw an unexpected error instead because "
                           f"of {context.response['reason']}")
    if context.response["is_cancelled"]:
        print(f"As expected, this was cancelled. Reason: {context.response['reason']}")
    else:
        assert False, "This went through even though it was supposed to be cancelled!"
