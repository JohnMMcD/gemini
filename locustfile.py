import time
from locust import HttpUser, task, between

index_url = "/"
admin_url = "/wp-admin/"
page_url = "/page-"


class QuickstartUser(HttpUser):
    wait_time = between(1, 10)

    @task
    def index_page(self):
        self.client.get(index_url)

    @task(3)
    def view_item(self):
        for item_id in range(1, 3):
            self.client.get(f"{page_url}{item_id}")
            time.sleep(1)

    def on_start(self):
        pass
        # self.client.post("/login", json={"username": "foo", "password": "bar"})
