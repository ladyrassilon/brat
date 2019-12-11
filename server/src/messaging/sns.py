import os

from boto3 import client, resource
from config import AWS_CREDENTIALS, AWS_SNS_TOPIC

from ..celery import celery

sns_client = client('sns', **AWS_CREDENTIALS)

class NotificationService:

    def send_document_done_notification(collection, document, user):
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
        subject = f"{user} finished {document_path}"
        message = f"""
        User: {user}
        File: {document_path}
        """
        message_kwargs = {
            "Subject": subject,
            "TopicArn": AWS_SNS_TOPIC,
            "MessageAttributes": message_attributes,
            "Message": message,
        }
        response = sns_client.publish(
            **message_kwargs
        )

        return response
