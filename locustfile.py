from locust import HttpLocust, TaskSet, task, between
import numpy as np

fimage = "/home/pavanmv/Pictures/p3.jpg"
    
class UserBehavior(TaskSet):
    @task
    def register_user(self):
        payload = {
                    "groupUUID": "bce46197f396486aa6929697f5bb7633",
                }
        files = [
            ("input_files", open(fimage, "rb")),
            # ("input_files", img_for_post),
        ]
        self.client.post('face/identify', data=payload, files=files)
        
class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    wait_time = between(0.5,5)