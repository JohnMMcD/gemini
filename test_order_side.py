import gemini
import unittest


class TestOrderSide(unittest.TestCase):
    amount = "0.01"
    currency = "btcusd"
    buy_price = "16000"
    sell_price = "1.01"

    type = "exchange limit"
    options = ["immediate-or-cancel"]

    def verify_fine(self, response):
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
        # is_cancelled and executed_amount should be there
        self.assertIn("is_cancelled", response, "Missing cancellation key in response")
        self.assertIn("executed_amount", response, "Missing executed_amount key in response")
        # is_cancelled should be false.
        self.assertFalse(response["is_cancelled"], f"Response was unexpectedly cancelled")
        # executed_amount must be positive
        self.assertTrue(float(response['executed_amount']) > 0,
                        f"Non-positive executed_amount: {response['executed_amount']}")
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
        self.assertTrue("result" in response and response["result"] == "error", "Did not get an error as expected")
        self.assertIn("reason", response, "Did not get a reason for the error")
        self.assertEqual(reason, response["reason"],
                        f"Got error as expected, but got {response['reason']} instead of {reason}")
        # Errors shouldn't have the is_cancelled element. If this element exists, then we want to know the reason.
        self.assertNotIn("is_cancelled", response, f"Unexpected cancellation because of {response['reason']}")
        return True

    def test_buy_normal(self):
        side = "buy"
        response = gemini.transact(self.amount, self.currency, self.buy_price, side, self.type, self.options)
        self.verify_fine(response)

    def test_sell_normal(self):
        side = "sell"
        response = gemini.transact(self.amount, self.currency, self.sell_price, side, self.type, self.options)
        self.verify_fine(response)

    def test_invalid_side(self):
        side = "notaside"
        response = gemini.transact(self.amount, self.currency, self.buy_price, side, self.type, self.options)
        self.verify_error(response, "InvalidSide")

    def test_empty_side(self):
        side = ""
        response = gemini.transact(self.amount, self.currency, self.buy_price, side, self.type, self.options)
        self.verify_error(response, "InvalidSide")


    @unittest.skip("Causes encoding errors - see Issues section of README.md")
    def test_buy_with_unicode_side(self):
        side = u"ᛇᚻðeλნ⠝ラı".encode("utf-8")
        response = gemini.transact(self.amount, self.currency, self.price, side, self.type, self.options)
        self.verify_error(response, "InvalidSide")

if __name__ == '__main__':
    unittest.main()
