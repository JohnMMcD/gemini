from response import *
from order import *
import unittest
import logging


class TestImmediateOrCancel(unittest.TestCase):
    """
    Most of these testcases are indistinguishable from the fill-or-kill testcases. The
    difference would be noticeable if there were a way to inspect the order book and create
    an order that would be partially filled (and therefore, partially cancelled). I attempt
    to do this in testImmediateOrCancelPartialBuy/Sell, but it usually doesn't work because
    I get a price that's too high or low, so the whole order either fills or cancels.
    """
    amount = "0.01"
    symbol = "btcusd"
    buy_price = "16000"
    sell_price = "1.01"
    # An amount that is impossible to fill in one order
    amount_way_too_high = "9999999999"
    # An amount that is *possible* to fill in one order, but the order book probably isn't deep enough
    amount_which_can_be_partially_filled = "9999"
    best_guess = 0.0
    logger = logging.getLogger(__name__)

    def test_buy_with_high_price(self):
        """Verify that your basic buy is executed in full."""
        order = ImmediateOrCancelOrder("buy", self.amount, self.symbol, self.buy_price)
        ExecutedInFullResponse(order.execute()).verify(order)

    def test_sell_with_low_price(self):
        """Verify that your basic sell is executed in full."""
        order = ImmediateOrCancelOrder("sell", self.amount, self.symbol, self.sell_price)
        ExecutedInFullResponse(order.execute()).verify(order)

    def test_buy_with_low_price(self):
        """Verify that buying with a price that's too low gets cancelled."""
        order = ImmediateOrCancelOrder("buy", self.amount, self.symbol, self.sell_price)
        CancelledInFullResponse(order.execute()).verify(order, reason="ImmediateOrCancelWouldPost")

    def test_sell_with_high_price(self):
        """Verify that selling with a price that's too high gets cancelled."""
        order = ImmediateOrCancelOrder("sell", self.amount, self.symbol, self.buy_price)
        CancelledInFullResponse(order.execute()).verify(order, reason="ImmediateOrCancelWouldPost")

    def test_buy_way_too_much(self):
        """Verify that buys which are way too large to be completed throw an error."""
        order = ImmediateOrCancelOrder("buy", self.amount_way_too_high, self.symbol, self.buy_price)
        ErrorResponse(order.execute()).verify("InvalidQuantity")

    def test_sell_way_too_much(self):
        """Verify that sells which are way too large to be completed throw an error."""
        order = ImmediateOrCancelOrder("sell", self.amount_way_too_high, self.symbol, self.sell_price)
        ErrorResponse(order.execute()).verify("InvalidQuantity")

    def test_partial_buy(self):
        """ Verify that buys which are slightly too large to be completed are partially filled.

        What I would do if allowed access to the order book is:
        # Inspect order book. Let's say the asks are 1 BTC at 10000, 1 BTC at 10250, and 2 BTC at 10500.
        # Create an IOC order to buy 3 BTC at 10250.
        # verify in the response:
         # executed_amount==2
         # avg_execution_price=10125
         # remaining_amount==1
         # original_amount==3
         # is_cancelled==true

        See the implementation of guess_current_market for what I actually did. Or don't - it's not pretty.
        """
        current_guess = self.guess_current_market()
        # Give it a small bump to increase the odds that it will be partially filled
        self.best_guess = round(current_guess * 1.005, 2)
        partial_response = ImmediateOrCancelOrder("buy", "2", self.symbol, str(self.best_guess)).execute()
        fields = ['executed_amount', 'avg_execution_price', 'remaining_amount', 'original_amount',
                  'is_cancelled', 'result', 'reason', 'message']
        for field in fields:
            if field in partial_response:
                self.logger.debug(f"{field}={partial_response[field]}")
        assert partial_response['is_cancelled'], "PartialBuy should be cancelled but wasn't."
        assert float(partial_response['executed_amount']) > 0.0, \
            f"Incorrect executed_amount: {partial_response['executed_amount']}"
        self.logger.debug("done with PartialBuy")

    def test_partial_sell(self):
        """ Verify that sells which are slightly too large to be completed are partially filled.

        What I would do if allowed access to the order book is:
        # Inspect order book. Let's say the bids are for 1 BTC at 10000, 1 BTC at 9750 and 1 BTC at 9500
        # With IOC, sell 3 BTC at 9750. One should get filled at 10000, 1 at 9750 and the third cancelled.
        # verify in the response:
        # executed_amount==1
        # avg_execution_price=9875
        # remaining_amount==1
        # original_amount=3
        # is_cancelled==true

        See the implementation of guess_current_market for what I actually did.
        """
        current_guess = self.guess_current_market()
        # Give it a small bump down to increase the odds that it will be partially filled
        self.best_guess = round(current_guess * 0.995, 2)
        partial_response = ImmediateOrCancelOrder("sell", "2", self.symbol, str(self.best_guess)).execute()
        fields = ['executed_amount', 'avg_execution_price', 'remaining_amount', 'original_amount',
                  'is_cancelled', 'result', 'reason', 'message']
        for field in fields:
            if field in partial_response:
                self.logger.debug(f"{field}={partial_response[field]}")
        assert partial_response['is_cancelled'], "PartialSell should be cancelled but wasn't."
        assert float(partial_response['executed_amount']) > 0.0, \
            f"Incorrect executed_amount: {partial_response['executed_amount']}"
        self.logger.debug("done with PartialSell")

    def test_with_negative_price(self):
        """Verify that sells with a negative price give an error."""
        order = ImmediateOrCancelOrder("sell", self.amount, self.symbol, "-1")
        ErrorResponse(order.execute()).verify("InvalidPrice")

    def test_with_zero_price(self):
        """Verify that sells with a zero price give an error."""
        order = ImmediateOrCancelOrder("sell", self.amount, self.symbol, "0")
        ErrorResponse(order.execute()).verify("InvalidPrice")

    def guess_current_market(self):
        """
        Do a small fill or kill order to get the market price.

        TODO: replace with a call to /v1/pubticker/btcusd and the 'last' field.
        Returns:
            A floating point number, which should be very close to the market price.
        """
        order = FillOrKillOrder("buy", self.amount, self.symbol, self.buy_price)
        response = ExecutedInFullResponse(order.execute())
        price = response.get_avg_execution_price()
        self.logger.debug(f"Market price should be {price}")
        return float(price)

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
        cls.logger.info("Let's get going! We'll pretend we are starting a new session.")

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("Finished! We'll pretend we cancelled all open orders and closed the session.")


if __name__ == '__main__':
    unittest.main()
