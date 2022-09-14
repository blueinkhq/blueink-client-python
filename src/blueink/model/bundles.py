import random
import string
from typing import List, Optional
from pydantic import BaseModel, validator, EmailStr

from ..constants import DELIVER_VIA, FIELD_KIND


class ValidationError(RuntimeError):
    def __init__(self, error_text: str):
        super(ValidationError, self).__init__(error_text)


def generate_key(type, length=5):
    slug = ''.join(random.choice(string.ascii_letters) for i in range(length))
    return f'{type}_{slug}'


class Field(BaseModel):
    kind: str = ...
    key: str = ...
    x: int = ...
    y: int = ...
    w: int = ...
    h: int = ...
    label: Optional[str]
    page: Optional[int]
    v_pattern: Optional[int]
    v_min: Optional[int]
    v_max: Optional[int]
    editors: Optional[List[str]]

    class Config:
        extra = 'allow'

    @classmethod
    def create(cls, x, y, w, h, page, kind, key=None, **kwargs):
        if not key:
            key = generate_key('field', 5)
        obj = Field(key=key,
                    x=x,
                    y=y,
                    w=w,
                    h=h,
                    page=page,
                    kind=kind,
                    **kwargs)
        return obj

    @validator('kind')
    def kind_is_allowed(cls, v):
        assert v in FIELD_KIND.values(), f'Field Kind \'{v}\' not allowed. Must be one of {FIELD_KIND.values()}'
        return v

    def add_editor(self, editor: str):
        if self.editors is None:
            self.editors = []
        self.editors.append(editor)


class Packet(BaseModel):
    key: str = ...
    name: str = ...
    email: Optional[EmailStr]
    phone: Optional[str]
    auth_sms: Optional[bool]
    auth_selfie: Optional[bool]
    auth_id: Optional[bool]
    deliver_via: Optional[str]
    person_id: Optional[str]
    order: Optional[str]

    class Config:
        extra = 'allow'

    @validator('deliver_via')
    def deliver_via_is_allowed(cls, v):
        if v is not None:
            assert v in DELIVER_VIA.values(), f'deliver_via \'{v}\' not allowed. Must be None' \
                                              f' or one of {DELIVER_VIA.values()}'
        return v

    @classmethod
    def create(cls, name, key=None, **kwargs):
        if not key:
            key = generate_key('packet', 5)
        obj = Packet(key=key,
                     name=name,
                     **kwargs)
        return obj


class TemplateRefAssignment(BaseModel):
    role: str = ...
    signer: str = ...

    class Config:
        extra = 'allow'

    @classmethod
    def create(cls, role, signer, **kwargs):
        obj = TemplateRefAssignment(role=role,
                                    signer=signer,
                                    **kwargs)
        return obj


class TemplateRefFieldValue(BaseModel):
    key: str = ...
    initial_value: str = ...

    class Config:
        extra = 'allow'

    @classmethod
    def create(cls, key, initial_value, **kwargs):
        obj = TemplateRefFieldValue(key=key,
                                    initial_value=initial_value,
                                    **kwargs)
        return obj


class TemplateRef(BaseModel):
    template_id: Optional[str]
    assignments: Optional[List[TemplateRefAssignment]]
    field_values: Optional[List[TemplateRefFieldValue]]

    class Config:
        extra = 'allow'

    @classmethod
    def create(cls, key=None, **kwargs):
        if not key:
            key = generate_key('tmpl', 5)
        obj = TemplateRef(key=key, **kwargs)
        return obj

    def add_assignment(self, assignment: TemplateRefAssignment):
        if self.assignments is None:
            self.assignments = []
        self.assignments.append(assignment)

    def add_field_value(self, field_value: TemplateRefFieldValue):
        if self.field_values is None:
            self.field_values = []
        self.field_values.append(field_value)


class Document(BaseModel):
    key: str = ...

    # document related
    file_url: Optional[str]
    file_index: Optional[int]
    fields: Optional[List[Field]]

    class Config:
        extra = 'allow'

    @classmethod
    def create(cls, key=None, **kwargs):
        if not key:
            key = generate_key('doc', 5)
        obj = Document(key=key, **kwargs)
        return obj

    def add_field(self, field: Field):
        if self.fields is None:
            self.fields = []
        self.fields.append(field)

    def add_assignment(self, assignment: TemplateRefAssignment):
        if self.assignments is None:
            self.assignments = []
        self.assignments.append(assignment)


class Bundle(BaseModel):
    packets: List[Packet] = ...
    documents: List[Document] = ...
    label: Optional[str]
    in_order: Optional[bool]
    email_subject: Optional[str]
    email_message: Optional[str]
    cc_emails: Optional[List[EmailStr]]
    is_test: Optional[bool]
    custom_key: Optional[str]
    team: Optional[str]

    class Config:
        extra = 'allow'

    @classmethod
    def create(cls, packets: List[Packet], documents: List[Document], **kwargs):
        obj = Bundle(packets=packets,
                     documents=documents,
                     **kwargs)
        return obj

    def add_packet(self, packet: Packet):
        if self.packets is None:
            self.packets = []
        self.packets.append(packet)

    def add_document(self, document: Document):
        if self.documents is None:
            self.documents = []
        self.documents.append(document)


