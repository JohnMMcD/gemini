from response import *

import unittest


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

    def testImmediateOrCancelBuyWithHighPrice(self):
        """Verify that your basic buy is executed in full."""
        order = ImmediateOrCancelOrder("buy", self.amount, self.symbol, self.buy_price)
        ExecutedInFullResponse(order.execute()).verify(order)

    def testImmediateOrCancelSellWithLowPrice(self):
        """Verify that your basic sell is executed in full."""
        order = ImmediateOrCancelOrder("sell", self.amount, self.symbol, self.sell_price)
        ExecutedInFullResponse(order.execute()).verify(order)

    def testImmediateOrCancelBuyWithLowPrice(self):
        """Verify that buying with a price that's too low gets cancelled."""
        order = ImmediateOrCancelOrder("buy", self.amount, self.symbol, self.sell_price)
        CancelledInFullResponse(order.execute()).verify("ImmediateOrCancelWouldPost")

    def testImmediateOrCancelSellWithHighPrice(self):
        """Verify that selling with a price that's too high gets cancelled."""
        order = ImmediateOrCancelOrder("sell", self.amount, self.symbol, self.buy_price)
        CancelledInFullResponse(order.execute()).verify("ImmediateOrCancelWouldPost")

    def testImmediateOrCancelBuyWayTooMuch(self):
        """Verify that buys which are way too large to be completed throw an error."""
        order = ImmediateOrCancelOrder("buy", self.amount_way_too_high, self.symbol, self.buy_price)
        ErrorResponse(order.execute()).verify("InvalidQuantity")

    def testImmediateOrCancelSellWayTooMuch(self):
        """Verify that sells which are way too large to be completed throw an error."""
        order = ImmediateOrCancelOrder("sell", self.amount_way_too_high, self.symbol, self.sell_price)
        ErrorResponse(order.execute()).verify("InvalidQuantity")

    def testImmediateOrCancelPartialBuy(self):
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
        
        Another solution, shown below, uses a Fibonacci search with a lot of FoK orders to determine the prices. 
        Start at a high price, then decrease the price until you go too low and the order get cancelled.
        When that happens, increase the price until it gets filled. Limit the price swings to a percentage of 
        the difference between the highest failed price and the lowest successful price. When the difference 
        is small enough, declare that the best price, and do the big order, which hopefully will be partially filled.
        """
        initial_guess = float(self.buy_price)
        last_guess = 0
        next_delta = 100
        count = 0
        lowest_worked = initial_guess
        highest_failed = last_guess
        current_guess = initial_guess
        close_enough = False
        while not close_enough:
            response = FillOrKillOrder("buy", self.amount, self.symbol, str(current_guess)).execute()
            if response['is_cancelled']:
                highest_failed = current_guess
                current_guess = current_guess + next_delta
            else:
                lowest_worked = current_guess
                current_guess = current_guess - next_delta
            count = count + 1
            spread = abs(highest_failed - lowest_worked)
            next_delta = round(max(spread * 0.33, 0.01), 2)
            current_guess = round(current_guess, 2)
            print(f"count={count} next_delta={str(next_delta)}")
            if abs(last_guess - current_guess) < 0.02:
                close_enough = True
            last_guess = current_guess
        # Give it a small bump to increase the odds that it will be partially filled
        self.best_guess = round(current_guess * 1.000005, 2)
        print(f"self.best_guess={self.best_guess} count={str(count)}")
        partial_response = ImmediateOrCancelOrder("buy", "2", self.symbol, str(self.best_guess)).execute()
        fields = ['executed_amount', 'avg_execution_price', 'remaining_amount', 'original_amount',
                  'is_cancelled', 'result', 'reason', 'message']
        for field in fields:
            if field in partial_response:
                print(f"{field}={partial_response[field]}")
        assert partial_response['is_cancelled'], "PartialBuy should be cancelled but wasn't."
        assert float(partial_response['execution_amount']) > 0.0, \
            f"Incorrect execution amount: {partial_response['execution_amount']}"
        print("done with PartialBuy")

    def testImmediateOrCancelPartialSell(self):
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

        We reuse the algorithm from the partial buy.
        """
        initial_guess = float(self.buy_price)
        last_guess = 0
        next_delta = 100
        count = 0
        lowest_worked = initial_guess
        highest_failed = last_guess
        current_guess = initial_guess
        close_enough = False
        while not close_enough:
            response = FillOrKillOrder("buy", self.amount, self.symbol, str(current_guess)).execute()
            if response['is_cancelled']:
                highest_failed = current_guess
                current_guess = current_guess + next_delta
            else:
                lowest_worked = current_guess
                current_guess = current_guess - next_delta
            count = count + 1
            spread = abs(highest_failed - lowest_worked)
            next_delta = round(max(spread * 0.33, 0.01), 2)
            current_guess = round(current_guess, 2)
            print(f"count={count} next_delta={str(next_delta)}")
            if abs(last_guess - current_guess) < 0.02:
                close_enough = True
            last_guess = current_guess
        # Give it a small bump down to increase the odds that it will be partially filled
        self.best_guess = round(current_guess * 0.999995, 2)
        print(f"self.best_guess={self.best_guess} count={str(count)}")
        partial_response = ImmediateOrCancelOrder("sell", "2", self.symbol, str(self.best_guess)).execute()
        fields = ['executed_amount', 'avg_execution_price', 'remaining_amount', 'original_amount',
                  'is_cancelled', 'result', 'reason', 'message']
        for field in fields:
            if field in partial_response:
                print(f"{field}={partial_response[field]}")
        assert partial_response['is_cancelled'], "PartialSell should be cancelled but wasn't."
        assert float(partial_response['execution_amount']) > 0.0, \
            f"Incorrect execution amount: {partial_response['execution_amount']}"
        print("done with PartialSell")

    def testImmediateOrCancelWithNegativePrice(self):
        """Verify that sells with a negative price give an error."""
        order = ImmediateOrCancelOrder("sell", self.amount, self.symbol, "-1")
        ErrorResponse(order.execute()).verify("InvalidPrice")

    def testImmediateOrCancelWithZeroPrice(self):
        """Verify that sells with a zero price give an error."""
        order = ImmediateOrCancelOrder("sell", self.amount, self.symbol, "0")
        ErrorResponse(order.execute()).verify("InvalidPrice")

    @classmethod
    def setUpClass(cls):
        print("Let's get going! We'll pretend we are starting a new session.")

    @classmethod
    def tearDownClass(cls):
        print("Finished! We'll pretend we cancelled all open orders and closed the session.")


if __name__ == '__main__':
    unittest.main()
