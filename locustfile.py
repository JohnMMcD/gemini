from order import *
# from response import *
import time
from locust import HttpUser, task, between

index_url = "/"
admin_url = "/wp-admin/"
# the full url is https://s-ql6tlwtx8b8al.eu1.wpsandbox.org/page-1/ - see
# the run_locust.cmd batch file for the URL used to pre-fill the protocol, host, and port.
page_url = "/page-"


class NewOrder(HttpUser):
    wait_time = between(1, 10)

    @task(1)
    def view_item(self):

        for item_id in range(1, 2):
            order = FillOrKillOrder("buy", "1.0", "btcusd", "16000")
            headers = order.get_headers(order.get_payload())
            self.client.post(url=f"{order.ENDPOINT}", data=None, headers=headers)

            time.sleep(2)

    def on_start(self):
        pass
        # self.client.post("/login", json={"username": "foo", "password": "bar"})
