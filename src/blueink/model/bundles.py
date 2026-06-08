import random
import string
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from blueink.constants import DELIVER_VIA, FIELD_KIND


class ValidationError(RuntimeError):
    def __init__(self, error_text: str):
        super(ValidationError, self).__init__(error_text)


def generate_key(type, length=5):
    slug = "".join(random.choice(string.ascii_letters) for i in range(length))
    return f"{type}_{slug}"


class AutoPlacement(BaseModel):
    """Model for auto-placement fields that automatically find and place fields on documents"""

    model_config = ConfigDict(extra="allow")

    kind: str
    search: str
    w: int
    h: int
    offset_x: Optional[int] = 0
    offset_y: Optional[int] = 0
    editors: Optional[List[str]] = None
    page: Optional[int] = None
    v_attachment_types: Optional[List[str]] = None

    @classmethod
    def create(
        cls,
        kind: str,
        search: str,
        w: int,
        h: int,
        offset_x: int = 0,
        offset_y: int = 0,
        **kwargs,
    ):
        """Create an AutoPlacement instance

        Args:
            kind: Field type (e.g., 'sig', 'inp', 'ini', etc.)
            search: Text to search for in the document
            w: Width of the field
            h: Height of the field
            offset_x: Horizontal offset from the search text (default: 0)
            offset_y: Vertical offset from the search text (default: 0)
            **kwargs: Additional parameters like editors, page, etc.

        Returns:
            AutoPlacement instance
        """
        obj = AutoPlacement(
            kind=kind,
            search=search,
            w=w,
            h=h,
            offset_x=offset_x,
            offset_y=offset_y,
            **kwargs,
        )
        return obj

    @field_validator("kind")
    @classmethod
    def kind_is_allowed(cls, v):
        assert (
            v in FIELD_KIND.values()
        ), f"AutoPlacement Kind '{v}' not allowed. Must be one of {FIELD_KIND.values()}"
        return v

    def add_editor(self, editor: str):
        if self.editors is None:
            self.editors = []
        self.editors.append(editor)


class Field(BaseModel):
    model_config = ConfigDict(extra="allow")

    kind: str
    key: str
    x: int
    y: int
    w: int
    h: int
    label: Optional[str] = None
    page: Optional[int] = None
    v_pattern: Optional[int] = None
    v_min: Optional[int] = None
    v_max: Optional[int] = None
    v_regex: Optional[str] = None
    v_regex_msg: Optional[str] = None
    editors: Optional[List[str]] = None
    v_attachment_types: Optional[List[str]] = None

    @classmethod
    def create(cls, x, y, w, h, page, kind, key=None, **kwargs):
        if not key:
            key = generate_key("field", 5)
        obj = Field(key=key, x=x, y=y, w=w, h=h, page=page, kind=kind, **kwargs)
        return obj

    @field_validator("kind")
    @classmethod
    def kind_is_allowed(cls, v):
        assert (
            v in FIELD_KIND.values()
        ), f"Field Kind '{v}' not allowed. Must be one of {FIELD_KIND.values()}"
        return v

    def add_editor(self, editor: str):
        if self.editors is None:
            self.editors = []
        self.editors.append(editor)


class Packet(BaseModel):
    model_config = ConfigDict(extra="allow")

    key: str
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    auth_sms: Optional[bool] = None
    auth_selfie: Optional[bool] = None
    auth_id: Optional[bool] = None
    deliver_via: Optional[str] = None
    person_id: Optional[str] = None
    order: Optional[str] = None

    @field_validator("deliver_via")
    @classmethod
    def deliver_via_is_allowed(cls, v):
        if v is not None:
            assert v in DELIVER_VIA.values(), (
                f"deliver_via '{v}' not allowed. Must be None"
                f" or one of {DELIVER_VIA.values()}"
            )
        return v

    @classmethod
    def create(cls, name, key=None, **kwargs):
        if not key:
            key = generate_key("packet", 5)
        obj = Packet(key=key, name=name, **kwargs)
        return obj


class TemplateRefAssignment(BaseModel):
    model_config = ConfigDict(extra="allow")

    role: str
    signer: str

    @classmethod
    def create(cls, role, signer, **kwargs):
        obj = TemplateRefAssignment(role=role, signer=signer, **kwargs)
        return obj


class TemplateRefFieldValue(BaseModel):
    model_config = ConfigDict(extra="allow")

    key: str
    initial_value: str

    @classmethod
    def create(cls, key, initial_value, **kwargs):
        obj = TemplateRefFieldValue(key=key, initial_value=initial_value, **kwargs)
        return obj


class EnvelopeTemplateFieldValue(BaseModel):
    """Model for field values in envelope templates"""

    model_config = ConfigDict(extra="allow")

    key: str
    initial_value: str

    @classmethod
    def create(cls, key, initial_value, **kwargs):
        obj = EnvelopeTemplateFieldValue(key=key, initial_value=initial_value, **kwargs)
        return obj


class EnvelopeTemplate(BaseModel):
    """Model for envelope template reference"""

    model_config = ConfigDict(extra="allow")

    template_id: str
    field_values: Optional[List[EnvelopeTemplateFieldValue]] = None

    @classmethod
    def create(cls, template_id, field_values=None, **kwargs):
        obj = EnvelopeTemplate(
            template_id=template_id, field_values=field_values, **kwargs
        )
        return obj

    def add_field_value(self, field_value: EnvelopeTemplateFieldValue):
        if self.field_values is None:
            self.field_values = []
        self.field_values.append(field_value)


class TemplateRef(BaseModel):
    model_config = ConfigDict(extra="allow")

    template_id: Optional[str] = None
    assignments: Optional[List[TemplateRefAssignment]] = None
    field_values: Optional[List[TemplateRefFieldValue]] = None

    @classmethod
    def create(cls, key=None, **kwargs):
        if not key:
            key = generate_key("tmpl", 5)
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
    model_config = ConfigDict(extra="allow")

    key: str

    # document related
    file_url: Optional[str] = None
    filename: Optional[str] = None
    file_b64: Optional[str] = None
    file_html: Optional[str] = None
    file_index: Optional[int] = None
    fields: Optional[List[Field]] = None
    auto_placements: Optional[List[AutoPlacement]] = None
    html_fields_mode: Optional[str] = None

    @classmethod
    def create(cls, key=None, **kwargs):
        if not key:
            key = generate_key("doc", 5)
        obj = Document(key=key, **kwargs)
        return obj

    def add_field(self, field: Field):
        if self.fields is None:
            self.fields = []
        self.fields.append(field)

    def add_auto_placement(self, auto_placement: AutoPlacement):
        """Add an auto-placement to this document

        Args:
            auto_placement: AutoPlacement instance to add
        """
        if self.auto_placements is None:
            self.auto_placements = []
        self.auto_placements.append(auto_placement)

    def add_assignment(self, assignment: TemplateRefAssignment):
        if self.assignments is None:
            self.assignments = []
        self.assignments.append(assignment)


class Bundle(BaseModel):
    model_config = ConfigDict(extra="allow")

    packets: List[Packet]
    documents: List[Document]
    label: Optional[str] = None
    in_order: Optional[bool] = None
    email_subject: Optional[str] = None
    email_message: Optional[str] = None
    cc_emails: Optional[List[EmailStr]] = None
    is_test: Optional[bool] = None
    custom_key: Optional[str] = None
    team: Optional[str] = None
    signing_brand: Optional[str] = None

    @classmethod
    def create(cls, packets: List[Packet], documents: List[Document], **kwargs):
        obj = Bundle(packets=packets, documents=documents, **kwargs)
        return obj

    def add_packet(self, packet: Packet):
        if self.packets is None:
            self.packets = []
        self.packets.append(packet)

    def add_document(self, document: Document):
        if self.documents is None:
            self.documents = []
        self.documents.append(document)
