import random
from locust import HttpUser, task, between  # <--- THIS IS THE FIX

class OrderUser(HttpUser):
    # This is the DNS name of your load balancer.
    # Make sure to add "http://"
    host = "http://assignment-alb-809509990.us-west-2.elb.amazonaws.com"

    # User wait time: random 100-500ms between requests
    wait_time = between(0.1, 0.5)

    # This is the "order" payload we'll send
    def get_order_payload(self):
        return {
            "customer_id": random.randint(1, 1000),
            "items": [
                {"item_id": "item-a", "quantity": random.randint(1, 3)},
                {"item_id": "item-b", "quantity": random.randint(1, 2)}
            ]
        }

    # This is the task for Phase 1
    @task(10) # 10 means this task is 10x more likely to be run
    def post_sync_order(self):
        self.client.post("/orders/sync", json=self.get_order_payload())

    # We'll use this task in Phase 3
    @task(1) # 1 means this task is less likely (we'll change this later)
    def post_async_order(self):
        # For now, we'll just ignore this one
        pass