from response import *
import unittest
import logging


class TestFillOrKillOO(unittest.TestCase):
    amount = "0.01"
    symbol = "btcusd"
    buy_price = "16000"
    sell_price = "1.01"
    # An amount that is impossible to fill in one order
    amount_way_too_high = "9999999999"
    # An amount that is *possible* to fill in one order, but the order book probably isn't deep enough
    amount_slightly_too_high = "9999"
    logger = logging.getLogger(__name__)

    def test_buy_with_high_price(self):
        """Verify that your basic buy is executed in full."""
        order = FillOrKillOrder("buy", self.amount, self.symbol, self.buy_price)
        ExecutedInFullResponse(order.execute()).verify(order)

    def test_sell_with_low_price(self):
        """Verify that your basic sell is executed in full."""
        order = FillOrKillOrder("sell", self.amount, self.symbol, self.sell_price)
        ExecutedInFullResponse(order.execute()).verify(order)

    def test_buy_with_low_price(self):
        """Verify that buying with a price that's too low gets cancelled."""
        order = FillOrKillOrder("buy", self.amount, self.symbol, self.sell_price)
        CancelledInFullResponse(order.execute()).verify(order, reason="FillOrKillWouldNotFill")

    def test_sell_with_high_price(self):
        """Verify that selling with a price that's too high gets cancelled."""
        order = FillOrKillOrder("sell", self.amount, self.symbol, self.buy_price)
        CancelledInFullResponse(order.execute()).verify(order, reason="FillOrKillWouldNotFill")

    def test_buy_way_too_much(self):
        """Verify that buys which are way too large to be completed throw an error."""
        order = FillOrKillOrder("buy", self.amount_way_too_high, self.symbol, self.buy_price)
        ErrorResponse(order.execute()).verify("InvalidQuantity")

    def test_sell_way_too_much(self):
        """Verify that sells which are way too large to be completed throw an error."""
        order = FillOrKillOrder("sell", self.amount_way_too_high, self.symbol, self.sell_price)
        ErrorResponse(order.execute()).verify("InvalidQuantity")

    def test_buy_slightly_too_much(self):
        """Verify that buys which are slightly too large to be completed are cancelled."""
        order = FillOrKillOrder("buy", self.amount_slightly_too_high, self.symbol, self.buy_price)
        CancelledInFullResponse(order.execute()).verify(order, reason="FillOrKillWouldNotFill")

    def test_sell_slightly_too_much(self):
        """Verify that sells which are slightly too large to be completed are cancelled."""
        order = FillOrKillOrder("sell", self.amount_slightly_too_high, self.symbol, self.sell_price)
        CancelledInFullResponse(order.execute()).verify(order, reason="FillOrKillWouldNotFill")

    def test_with_negative_price(self):
        """Verify that sells with a negative price give an error."""
        order = FillOrKillOrder("sell", self.amount, self.symbol, "-1")
        ErrorResponse(order.execute()).verify("InvalidPrice")

    def test_with_zero_price(self):
        """Verify that sells with a zero price give an error."""
        order = FillOrKillOrder("sell", self.amount, self.symbol, "0")
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
        cls.logger.info("Let's start filling and killing! We'll pretend we are starting a new session.")

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("Finished! We'll pretend we cancelled all open orders and closed the session.")


if __name__ == '__main__':
    unittest.main()
