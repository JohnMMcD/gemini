from response import *
import unittest
import logging


class IndicationOfInterestOO(unittest.TestCase):
    """
    These are very similar to the Auction Only testcases. Similarly, since the
    "Get Active Orders" endpoint is prohibited, there's no way to verify these get sent.
    """
    amount = "0.1"
    symbol = "btcusd"
    buy_price = "16000"
    sell_price = "1.01"
    # An amount that is impossible to fill in one order
    amount_way_too_high = "9999999999"

    logger = logging.getLogger(__name__)

    def test_buy_with_high_price(self):
        """Verify that your basic buy is sent."""
        order = IndicationOfInterestOrder("buy", self.amount, self.symbol, self.buy_price)
        NoExecutedAmountResponse(order.execute()).verify(order)

    def test_sell_with_low_price(self):
        """Verify that your basic sell is executed in sent."""
        order = IndicationOfInterestOrder("sell", self.amount, self.symbol, self.sell_price)
        NoExecutedAmountResponse(order.execute()).verify(order)

    def test_buy_with_low_price(self):
        """Trying to buying with a price that's too low will get sent, but probably not filled."""
        order = IndicationOfInterestOrder("buy", self.amount, self.symbol, self.sell_price)
        NoExecutedAmountResponse(order.execute()).verify(order)

    def test_sell_with_high_price(self):
        """Similarly, trying to sell with a price that's too high will get sent, but probably not filled."""
        order = IndicationOfInterestOrder("sell", self.amount, self.symbol, self.buy_price)
        NoExecutedAmountResponse(order.execute()).verify(order)

    def test_buy_way_too_much(self):
        """Verify that buys which are way too large to be completed throw an error."""
        order = IndicationOfInterestOrder("buy", self.amount_way_too_high, self.symbol, self.buy_price)
        ErrorResponse(order.execute()).verify("InvalidQuantity")

    def test_sell_way_too_much(self):
        """Verify that sells which are way too large to be completed throw an error."""
        order = IndicationOfInterestOrder("sell", self.amount_way_too_high, self.symbol, self.sell_price)
        ErrorResponse(order.execute()).verify("InvalidQuantity")

    def test_with_negative_price(self):
        """Verify that sells with a negative price give an error."""
        order = IndicationOfInterestOrder("sell", self.amount, self.symbol, "-1")
        ErrorResponse(order.execute()).verify("InvalidPrice")

    def test_with_zero_price(self):
        """Verify that sells with a zero price give an error."""
        order = IndicationOfInterestOrder("sell", self.amount, self.symbol, "0")
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
        cls.logger.info("Let's start showing some interest! " +
                        "We'll pretend we are starting a new session, " +
                        "although it doesn't matter since there's an ephemeral order book.")

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("Finished! We'll let the orders blow away like dust in the wind.")


if __name__ == '__main__':
    unittest.main()
