from response import *
import unittest
import logging


class AuctionOnlyOO(unittest.TestCase):
    """
    Since the "Get Active Orders" endpoint is prohibited, there's no way to verify these get sent to the auction.

    However, as I write this, all these are throwing "AuctionNotOpen" errors, despite
    https://docs.sandbox.gemini.com/rest-api/#sandbox saying "hourly auctions." Bug?
    """
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
        """Verify that your basic buy is sent."""
        order = AuctionOnlyOrder("buy", self.amount, self.symbol, self.buy_price)
        NoExecutedAmountResponse(order.execute()).verify(order)

    def test_sell_with_low_price(self):
        """Verify that your basic sell is executed in sent."""
        order = AuctionOnlyOrder("sell", self.amount, self.symbol, self.sell_price)
        NoExecutedAmountResponse(order.execute()).verify(order)

    def test_buy_with_low_price(self):
        """Trying to buying with a price that's too low will get sent, but probably not filled."""
        order = AuctionOnlyOrder("buy", self.amount, self.symbol, self.sell_price)
        NoExecutedAmountResponse(order.execute()).verify(order)

    def test_sell_with_high_price(self):
        """Similarly, trying to sell with a price that's too high will get sent, but probably not filled."""
        order = AuctionOnlyOrder("sell", self.amount, self.symbol, self.buy_price)
        NoExecutedAmountResponse(order.execute()).verify(order)

    def test_buy_way_too_much(self):
        """Verify that buys which are way too large to be completed throw an error."""
        order = AuctionOnlyOrder("buy", self.amount_way_too_high, self.symbol, self.buy_price)
        ErrorResponse(order.execute()).verify("InvalidQuantity")

    def test_sell_way_too_much(self):
        """Verify that sells which are way too large to be completed throw an error."""
        order = AuctionOnlyOrder("sell", self.amount_way_too_high, self.symbol, self.sell_price)
        ErrorResponse(order.execute()).verify("InvalidQuantity")

    def test_with_negative_price(self):
        """Verify that sells with a negative price give an error."""
        order = AuctionOnlyOrder("sell", self.amount, self.symbol, "-1")
        ErrorResponse(order.execute()).verify("InvalidPrice")

    def test_with_zero_price(self):
        """Verify that sells with a zero price give an error."""
        order = AuctionOnlyOrder("sell", self.amount, self.symbol, "0")
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
        cls.logger.info("Paddles at the ready! We'll pretend we are starting a new session.")

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("Finished! We'll pretend we cancelled all open orders and closed the session.")


if __name__ == '__main__':
    unittest.main()
