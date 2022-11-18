from blueink import endpoints
from blueink.request_helper import NormalizedResponse
from blueink.subclients.subclient import SubClient


class WebhookSubClient(SubClient):
    def __init__(self, base_url, private_api_key):
        super().__init__(base_url, private_api_key)

    # ----------
    # Webhooks
    # ----------
    def create(self, data: dict):
        url = self.build_url(endpoint=endpoints.WEBHOOKS.CREATE)

        return self._requests.post(url, data=data)

    def list(self, **query_params) -> NormalizedResponse:
        url = self.build_url(endpoint=endpoints.WEBHOOKS.LIST)

        return self._requests.get(
            url, params=self.build_params(query_params=query_params)
        )

    def retrieve(self, webhook_id: str) -> NormalizedResponse:
        url = self.build_url(
            endpoint=endpoints.WEBHOOKS.RETRIEVE, webhook_id=webhook_id
        )

        return self._requests.get(url)

    def delete(self, webhook_id: str) -> NormalizedResponse:
        url = self.build_url(endpoint=endpoints.WEBHOOKS.DELETE, webhook_id=webhook_id)

        return self._requests.delete(url)

    def update(self, webhook_id: str, data: dict) -> NormalizedResponse:
        url = self.build_url(endpoint=endpoints.WEBHOOKS.UPDATE, webhook_id=webhook_id)

        return self._requests.patch(url, data=data)

    # ----------
    # Extra Header
    # ----------
    def create_header(self, data: dict) -> NormalizedResponse:
        url = self.build_url(endpoint=endpoints.WEBHOOKS.CREATE_HEADER)

        return self._requests.post(url, data=data)

    def list_headers(self, **query_params) -> NormalizedResponse:
        url = self.build_url(endpoint=endpoints.WEBHOOKS.LIST_HEADERS)

        return self._requests.get(url, params=self.build_params(**query_params))

    def retrieve_header(self, header_id: str) -> NormalizedResponse:
        url = self.build_url(
            endpoint=endpoints.WEBHOOKS.RETRIEVE_HEADER, webhook_header_id=header_id
        )

        return self._requests.get(url)

    def delete_header(self, header_id: str) -> NormalizedResponse:
        url = self.build_url(
            endpoint=endpoints.WEBHOOKS.DELETE_HEADERE, webhook_header_id=header_id
        )

        return self._requests.delete(url)

    def update_header(self, header_id: str, **data) -> NormalizedResponse:
        url = self.build_url(
            endpoint=endpoints.WEBHOOKS.UPDATE_HEADER, webhook_header_id=header_id
        )

        return self._requests.patch(url, data=data)

    # ----------
    # Events
    # ----------
    def list_events(self, **query_params) -> NormalizedResponse:
        url = self.build_url(endpoint=endpoints.WEBHOOKS.LIST_EVENTS)

        return self._requests.get(
            url, params=self.build_params(query_params=query_params)
        )

    def retrieve_event(self, event_id: str) -> NormalizedResponse:
        url = self.build_url(
            endpoint=endpoints.WEBHOOKS.RETRIEVE_EVENT, wehook_event_id=event_id
        )

        return self._requests.get(url)

    # ----------
    # Deliveries
    # ----------
    def list_deliveries(self, **query_params) -> NormalizedResponse:
        url = self.build_url(endpoint=endpoints.WEBHOOKS.LIST_DELIVERIES)

        return self._requests.get(
            url, params=self.build_params(query_params=query_params)
        )

    def retrieve_delivery(self, delivery_id: str) -> NormalizedResponse:
        url = self.build_url(
            endpoint=endpoints.WEBHOOKS.RETRIEVE_DELIVERY,
            webhook_delivery_id=delivery_id,
        )

        return self._requests.get(url)

    # ----------
    # Secret
    # ----------
    def retrieve_secret(self) -> NormalizedResponse:
        url = self.build_url(endpoint=endpoints.WEBHOOKS.RETRIEVE_SECRET)

        return self._requests.get(url)

    def regenerate_secret(self) -> NormalizedResponse:
        url = self.build_url(endpoint=endpoints.WEBHOOKS.REGENERATE_SECRET)

        return self._requests.post(url)
