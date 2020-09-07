from behave import given, then, use_step_matcher
from order import *
from response import *

# Switch to regular expressions
use_step_matcher("re")


@given('we have insufficient funds')
def step_impl(context):
    pass


@then('the order will give the error (?P<expected_reason>(?i)\w+)')
def step_impl(context, expected_reason):
    assert ErrorResponse(context.response).verify(expected_reason), \
        f"Order was supposed to give an error with {expected_reason}, but did not."
