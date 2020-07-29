from flask import Flask, request, send_file, abort
import os
from app.db import Task
from app.model import TaskSchema
from app.parser import Parser
from celery import Celery
from app.utils import zip_folder


app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = os.getenv("BROKER_URL")
celery = Celery(
    "tasks",
    broker=app.config["CELERY_BROKER_URL"],
)
celery.conf.update(app.config)


@app.route("/", methods=["GET"])
def index():
    return "Hello world!"


@app.route("/tasks/", methods=["POST"])
def add_task():
    data = TaskSchema().loads(request.data)
    task = Task(**data).create()
    parse_website.delay(task.id)
    return TaskSchema().dumps(task), 201


@app.route("/tasks/", methods=["GET"])
def get_tasks():
    tasks = Task.filter_by()
    return TaskSchema().dumps(tasks, many=True), 200


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = Task.filter_by(id=task_id)
    if not task:
        abort(404, "No such task")

    return TaskSchema().dumps(task[0]), 200


@app.route("/files/<int:task_id>", methods=["GET"])
def get_zip(task_id):
    task = Task.filter_by(id=task_id)
    if not task:
        abort(404, "No such task")

    if task[0].state != "COMPLETED":
        abort(400, "File not ready")

    return send_file("./sites/{}.zip".format(task_id)), 200


@celery.task
def parse_website(task_id):
    task = Task.filter_by(id=task_id)[0]
    task.update(1)
    try:
        Parser(task.web_url, task.depth, task.id).parse()
        task.update(2)
        dir = "{}/app/sites/{}".format(
            os.getcwd(),
            task_id
        )
        zip_folder(dir)
    except Exception as e:
        print("Error while parsing site\n{}".format(e))
        task.update(3)


if __name__ == "__main__":
    app.run(debug=True)