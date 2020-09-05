from behave import given, then, use_step_matcher
import parse
# import gemini

# Switch to regular expressions
use_step_matcher("re")


@given('we have insufficient funds')
def step_impl(context):
    pass


@then('the order will throw an unknow error')
def step_impl(context):
    if "error" in context.response:
        assert True


@then('the order will give the error (?P<expected_reason>(?i)\w+)')
def step_impl(context, expected_reason):
    # {'result': 'error', 'reason': 'InvalidPrice', 'message': 'Invalid price for symbol BTCUSD: 0.0001'}
    actual_result = context.response["result"]
    actual_reason = context.response["reason"]
    assert actual_reason == expected_reason and actual_result == "error"
