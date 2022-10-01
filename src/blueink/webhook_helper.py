from typing import List

from src.blueink.model.webhook import WebhookSchema, WebhookExtraHeaderSchema


class WebhookHelper:
    def __init__(self,
                 url: str,
                 event_types: List[str] = [],
                 enabled: bool = True,
                 json: bool = True):
        self.url = url
        self.event_types = event_types
        self.enabled = enabled
        self.json = json
        self.extra_headers: List[WebhookExtraHeaderSchema] = []
        self._extraheader_idx = 0

    def add_extra_header(self, name:str, value: str):
        wheh = WebhookExtraHeaderSchema(
            name=name,
            value=value,
            order=self._extraheader_idx
        )
        self.extra_headers.append(wheh)
        self._extraheader_idx = self._extraheader_idx + 1
        return wheh

    def as_data(self, **kwargs):
        webhook_out = WebhookSchema(
            url=self.url,
            enabled=self.enabled,
            json=self.json,
            event_types=self.event_types,
            extra_headers=self.extra_headers,
        )

        out_dict = webhook_out.dict(
            exclude_unset=True,
        )

        # Merge in the additional data
        out_dict = {**out_dict, **kwargs}

        return out_dict
