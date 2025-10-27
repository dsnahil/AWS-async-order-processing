import random
from locust import HttpUser, task, between

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

    # This is the task for Phase 1 - NOW DISABLED
    @task(0) # Set weight to 0 to disable this task
    def post_sync_order(self):
        # We are skipping this now
        pass

    # This is the task for Phase 3 - NOW ENABLED
    @task(10) # Set weight to 10 to make this the primary task
    def post_async_order(self):
        # This is the new active task, hitting the async endpoint
        self.client.post("/orders/async", json=self.get_order_payload())
