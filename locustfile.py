from locust import HttpUser, task, between

class ChattyUser(HttpUser):
    wait_time = between(1, 5)

    @task(2)
    def register_and_login(self):
        username = f"user_{self.client.session.cookies.get('locust_user_id', 'test')}"
        self.client.post("/auth/register", json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "password123"
        })
        response = self.client.post("/auth/login", json={
            "username": username,
            "password": "password123"
        })
        if response.status_code == 200:
            self.token = response.json().get("token", "fake-token")

    @task(3)
    def create_post(self):
        self.client.post("/post/posts", json={
            "title": "Test Post",
            "content": "This is a test post"
        })

    @task(1)
    def subscribe(self):
        self.client.post("/subscription/subscribe/2")

    @task(1)
    def get_feed(self):
        self.client.get("/subscription/feed")

    @task(1)
    def get_recommendations(self):
        self.client.get("/recommendation/recommendations")

    def on_start(self):
        self.register_and_login()
