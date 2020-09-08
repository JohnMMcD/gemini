from response import *
import unittest
import logging


class TestMakerOrCancel(unittest.TestCase):
    """
    Maker-or-cancel orders never result in immediate transactions - they
    get posted to the order book, or cancelled. The testcases below seem similar
    to the fill-and-kill ones but they have been edited to account for this.
    """
    amount = "0.01"
    symbol = "btcusd"
    high_price = "16000"
    low_price = "1.01"

    # An amount that is impossible to fill in one order
    amount_way_too_high = "9999999999"

    logger = logging.getLogger(__name__)

    def test_buy_with_low_price_should_post(self):
        """Verify that your basic buy with a low price will post."""
        order = MakerOrCancelOrder("buy", self.amount, self.symbol, self.low_price)
        NoExecutedAmountResponse(order.execute()).verify(order)

    def test_buy_with_high_price_should_cancel(self):
        """Verify that your basic buy with a high price will cancel."""
        order = MakerOrCancelOrder("buy", self.amount, self.symbol, self.high_price)
        CancelledInFullResponse(order.execute()).verify(order, 'MakerOrCancelWouldTake')

    def test_sell_with_high_price_should_post(self):
        """Verify that your basic sell with a high price will post."""
        order = MakerOrCancelOrder("sell", self.amount, self.symbol, self.high_price)
        NoExecutedAmountResponse(order.execute()).verify(order)

    def test_sell_with_low_price_should_cancel(self):
        """Verify that your basic sell with a high price will post."""
        order = MakerOrCancelOrder("sell", self.amount, self.symbol, self.low_price)
        CancelledInFullResponse(order.execute()).verify(order, 'MakerOrCancelWouldTake')

    def test_buy_with_too_high_amount_should_give_error(self):
        """Verify that buys which are way too large to be completed throw an error instead of posting."""
        order = MakerOrCancelOrder("buy", self.amount_way_too_high, self.symbol, self.low_price)
        ErrorResponse(order.execute()).verify("InvalidQuantity")

    def test_sell_with_too_high_amount_should_give_error(self):
        """Verify that sells which are way too large to be completed throw an error instead of posting."""
        order = MakerOrCancelOrder("sell", self.amount_way_too_high, self.symbol, self.high_price)
        ErrorResponse(order.execute()).verify("InvalidQuantity")

    def test_buy_with_negative_price(self):
        """Verify that buys with a negative price give an error."""
        order = MakerOrCancelOrder("buy", self.amount, self.symbol, "-1")
        ErrorResponse(order.execute()).verify("InvalidPrice")

    def test_buy_with_zero_price(self):
        """Verify that buys with a zero price give an error."""
        order = MakerOrCancelOrder("buy", self.amount, self.symbol, "0.00")
        ErrorResponse(order.execute()).verify("InvalidPrice")

    @classmethod
    def setUpClass(cls):
        # Adapted from https://docs.python.org/3/howto/logging-cookbook.html
        verbose_format = '%(asctime)s : %(levelno)s : %(funcName)s : %(message)s'
        logging.basicConfig(level=logging.DEBUG, filemode='w',
                            filename="./reports/" + __name__ + ".log", format=verbose_format)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(logging.Formatter(verbose_format))
        cls.logger.addHandler(ch)
        cls.logger.info("Let's maker something happen! We'll pretend we are starting a new session.")

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("Fini! We'll pretend we cancelled all open orders and closed the session.")


if __name__ == '__main__':
    unittest.main()
