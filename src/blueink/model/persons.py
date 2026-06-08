from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List


class ContactChannelSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    kind: Optional[str] = None


class PersonSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: Optional[str] = None
    metadata: Optional[dict] = None
    channels: Optional[List[ContactChannelSchema]] = None
