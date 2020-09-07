from order import *
import unittest


class Test1(unittest.TestCase):
    amount = "0.01"
    symbol = "btcusd"
    buy_price = "16000"
    sell_price = "1.01"

    def testFillOrKillBuyWithHighPrice(self):
        order = FillOrKillOrder("buy", self.amount, self.symbol, self.buy_price)
        ExecutedInFullResponse(order.execute()).verify(order)

    def testFillOrKillSellWithLowPrice(self):
        order = FillOrKillOrder("sell", self.amount, self.symbol, self.sell_price)
        ExecutedInFullResponse(order.execute()).verify(order)

    def testFillOrKillBuyWithLowPrice(self):
        order = FillOrKillOrder("buy", self.amount, self.symbol, self.sell_price)
        CancelledInFullResponse(order.execute()).verify("FillOrKillWouldNotFill")

    def testFillOrKillSellWithHighPrice(self):
        order = FillOrKillOrder("sell", self.amount, self.symbol, self.buy_price)
        CancelledInFullResponse(order.execute()).verify("FillOrKillWouldNotFill")

    def testFillOrKillWithNegativePrice(self):
        order = FillOrKillOrder("sell", self.amount, self.symbol, "-1")
        ErrorResponse(order.execute()).verify("InvalidPrice")

    def testFillOrKillWithZeroPrice(self):
        order = FillOrKillOrder("sell", self.amount, self.symbol, "0")
        ErrorResponse(order.execute()).verify("InvalidPrice")

    def testOneLineFillOrKillWithInvalidPrice(self):
        ErrorResponse(FillOrKillOrder("sell", self.amount, self.symbol, "-1").execute()).verify("InvalidPrice")


    @classmethod
    def setUpClass(cls):
        print("Let's get going! We'll pretend we are starting a new session.")

    @classmethod
    def tearDownClas(cls):
        print("Fini! We'll pretend we cancelled all open orders and closed the session.")


if __name__ == '__main__':
    unittest.main()
