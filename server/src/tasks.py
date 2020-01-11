import os

from server.src.auditing import AuditLog
from server.src.celery import celery
# from server.src.datamanagement.git import push_to_origin, commit_file
from server.src.messaging import NotificationService
import boto3
# @celery.task(queue="communication")
# def push_to_origin_task():
#     push_to_origin()
#     print("Sent to origin")


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


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

    # Calls test('world') every 30 seconds
    sender.add_periodic_task(30.0, long_poll_sns.s(), expires=10)


@celery.task(queue="periodic")
def long_poll_sns():
    # Create SQS client
    sqs = boto3.client('sqs')

    queue_url = 'https://sqs.eu-west-2.amazonaws.com/519411350235/BratAnnotationsQueue'

    # Long poll for message on provided SQS queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        WaitTimeSeconds=20
    )
    print(f"Long Poll Complete - {response}")



# @celery.task(queue="internal")
# def _git_commit_task(user, relative_path):
#     commit_file(user=user, relative_path=relative_path)
#     print(f"committed file - {relative_path}")
#     push_to_origin_task.delay()
#
# def git_commit_task(collection, document, user):
#     document_path = os.path.join(collection, document)
#     relative_path = "{}.ann".format(document_path.lstrip("/"))
#     _git_commit_task.delay(user, relative_path)