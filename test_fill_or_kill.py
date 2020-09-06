import gemini
import unittest


class TestFillOrKill(unittest.TestCase):
    amount = "0.01"
    currency = "btcusd"
    buy_price = "16000"
    sell_price = "1.01"
    mandatory_fields = ["order_id", "symbol", "exchange", "price",
                        "avg_execution_price", "side", "type", "options",
                        "timestamp", "timestampms", "is_live",
                        "is_cancelled", "was_forced",
                        "executed_amount", "remaining_amount",
                        "original_amount", "is_hidden"]
    # Errors are considerably more terse, and the fields are different.
    mandatory_error_fields = ["result", "reason", "message"]
    type = "exchange limit"
    options = ["fill-or-kill"]
    cancel_reason = "FillOrKillWouldNotFill"
    # An amount that is impossible to fill in one order
    amount_way_too_high = "9999999999"
    # An amount that is *possible* to fill in one order, but the order book probably isn't deep enough
    amount_slightly_too_high = "99999"

    # self.verify_executed(response, self.amount, self.currency, self.buy_price, side, self.type, self.options)
    def verify_executed(self, response, amount, currency, price, side, type, options):
        """
        Verifies the response did not have any errors, was not cancelled, and
        had a positive execution amount. Other test may be added.
        Args:
            response: the dictionary containing the response to be checked
        Returns:
            True if everything went OK, throws assertion otherwise
        """
        # The 'result' key is only present if there is an error.
        self.assertNotIn("result", response, "Unexpected result in response: response['result']}")
        # is_cancelled should be false.
        self.assertFalse(response["is_cancelled"], f"Response was unexpectedly cancelled")
        # executed_amount must be positive
        self.assertTrue(float(response['executed_amount']) > 0,
                        f"Non-positive executed_amount: {response['executed_amount']}")
        self.assertEqual(response['executed_amount'], amount,
                         f"Amount mismatch! Expected {amount}, was {response['executed_amount']}")
        f_price = float(response['price'])
        self.assertTrue(abs(f_price - float(price)) < 0.001,
                        f"Executed prices differ: Expected {str(price)}), was {str(f_price)}")
        self.assertEqual(response['side'], side,
                         f"Side mismatch! Expected {side}, was {response['side']}")

        f_executed = float(response['executed_amount'])
        self.assertTrue(abs(f_executed - float(amount)) < 0.001,
                        f"Executed amounts differ: Expected {amount}, was {response['executed_amount']}")
        self.assertEqual(response['type'], type,
                         f"Type mismatch! Expected {type}, was {response['type']}")
        self.assertEqual(response['options'], options,
                         f"Options mismatch! Expected {options}, was {response['options']}")

        return True


    def verify_error(self, response, reason):
        """
        Verifies the response had the expected error, and the reason matched.
        Args:
            response: the dictionary containing the response to be checked
            reason: the text of the reason.
        Returns:
            True if everything went OK, throws assertion otherwise
        """
        for key in self.mandatory_error_fields:
            self.assertIn(key, response, f"Missing {key} key in response")
        self.assertEqual(response["result"], "error",
                         f"Result mismatch! Expected error, was {response['result']}")
        self.assertEqual(response["reason"], reason,
                         f"Reason mismatch! Expected {reason}, was {response['reason']}")
        # Errors shouldn't have the is_cancelled element. If this element exists, then we want to know the reason.
        self.assertNotIn("is_cancelled", response, f"Unexpected cancellation because of {response['reason']}")
        return True


    def verify_response_basics(self, response):
        # Check the keys which must be present. There values will be verified separately.
        # Should match list from https://docs.gemini.com/rest-api/#order-status
        for key in self.mandatory_fields:
            self.assertIn(key, response, f"Missing {key} key in response")
        self.assertEqual(response['exchange'], 'gemini',
                         f'Order Executed on wrong exchange??')
        self.assertFalse(response['was_forced'], "'Will always be false'")
        # This part is specific to fill-and-kill orders
        self.assertFalse(response['is_live'], "Fill or kill order should not still be live")



    def verify_cancelled(self, response, amount, reason):
        """
        Verifies the response did not have any errors, and was cancelled, and
        had a zero execution amount. Other test may be added.
        Args:
            response: the dictionary containing the response to be checked
        Returns:
            True if everything went OK, throws assertion otherwise.
        """
        # The 'result' key is only present if there is an error.
        self.assertNotIn("result", response, "Unexpected result in response: response['result']}")
        # is_cancelled should be True.
        self.assertTrue(response["is_cancelled"], f"Response should have been cancelled but was not")
        # executed_amount must be zero, or a very small value (never test floats for equality).
        f_expected = float(response['executed_amount'])
        self.assertTrue(f_expected < 0.001 and f_expected > -0.001,
                        f"Non-zero executed_amount: {response['executed_amount']}")
        # Checking the literal '0' string in addition to the floating point inequality
        self.assertEqual(response['executed_amount'], '0',
                         f"Non-zero executed_amount: {response['executed_amount']}")
        self.assertEqual(response["reason"], reason)
        self.assertEqual(response['remaining_amount'], amount, "Order was partially filled!")
        return True


    def testBuyNormal(self):
        side = "buy"
        response = gemini.transact(self.amount, self.currency, self.buy_price, side, self.type, self.options)
        self.verify_response_basics(response)
        self.verify_executed(response, self.amount, self.currency, self.buy_price, side, self.type, self.options)


    def testSellNormal(self):
        side = "sell"
        response = gemini.transact(self.amount, self.currency, self.sell_price, side, self.type, self.options)
        self.verify_response_basics(response)
        self.verify_executed(response, self.amount, self.currency, self.sell_price, side, self.type, self.options)


    def testBuyTooCheap(self):
        side = "buy"
        response = gemini.transact(self.amount, self.currency, self.sell_price, side, self.type, self.options)
        self.verify_response_basics(response)
        self.verify_cancelled(response, self.amount, self.cancel_reason)


    def testSellTooHigh(self):
        side = "sell"
        response = gemini.transact(self.amount, self.currency, self.buy_price, side, self.type, self.options)
        self.verify_response_basics(response)
        self.verify_cancelled(response, self.amount, self.cancel_reason)


    def testBuyWayTooMuch(self):
        """Verify that buy transactions which would break the exchange given an error."""
        side = "buy"
        response = gemini.transact(self.amount_way_too_high, self.currency,
                                   gemini.DICT_BIDASK[self.currency]['ask'], side, self.type, self.options)
        #self.verify_response_basics(response)
        self.verify_error(response, 'InvalidQuantity')


    def testSellWayTooMuch(self):
        """Verify that sell transactions which would break the exchange given an error."""
        side = "sell"
        response = gemini.transact(self.amount_way_too_high, self.currency, self.sell_price, side, self.type, self.options)
        # self.verify_response_basics(response)
        self.verify_error(response, 'InvalidQuantity')


    def testBuySlightlyTooMuch(self):
        """Verify that transactions which are too large to be completed are killed."""
        side = "buy"
        response = gemini.transact(self.amount_slightly_too_high, self.currency,
                                   gemini.DICT_BIDASK[self.currency]['ask'], side, self.type, self.options)
        self.verify_response_basics(response)
        self.verify_cancelled(response, self.amount_slightly_too_high, self.cancel_reason)


    def testSellSlightlyTooMuch(self):
        side = "sell"
        response = gemini.transact(self.amount_slightly_too_high, self.currency, self.sell_price, side, self.type, self.options)
        self.verify_response_basics(response)
        self.verify_cancelled(response, self.amount_slightly_too_high, self.cancel_reason)


if __name__ == '__main__':
    unittest.main()
