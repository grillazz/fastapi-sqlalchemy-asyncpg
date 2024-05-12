from locust import HttpUser, task, between


class Stuff(HttpUser):
    wait_time = between(1, 3)

    @task
    def test_find(self):
        self.client.get("/v1/stuff/string")

    @task
    def test_find_pool(self):
        self.client.get("/v1/stuff/pool/string")
