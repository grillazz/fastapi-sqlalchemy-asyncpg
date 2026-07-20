from locust import HttpUser, between, task


class Stuff(HttpUser):
    wait_time = between(1, 3)

    @task
    def find_stuff(self) -> None:
        self.client.get("/v1/stuff/string")

    @task
    def find_stuff_with_pool(self) -> None:
        self.client.get("/v1/stuff/pool/string")
