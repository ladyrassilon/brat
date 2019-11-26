import os

from boto3 import client, resource

from ..celery import celery
from config import AWS_CREDENTIALS, AWS_SNS_QUEUE

sns_client = client('sqs', **AWS_CREDENTIALS)
sns_resource = client('sqs', **AWS_CREDENTIALS)

class NotificationService:

    @celery.task()
    def _send_document_done_notification(collection, document, user):
        document_path = os.path.join(collection, document)
        message_attributes = {
            "User": {
                "DataType": "String",
                "StringValue" : user,
            },
            "Collection":  {
                "DataType": "String",
                "StringValue" : collection,
            },
            "Document":  {
                "DataType": "String",
                "StringValue" : document,
            },
            "DocumentPath":  {
                "DataType": "String",
                "StringValue" : document_path,
            },
        }

        message_body = f"""
        User: {user}
        File: {document_path}
        """
        message_kwargs = {
            "QueueUrl": AWS_SNS_QUEUE,
            "DelaySeconds": 0,
            "MessageAttributes": message_attributes,
            "MessageBody": message_body,
        }

        response = sns_client.send_message(**message_kwargs)

    @classmethod
    def send_document_done_notification(cls, collection, document, user):
        task = cls._send_document_done_notification.delay(collection, document, user)
        json_dic = {
            'task_id': task.id,
        }
        return json_dic
