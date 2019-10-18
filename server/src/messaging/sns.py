import os

from boto3 import client, resource

from config import AWS_CREDENTIALS, AWS_SNS_QUEUE

class _Queue:
    def __init__(self):
        self._client = client('sqs', **AWS_CREDENTIALS)
        self._resource = client('sqs', **AWS_CREDENTIALS)

    def send_document_done_notification(self, collection, document, user):
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

        response = self._client.send_message(**message_kwargs)
        json_dic = {
            'mesage_id': response["MessageId"],
        }
        return json_dic

Queue = _Queue()
