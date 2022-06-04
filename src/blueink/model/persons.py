from pydantic import BaseModel, EmailStr
from typing import Optional, List


class ContactChannelSchema(BaseModel):
    email: Optional[EmailStr]
    phone: Optional[str]
    kind: Optional[str]

    class Config:
        extra = 'allow'


class PersonSchema(BaseModel):
    name: Optional[str]
    metadata: Optional[dict]
    channels: Optional[List[ContactChannelSchema]]

    class Config:
        extra = 'allow'


