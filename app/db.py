from pymongo import MongoClient
import os
import datetime


db = MongoClient(os.getenv("DBURL")).parser
tasks_collection = db.tasks
STATES = ["CREATED", "IN PROGRESS", "COMPLETED"]


def get_empty_id(collection):
    req = collection.find({}, {"id": 1}).sort("id", -1).limit(1)
    data = list(req)
    if data:
        return data[0]['id'] + 1
    else:
        return 1


class Task:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @staticmethod
    def filter_by(**kwargs):
        query = kwargs
        tasks = tasks_collection.find(query, {"_id": 0})
        return [Task(**task) for task in tasks]

    def create(self):
        data = {
            "date_created": datetime.datetime.utcnow(),
            "id": get_empty_id(tasks_collection),
            "state": STATES[0],
            "web_url": self.web_url,
            "depth": int(self.depth)
        }
        task_id = tasks_collection.insert_one(data).inserted_id
        return self.filter_by(_id=task_id)[0]

    def update(self, state_id):
        query = {
            "id": self.id
        }
        data = {
            "$set": {
                "state": STATES[state_id]
            }
        }
        tasks_collection.update_one(query, data)
        return self.filter_by(id=self.id)

    @staticmethod
    def delete(task_id):
        query = {
            "id": task_id
        }
        tasks_collection.delete(query)
        return None
