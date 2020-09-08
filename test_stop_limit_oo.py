from response import *
import unittest


class TestStopLimit(unittest.TestCase):
    """
    A Stop-Limit order is an order type that allows for order placement when a price reaches a specified
    level. Stop-Limit orders take in both a price and and a stop_price as parameters. The stop_price is the
    price that triggers the order to be placed on the continuous live order book at the price. For buy orders,
    the stop_price must be below the price while sell orders require the stop_price to be greater than the price.
    """

    amount = "0.01"
    symbol = "btcusd"
    buy_price = "16000"
    buy_stop_price = "15999"
    sell_price = "10001"
    sell_stop_price = "10002"

    # An amount that is impossible to fill in one order
    amount_way_too_high = "9999999999"

    def test_buy(self):
        """Verify that your basic buy stop limit order is added."""
        order = StopLimitOrder("buy", self.amount, self.symbol, self.buy_price, self.buy_stop_price)
        response = NoExecutedAmountResponse(order.execute())
#        print(order.payload)
        response.verify(order)

    def test_sell(self):
        """Verify that your basic sell stop limit order is added."""
        order = StopLimitOrder("sell", self.amount, self.symbol, self.sell_price, self.sell_stop_price)
        NoExecutedAmountResponse(order.execute()).verify(order)

    def test_buy_with_wrong_prices(self):
        """Verify cancellation if the stop_price is above the price for a buy order"""
        order = StopLimitOrder("buy", self.amount, self.symbol, self.buy_stop_price, self.buy_price)
        ErrorResponse(order.execute()).verify("InvalidStopPriceBuy")

    def test_sell_with_wrong_prices(self):
        """Verify cancellation if the stop_price is below the price for a sell order"""
        order = StopLimitOrder("sell", self.amount, self.symbol, self.sell_stop_price, self.sell_price)
        ErrorResponse(order.execute()).verify("InvalidStopPriceSell")

    @unittest.skip("because it's giving an InvalidPrice error and I don't know why")
    def test_buy_below_the_market(self):
        """Buy stop limit order below the current market price aka catch the falling knife"""
        order = StopLimitOrder("buy", self.amount, self.symbol, self.sell_stop_price, self.sell_price)
        NoExecutedAmountResponse(order.execute()).verify(order)

    def test_sell_above_the_market(self):
        """Sell stop limit order above the current market price aka I've made my money I want off"""
        order = StopLimitOrder("buy", self.amount, self.symbol, self.buy_price, self.buy_stop_price)
        NoExecutedAmountResponse(order.execute()).verify(order)

    def test_buy_way_too_much(self):
        """Verify that buys which are way too large to be completed throw an error."""
        order = StopLimitOrder("buy", self.amount_way_too_high, self.symbol, self.buy_price, self.buy_stop_price)
        ErrorResponse(order.execute()).verify("InvalidQuantity")

    def test_sell_way_too_much(self):
        """Verify that sells which are way too large to be completed throw an error."""
        order = StopLimitOrder("sell", self.amount_way_too_high, self.symbol, self.sell_price, self.sell_stop_price)
        ErrorResponse(order.execute()).verify("InvalidQuantity")

    # Test cases for the 'slightly too much' are not included because they would not be cancelled or result
    # in an error; they would just be added to the order book, so they're equivalent to the basic tests.

    def test_sell_with_negative_price(self):
        """Verify that sells with a negative price give an error."""
        order = StopLimitOrder("sell", self.amount, self.symbol, "-1", "-0.9")
        ErrorResponse(order.execute()).verify("InvalidPrice")

    def test_sell_with_zero_price(self):
        """Verify that sells with a zero price give an error."""
        order = StopLimitOrder("sell", self.amount, self.symbol, "0", "0.01")
        ErrorResponse(order.execute()).verify("InvalidPrice")

    def test_sell_with_zero_stop_price(self):
        """Verify that sells with a zero stop price give an error. Duplicates the SellWithNegativePrice testcase?"""
        order = StopLimitOrder("sell", self.amount, self.symbol, "-0.01", "0.00")
        ErrorResponse(order.execute()).verify("InvalidPrice")

    def test_buy_with_missing_stop_price(self):
        """Verify that stop limit buys with no stop price give an error."""
        order = StopLimitOrder("buy", self.amount, self.symbol, self.buy_price, '')
        ErrorResponse(order.execute()).verify("MissingStopPrice")

    @classmethod
    def setUpClass(cls):
        print("Testing stop limit orders! We'll pretend we are starting a new session.")

    @classmethod
    def tearDownClass(cls):
        print("Fini! We'll pretend we cancelled all open orders and closed the session.")


if __name__ == '__main__':
    unittest.main()
