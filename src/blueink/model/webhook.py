from typing import List, Optional
from pydantic import BaseModel, validator


class WebhookExtraHeaderSchema(BaseModel):
    id: str
    webhook: str
    name: str
    value: str
    order: int


class WebhookSchema(BaseModel):
    id: str
    url: str
    enabled: bool
    json: bool
    event_types: List[str]
    extra_header: Optional[List[WebhookExtraHeaderSchema]]
