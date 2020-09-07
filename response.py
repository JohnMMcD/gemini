from order import *

class Response():
    """
    Parent class for responses. Note that error responses have very different formats than other responses.
    """
    raw = {}

    def __init__(self, dict_response):
        self.raw = dict_response


"""
    result = ""
    reason = ""
    message = ""
    order_id = ""
    client_order_id = ""
    id = ""
    symbol = ""
    exchange = "gemini"
    avg_execution_price = ""
    side = ""
    order_type = ""
    timestamp = ""
    timestampms = ""
    is_live = ""
    is_cancelled = ""
    is_hidden = ""
    was_forced = ""
    executed_amount = ""
    options = []
    price = ""
    original_amount = ""
    remaining_amount = ""
"""


class ErrorResponse(Response):
    def __init__(self, dict_response):
        Response.__init__(self, dict_response)

    mandatory_error_fields = ["result", "reason", "message"]

    def verify(self, reason):
        """
        Verifies the response was an error, and the reason matched.
        Args:
            reason: the text of the reason. This is not the 'message'!
        Returns:
            True if everything went OK, throws assertion otherwise
        """
        #        print(f"verifying error was due to {reason}")
        for key in self.mandatory_error_fields:
            assert key in self.raw, f"Missing {key} key in response"
        assert self.raw["result"] == "error", f"Result mismatch! Expected error, was {self.raw['result']}"
        assert self.raw["reason"] == reason, f"Reason mismatch! Expected {reason}, was {self.raw['reason']}"
        # Errors shouldn't have the is_cancelled element. If this element exists, then we want to know the reason.
        assert "is_cancelled" not in self.raw, f"Unexpected cancellation because of {self.raw['reason']}"
        return True


class CancelledInFullResponse(Response):
    def __init__(self, dict):
        Response.__init__(self, dict)

    def verify(self, reason):
        """
        Verifies the response was cancelled and the reason matched.
        Cancelled responses do not have any errors.
        TODO: Determine other tests.
        Args:
            reason: the reason for the cancellation
        Returns:
            True if everything went OK, throws assertion otherwise.
        """
        # The 'result' key is only present if there is an error, which shouldn't be the case
        # Also log the reason for the error, because it's good to know and the reason is always given,
        # unless there's a KeyError.
        assert "result" not in self.raw, \
            f"Unexpected result in response: {self.raw['result']} with reason {self.raw['reason']}"
        # is_cancelled should be True.
        assert self.raw["is_cancelled"], f"Response should have been cancelled but was not"
        assert self.raw["reason"] == reason, f"Reason mismatch: expected {reason}, got {self.raw['reason']}"

        # executed_amount must be zero, or a very small value (never test floats for equality).
        f_expected = float(self.raw['executed_amount'])
        assert f_expected < 0.001 and f_expected > -0.001, f"Non-zero executed_amount: {self.raw['executed_amount']}"
        # Checking the literal '0' string in addition to the floating point inequality
        assert self.raw['executed_amount'] == '0', f"Non-zero executed_amount: {self.raw['executed_amount']}"

        return True


class ExecutedInFullResponse(Response):
    def __init__(self, dict):
        Response.__init__(self, dict)

    def verify(self, response, amount, currency, price, side, order_type, options):
        """
        Verifies the response did not have any errors, was not cancelled, and
        had a positive execution amount. Other test may be added.
        Args:
            response: the dictionary containing the response to be checked
            amount: the quantity that should have been executed
            currency: the currency symbol
            price: the price. Might need to tweak this because best effort means
            that buys might be at a lower price than requested
            order_type: type of order
            side: buy or sell
            options:

        Returns:
            True if everything went OK, throws assertion otherwise
        """
        # The 'result' key is only present if there is an error.
        assert "result" not in response, "Unexpected result in response: self.raw['result']}"
        # is_cancelled should be false.
        assert not self.raw["is_cancelled"], f"Response was unexpectedly cancelled with reason {self.raw['reason']}"
        # executed_amount must be positive
        assert float(self.raw['executed_amount']) > 0, f"Non-positive executed_amount: {self.raw['executed_amount']}"
        assert self.raw[
                   'executed_amount'] == amount, f"Amount mismatch! Expected {amount}, was {self.raw['executed_amount']}"
        assert self.raw['symbol'] == currency, f"Symbol mismatch! Expected {currency}, was {self.raw['symbol']}"
        f_price = float(self.raw['price'])
        assert abs(
            f_price - float(price)) < 0.001, f"Executed prices differ: Expected {str(price)}), was {str(f_price)}"
        assert self.raw['side'] == side, f"Side mismatch! Expected {side}, was {self.raw['side']}"
        f_executed = float(self.raw['executed_amount'])
        assert abs(f_executed - float(
            amount)) < 0.001, f"Executed amounts differ: Expected {amount}, was {self.raw['executed_amount']}"
        assert self.raw['type'] == order_type, f"Type mismatch! Expected {order_type}, was {self.raw['type']}"
        assert self.raw['options'] == options, f"Options mismatch! Expected {options}, was {self.raw['options']}"

        return True

    def verify(self, order):
        """
        Verifies the response did not have any errors, was not cancelled, was executed in full, and
        matches the order submitted. Also some sanity checks for things like a positive execution
        amount. Other tests may be added.
        Args:
            order: the order to check against.
        Returns:
            True if everything went OK, throws assertion otherwise.
        """
        # The 'result' key is only present if there is an error, and there should be a reason
        assert "result" not in self.raw, \
            f"Unexpected result in response: {self.raw['result']} {self.raw['reason']}"
        # is_cancelled should be false.
        assert not self.raw["is_cancelled"], \
            f"Response was unexpectedly cancelled with reason {self.raw['reason']}."
        # executed_amount must be positive
        assert float(self.raw['executed_amount']) > 0, \
            f"Non-positive executed_amount: {self.raw['executed_amount']}"
        assert self.raw['executed_amount'] == order.amount, \
            f"Amount mismatch! Expected {order.amount}, was {self.raw['executed_amount']}"
        assert self.raw['symbol'] == order.symbol, \
            f"Symbol mismatch! Expected {order.symbol}, was {self.raw['symbol']}"
        f_price = float(self.raw['price'])
        assert abs(f_price - float(order.price)) < 0.001, \
            f"Executed prices differ: Expected {str(order.price)}), was {str(f_price)}"
        assert self.raw['side'] == order.side, \
            f"Side mismatch! Expected {order.side}, was {self.raw['side']}"
        f_executed = float(self.raw['executed_amount'])
        assert abs(f_executed - float(order.amount)) < 0.001, \
            f"Executed amounts differ: Expected {order.amount}, was {self.raw['executed_amount']}"
        assert self.raw['type'] == order.order_type, \
            f"Type mismatch! Expected {order.order_type}, was {self.raw['type']}"
        assert self.raw['options'] == order.options, \
            f"Options mismatch! Expected {order.options}, was {self.raw['options']}"

        return True


class NoExecutedAmountResponse(Response):
    """ This response is used when the order was executed but the executed_amount should be zero."""
    def __init__(self, dict):
        Response.__init__(self, dict)

    def verify(self, order):
        """
        Verifies the response did not have any errors, was not cancelled, and has a zero execution
        amount. Other tests may be added.
        Args:
            order: the order to check against.
        Returns:
            True if everything went OK, throws assertion otherwise.
        """
        # The 'result' key is only present if there is an error, and there should be a reason
        # print(self.raw)
        assert "result" not in self.raw, \
            f"Unexpected result: {self.raw['result']} with reason: {self.raw['reason']} and message: {self.raw['message']}"
        # is_cancelled should be false.
        assert not self.raw["is_cancelled"], \
            f"Unexpectedly cancelled with reason {self.raw['reason']}."
        # executed_amount must be zero
        f_executed = float(self.raw['executed_amount'])
        assert (f_executed > -0.001) and (f_executed < 0.001), \
            f"Non-zero executed_amount: {self.raw['executed_amount']}"
#        assert self.raw['remaining_amount'] == order.amount, \
#            f"Amount mismatch! Expected {order.amount} to be remaining, was {self.raw['remaining_amount']}"
        assert self.raw['symbol'] == order.symbol, \
            f"Symbol mismatch! Expected {order.symbol}, was {self.raw['symbol']}"
        f_price = float(self.raw['price'])
        assert abs(f_price - float(order.price)) < 0.001, \
            f"Executed prices differ: Expected {str(order.price)}), was {str(f_price)}"
        assert self.raw['side'] == order.side, \
            f"Side mismatch! Expected {order.side}, was {self.raw['side']}"
        assert self.raw['options'] == order.options, \
            f"Options mismatch! Expected {order.options}, was {self.raw['options']}"
        """
        Verify the type
        This seems like a bug. https://docs.gemini.com/rest-api/#order-status lists these values for the type field:
        * exchange limit
        * auction-only exchange limit
        * market buy
        * market sell
        * indication-of-interest
        
        First, per https://docs.gemini.com/rest-api/#new-order, "The API doesn't directly support 
        market orders because they provide you with no price protection", so I don't see how the 
        'market buy' and 'market sell' types would ever be used.
        Second, 'stop-limit' is missing from the list. This value is returned when the order type is
        "exchange stop limit". The values in the bullets should be corrected to the actual returned values,
        including checking that the hyphens are noted correctly. 
        Also should think about changing the values returned here to match the values from the
        order-new API, but this would affect backwards compatibility.

        Due to this issue, I'm disabling the test for order type 
        assert self.raw['type'] == order.order_type, \
            f"Type mismatch! Expected {order.order_type}, was {self.raw['type']}"

        """


        return True

