import json
import os
from typing import Any, Dict

import boto3

_sqs = boto3.client("sqs", region_name=os.environ.get("AWS_REGION", "us-east-1"))


def enqueue_job(queue_url: str, job: Dict[str, Any]) -> None:
    body = json.dumps(job, ensure_ascii=False)
    _sqs.send_message(QueueUrl=queue_url, MessageBody=body)

