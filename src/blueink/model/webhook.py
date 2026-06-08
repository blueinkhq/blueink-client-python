from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from blueink.constants import EVENT_TYPE


class WebhookExtraHeaderSchema(BaseModel):
    id: Optional[str] = None
    webhook: str
    name: str
    value: str
    order: int


class WebhookSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = None
    url: str
    enabled: bool = True
    json_: bool = Field(default=True, alias="json")
    event_types: List[str]
    extra_headers: Optional[List[WebhookExtraHeaderSchema]] = None

    @field_validator("event_types")
    @classmethod
    def validate_event_types(cls, event_types):
        for event_type in event_types:
            assert event_type in EVENT_TYPE.values(), (
                f"subscription event_type '{event_type}' not allowed. Must be one of "
                f"{EVENT_TYPE.values()}"
            )
        return event_types
