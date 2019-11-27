from .celery import celery
from .messaging import NotificationService
from .auditing import AuditLog


@celery.task()
def _log_event(user, action, *args, **kwargs):
    print(f"logging user - {user}, action - {action}")
    AuditLog.log_event(user, action, *args, **kwargs)

def log_event(user, action, *args, **kwargs):
    task = _log_event.delay(user, action, *args, **kwargs)
    json_dic = {
        'task_id': task.id,
    }
    return json_dic

@celery.task()
def _send_document_done_notification(collection, document, user):
    print(f"document done user - {user} collection - {collection} document - {document}")
    NotificationService.send_document_done_notification(collection, document, user)

def send_document_done_notification(collection, document, user):
    task = _send_document_done_notification.delay(collection, document, user)
    json_dic = {
        'task_id': task.id,
    }
    return json_dic
