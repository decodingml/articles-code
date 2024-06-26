import datetime
import re
from typing import List

import boto3

_client = boto3.client('logs')


def monitor(correlation_ids: List[str]):
    finished = []

    now = int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp() * 1000)

    response = _client.filter_log_events(
        logGroupName='/aws/lambda/pi-prod-profiles-crawler',
        startTime=now,
        filterPattern="REPORT RequestId"
    )

    for event in response['events']:
        if match := re.search(r'REPORT RequestId: ([^\s]+)', event.get('message')):
            correlation_id = match.group(1)
            if correlation_id in correlation_ids:
                finished.append(correlation_id)

    return finished
