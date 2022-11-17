from typing import List

from src.blueink.model.webhook import WebhookExtraHeader
from src.blueink.subclients.subclient import SubClient


class WebhookSubClient(SubClient):
    def __init__(self, base_url, private_api_key):
        super().__init__(base_url, private_api_key)

    # ----------
    # Webhooks
    # ----------
    def create_webhook(
        self,
        url: str,
        event_types: List[str],
        extra_headers: List[WebhookExtraHeader],
        enabled: bool = True,
        json: bool = True,
    ):
        raise RuntimeError("Not Implemented")

    def list_webhooks(self):
        raise RuntimeError("Not Implemented")

    def retrieve_webhook(self, webhook_id: str):
        raise RuntimeError("Not Implemented")

    def delete_webhook(self, webhook_id: str):
        raise RuntimeError("Not Implemented")

    def update_webhook(self, webhook_id: str, **data):
        raise RuntimeError("Not Implemented")

    # ----------
    # Extra Header
    # ----------
    def create_header(self, webhook_id: str, name: str, value: str, order: int):
        raise RuntimeError("Not Implemented")

    def list_headers(self):
        raise RuntimeError("Not Implemented")

    def retrieve_header(self, header_id: str):
        raise RuntimeError("Not Implemented")

    def delete_header(self, header_id: str):
        raise RuntimeError("Not Implemented")

    def update_header(self, header_id: str, **data):
        raise RuntimeError("Not Implemented")

    # ----------
    # Events
    # ----------
    def list_events(self):
        raise RuntimeError("Not Implemented")

    def retrieve_event(self, event_id: str):
        raise RuntimeError("Not Implemented")

    # ----------
    # Deliveries
    # ----------
    def list_deliveries(self):
        raise RuntimeError("Not Implemented")

    def retrieve_delivery(self, event_id: str):
        raise RuntimeError("Not Implemented")

    # ----------
    # Secret
    # ----------
    def retrieve_secret(self):
        raise RuntimeError("Not Implemented")

    def regenerate_secret(self):
        raise RuntimeError("Not Implemented")
