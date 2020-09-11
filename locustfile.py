from order import FillOrKillOrder
import time
from locust import HttpUser, task, between


class NewOrder(HttpUser):
    """
    This is a very simple class that demonstrates how to do load testing in locust.
    # The run_locust.cmd batch file holds the URL used to pre-fill the protocol, host, and port.
    """

    wait_time = between(1, 3)

    @task(1)
    def view_item(self):

        for item_id in range(1, 1):
            order = FillOrKillOrder("buy", "1.0", "btcusd", "16000")
            headers = order.get_headers(order.get_payload())
            self.client.post(url=f"{order.ENDPOINT}", data=None, headers=headers)

            time.sleep(2)

    def on_start(self):
        # This would be a good place to get the credentials to run this as a multi-user test.
        # See https://www.blazemeter.com/blog/how-to-run-locust-with-different-users for one
        # way of doing this.
        pass
