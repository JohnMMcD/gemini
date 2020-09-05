from behave import *
import parse
import gemini

# Switch to regular expressions
use_step_matcher('re')


@given('we have insufficient funds')
def step_impl(context):
    context


@then('the order will fail')
def step_impl(context):
    print(f'Order failed')
    assert context.failed is False
    # raise gemini.NSFError
