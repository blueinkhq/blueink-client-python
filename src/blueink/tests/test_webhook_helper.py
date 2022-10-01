from src.blueink.utils.testcase import TestCase
from src.blueink.webhook_helper import WebhookHelper
from src.blueink.constants import EVENT_TYPE


class TestWebhookHelper(TestCase):
    WEBHOOK_URL = "http://www.example.com/webhook/01/"
    EVENT_TYPES = [
        EVENT_TYPE.EVENT_BUNDLE_LAUNCHED,
        EVENT_TYPE.EVENT_BUNDLE_COMPLETE
    ]

    def test_webhook_creation_all_in_one(self):
        whh = WebhookHelper(url=self.WEBHOOK_URL,
                            event_types=self.EVENT_TYPES)

        self.assert_true(whh.validate())

        data = whh.as_data()

        self.assert_len(data["event_types"], 2)
        self.assert_equal(data["url"], self.WEBHOOK_URL)

