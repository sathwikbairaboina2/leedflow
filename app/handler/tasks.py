from celery import Celery
from time import sleep

celery_app = Celery(
    "s", backend="redis://localhost:6379/0", broker="redis://localhost:6379/0"
)


@celery_app.task
def run_long_task(iterations):
    result = 0
    for i in range(iterations):
        result += i
        sleep(2)
    return result


def get_task_status(task_id):
    task_result = celery_app.AsyncResult(task_id)  # -line 1
    if task_result.ready():  # -line 2
        if task_result.successful():  # -line 3
            return {
                "ready": task_result.ready(),
                "successful": task_result.successful(),
                "value": task_result.result,  # -line 4
            }
        else:
            return {
                "status": "ERROR",
                "error_message": str(task_result.result),
            }  # -line 5
    else:
        return {"status": "Running"}  # -line 6
