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
        context.order = ImmediateOrCancelOrder(order_side, row['amount'], row['currency'], row['price'])
        context.response = context.order.execute()
        # stdout is only echoed when the assertion is false
        print(context.order.payload)
        print(context.response)


@when('we transact currency from this table')
def step_impl(context):
    for row in context.table:
        context.order = ImmediateOrCancelOrder(row['side'], row['amount'], row['currency'], row['price'])
        context.response = context.order.execute()
        print(context.order)
        print(context.response)


@then('the order will be executed in full')
def step_impl(context):
    ExecutedInFullResponse(context.response).verify(context.order)


@then('the order will be cancelled with (?P<reason>\w+)')
def step_impl(context, reason):
    CancelledInFullResponse(context.response).verify(context.order, reason=reason)
