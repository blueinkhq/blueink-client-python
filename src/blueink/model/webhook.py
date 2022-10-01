from typing import List, Optional
from pydantic import BaseModel, validator, Field


class WebhookExtraHeaderSchema(BaseModel):
    id: Optional[str]
    webhook: Optional[str]
    name: str
    value: str
    order: int


class WebhookSchema(BaseModel):
    id: Optional[str]
    url: str
    enabled: bool = True
    json_: bool = Field(default=True, alias="json")
    event_types: List[str]
    extra_header: Optional[List[WebhookExtraHeaderSchema]]
