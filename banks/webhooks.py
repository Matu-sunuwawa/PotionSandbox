
import requests
from django.utils.timezone import now

class WebhookService:
    @staticmethod
    def trigger_webhook(account, payload):
        if not account.webhook_url:
            return

        try:
            response = requests.post(
                account.webhook_url,
                json=payload,
                timeout=3
            )
            print(f"Webhook sent to {account.webhook_url}. Status: {response.status_code}")
        except Exception as e:
            print(f"Webhook failed for {account}: {str(e)}")