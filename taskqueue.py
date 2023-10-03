from google.cloud import tasks_v2
from flask import Flask
import json
import datetime

def create_http_task(
    json_payload
) -> tasks_v2.Task:
    
    project = project_name
    location = location
    queue = queue_name
    url = ''
    
    date = datetime.datetime.now()
    date_time = date.strftime("%m/%d/%Y_%H:%M:%S")
    id = ''
    for d in date_time:
        if d.isdigit():
            id+=d
    # Create a client.
    client = tasks_v2.CloudTasksClient()
    # Construct the task.
    task = tasks_v2.Task(
        http_request=tasks_v2.HttpRequest(
            http_method=tasks_v2.HttpMethod.POST,
            url=url,
            headers={"Content-type": "application/json"},
            body=json.dumps(json_payload).encode(),
        ),
        name=(
            client.task_path(project, location, queue, id)
        ),
    )

    return client.create_task(
        tasks_v2.CreateTaskRequest(
            parent=client.queue_path(project, location, queue),
            task=task,
        )
    )
