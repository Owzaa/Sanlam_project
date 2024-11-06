import json
import logging
import boto3
from tenacity import retry, stop_after_attempt, wait_fixed


# Configured logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WithdrawalEvent:
    def __init__(self, amount, account_id, status):
        self.amount = amount
        self.account_id = account_id
        self.status = status

    def to_json(self):
        return json.dumps({
            "amount": str(self.amount),
            "accountId": self.account_id,
            "status": self.status
        })

class WithdrawalEventPublisher:
    def __init__(self, sns_topic_arn):
        self.sns_client = boto3.client('sns')
        self.sns_topic_arn = sns_topic_arn

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def publish_withdrawal_event(self, event):
        event_json = event.to_json()
        response = self.sns_client.publish(
            TopicArn=self.sns_topic_arn,
            Message=event_json
        )
        logger.info(f"Published event successfully: {response['MessageId']}")


if __name__ == "__main__":
    sns_topic_arn = "sns-topic-arn"
    publisher = WithdrawalEventPublisher(sns_topic_arn)
    
    withdrawal_event = WithdrawalEvent(amount=100.00, account_id=12345, status="COMPLETED")
    try:
        publisher.publish_withdrawal_event(withdrawal_event)
    except Exception as e:
        logger.error(f"Failed to publish event: {e}")