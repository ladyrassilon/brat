import json
import os

from boto3 import client
from config import (AWS_CREDENTIALS, AWS_SNS_TOPIC, DATA_DIR,
                    SNS_SOURCE_HOSTNAME)

sns_client = client('sns', **AWS_CREDENTIALS)


class NotificationService:

    def send_document_done_notification(collection, document, user):
        document_path = os.path.join(collection, document)
        message_attributes = {
            "Hostname": {
                "DataType": "String",
                "StringValue": SNS_SOURCE_HOSTNAME
            },
            "User": {
                "DataType": "String",
                "StringValue": user,
            },
            "Collection": {
                "DataType": "String",
                "StringValue": collection,
            },
            "Document": {
                "DataType": "String",
                "StringValue": document,
            },
            "DocumentPath": {
                "DataType": "String",
                "StringValue": document_path,
            },
        }

        full_document_path = "{}.ann".format(os.path.join(DATA_DIR, document_path.lstrip("/")))
        print(f"Full document path - {full_document_path}")
        assert (os.path.isfile(full_document_path))

        file_stats = os.stat(full_document_path)
        assert (file_stats.st_size < 204800)

        with open(full_document_path, encoding='utf-8') as document_file:
            document_contents = document_file.read()

        message_dict = {"Properties": message_attributes, "File": document_contents}

        message_body = json.dumps(message_dict)

        subject = f"{user} finished {document_path}"
        message_kwargs = {
            "Subject": subject,
            "TopicArn": AWS_SNS_TOPIC,
            "MessageAttributes": message_attributes,
            "Message": message_body,
        }
        response = sns_client.publish(
            **message_kwargs
        )

        return response
