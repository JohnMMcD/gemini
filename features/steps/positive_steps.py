from behave import *
from response import *
from order import *

# Use the regular expression matcher
use_step_matcher('re')


@given('we have enough funds')
def step_impl(context):
    pass


@when('we (?P<order_side>buy|sell) currency from this table')
def step_impl(context, order_side):
    for row in context.table:
        print(f"{order_side} {row['amount']} {row['currency']} at {row['price']}")
        context.order = ImmediateOrCancelOrder(order_side, row['amount'], row['currency'], row['price'])
        context.response = context.order.execute()
        # Conveniently, stdout is only echoed when the assertion is false. Inconveniently,
        # the stdout for all rows is echoed if a single row fails.
        print(context.order.payload)
        print(context.response)
        response = Response(context.response)
        response.show_summary()


@when('we issue (?P<order_type>[A-za-z]+) orders from this table')
def step_impl(context, order_type):
    for row in context.table:
        if order_type.lower() == "ioc":
            context.order = ImmediateOrCancelOrder(row['side'], row['amount'], row['currency'], row['price'])
            context.response = context.order.execute()
        elif order_type.lower() == "fok":
            context.order = FillOrKillOrder(row['side'], row['amount'], row['currency'], row['price'])
            context.response = context.order.execute()
        else:
            print("Order type not recognized")


@when('we transact currency from this table')
def step_impl(context):
    for row in context.table:
        context.order = ImmediateOrCancelOrder(row['side'], row['amount'], row['currency'], row['price'])
        print(f"{row['side']} {row['amount']} {row['currency']} at {row['price']}")
        context.response = context.order.execute()
        print(context.order.payload)
        print(context.response)
        response = Response(context.response)
        response.show_summary()


@then('the order will be executed in full')
def step_impl(context):
    ExecutedInFullResponse(context.response).verify(context.order)


@then('the order will be cancelled with (?P<reason>\w+)')
def step_impl(context, reason):
    CancelledInFullResponse(context.response).verify(context.order, reason=reason)
