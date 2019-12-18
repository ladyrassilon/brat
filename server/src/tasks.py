import os

from server.src.auditing import AuditLog
from server.src.celery import celery
from server.src.data.git import push_to_origin, commit_file
from server.src.messaging import NotificationService

@celery.task(queue="communication")
def push_to_origin_task():
    push_to_origin()
    print("Sent to origin")


@celery.task(queue="communication")
def _log_event(user, action, *args, **kwargs):
    print(f"logging user - {user}, action - {action}")
    AuditLog.log_event(user, action, *args, **kwargs)


def log_event(user, action, *args, **kwargs):
    task = _log_event.delay(user, action, *args, **kwargs)
    json_dic = {
        'task_id': task.id,
    }
    return json_dic


@celery.task(queue="communication")
def _send_document_done_notification(collection, document, user):
    print(f"document done user - {user} collection - {collection} document - {document}")
    NotificationService.send_document_done_notification(collection, document, user)


def send_document_done_notification(collection, document, user):
    task = _send_document_done_notification.delay(collection, document, user)
    json_dic = {
        'task_id': task.id,
    }
    return json_dic

@celery.task(queue="internal")
def _git_commit_task(user, relative_path):
    commit_file(user=user, relative_path=relative_path)
    print(f"committed file - {relative_path}")
    push_to_origin_task.delay()

def git_commit_task(collection, document, user):
    document_path = os.path.join(collection, document)
    relative_path = "{}.ann".format(document_path.lstrip("/"))
    _git_commit_task.delay(user, relative_path)