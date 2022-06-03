import io
import random
import string
from typing import List, Optional
from pydantic import BaseModel, validator, EmailStr
from src.blueink.constants import (
    DELIVER_VIA,
    FIELD_KIND, ATTACHMENT_TYPE, BUNDLE_ORDER, BUNDLE_STATUS, PACKET_STATUS, V_PATTERN,
)

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

    @classmethod
    def create(cls, x, y, w, h, page, kind, *args, **kwargs):
        obj = Field(key=generate_key('field', 5),
                    x=x,
                    y=y,
                    w=w,
                    h=h,
                    page=page,
                    kind=kind,
                    data=kwargs)
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

    @validator('deliver_via')
    def deliver_via_is_allowed(cls, v):
        if v is not None:
            assert v in DELIVER_VIA.values(), f'deliver_via \'{v}\' not allowed. Must be None' \
                                              f' or one of {DELIVER_VIA.values()}'
        return v

    @classmethod
    def create(cls, name, **kwargs):
        obj = Packet(key=generate_key('packet', 5),
                     # person_id=str(uuid.uuid4()),
                     name=name,
                     **kwargs)
        return obj


class TemplateRefAssignment(BaseModel):
    role: str = ...
    signer: str = ...

    @classmethod
    def create(cls, role, signer, **kwargs):
        obj = TemplateRefAssignment(role=role,
                                    signer=signer,
                                    **kwargs)
        return obj


class TemplateRefFieldValue(BaseModel):
    key: str = ...
    initial_value: str = ...

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

    @classmethod
    def create(cls,
               *args,
               **kwargs):

        obj = TemplateRefFieldValue(**kwargs)
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

    # template related
    template_id: Optional[str]  # UUID to a valid template, required for Template
    assignments: Optional[List[TemplateRefAssignment]]
    field_values: Optional[List[TemplateRefFieldValue]]

    @classmethod
    def create(cls, **kwargs):
        obj = Document(key=generate_key('doc', 5),
                       **kwargs)
        return obj

    def add_field(self, field: Field):
        if self.fields is None:
            self.fields = []
        self.fields.append(field)

    def add_assignment(self, assignment: TemplateRefAssignment):
        if self.assignments is None:
            self.assignments = []
        self.assignments.append(assignment)

    def add_field_value(self, field_value: TemplateRefFieldValue):
        if self.field_values is None:
            self.field_values = []
        self.field_values.append(field_value)


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
        self.documents.append(Document)


class BundleHelper:
    ATTACHMENT_TYPE = ATTACHMENT_TYPE
    BUNDLE_ORDER = BUNDLE_ORDER
    BUNDLE_STATUS = BUNDLE_STATUS
    DELIVER_VIA = DELIVER_VIA
    FIELD_KIND = FIELD_KIND
    PACKET_STATUS = PACKET_STATUS
    V_PATTERN = V_PATTERN

    def __init__(
        self,
        label: str = None,
        email_subject: str = None,
        email_message: str = None,
        in_order: bool = False,
        is_test: bool = False,
        custom_key: str = None,
        team: str = None,
    ):
        self._label = label
        self._in_order = in_order
        self._email_subj = email_subject
        self._email_msg = email_message
        self._is_test = is_test
        self._cc_emails = []
        self._documents = {}
        self._packets = {}
        self._custom_key = custom_key
        self._team = team

        # for file uploads, index should match those in the document "file_index" field
        self.file_names = []
        self.file_types = []
        self.files = []

    def add_cc(self, email: str):
        self._cc_emails.append(email)
        return self

    def add_document_by_url(self, url: str) -> Document:
        """
        Add a document via url.
        :param url:
        :return: Document instance
        """
        document = Document.create(file_url=url)
        self._documents[document.key] = document
        return document

        self._documents[key] = Document(key, url=url)
        return key

    def add_document_by_file(self, file:io.BufferedReader, file_name:str, mime_type:str) -> str:
        '''
        Add a document via url, with unique key.
        :param file:
        :param key:
        :param url:
        :return:
        '''

        file_index = len(self.files)

        if type(file) == io.BufferedReader and file.readable():
            self.files.append(file)
            self.file_names.append(file_name)
            self.file_types.append(mime_type)
            print(f"Attaching file {file_index}: {file_name}")
        else:
            raise RuntimeError(f"File unreadable.")
        document = Document.create(file_index=file_index)
        self._documents[document.key] = document
        return document

    def add_document_by_path(self, file_path: str, mime_type: str) -> Document:
        """
        Add a document via url, returns generated unique key.
        :param file_path:
        :return: Document instance
        """

        file = open(file_path, 'rb')
        return self.add_document_by_file(file, file.name, mime_type)

    def add_document_by_bytearray(self, byte_array: bytearray, file_name: str, mime_type: str) -> Document:
        '''
        Add a document via url, with unique key.
        :param byte_array:
        :param file_name:
        :param mime_type:
        :return:
        '''

        bytes = io.BytesIO(byte_array)
        file = io.BufferedReader(bytes, len(byte_array))
        return self.add_document_by_file(file, file_name, mime_type)

    def add_document_template(self, template_id: str):
        """
        Create and add a template reference
        :param template_id:
        :return:Template object
        """
        if template_id in self._documents.keys():
            raise RuntimeError(f'Document/Template with id {template_id} already added.')

        template = TemplateRef(template_id=template_id)
        self._documents[template_id] = template
        return template

    def add_field(self, document: Document, x: int, y: int, w: int, h: int, p: int, kind: str,
                  label: str = None, v_pattern: int = None, v_min: int = None,
                  v_max: int = None, editors: [Packet] = None):
        """
        Create and add a field
        :param document_key:
        :param x:
        :param y:
        :param w:
        :param h:
        :param p:
        :param kind:

        :param label: Optional
        :param v_pattern: Optional
        :param v_min: Optional
        :param v_max: Optional
        :param editors: Optional
        :return: Field object
        """
        if document.key not in self._documents:
            raise RuntimeError(f"No document found with key {document.key}!")

        field = Field.create(x, y, w, h, p, kind, label, v_pattern, v_min, v_max)
        for editor in editors:
            field.add_editor(editor.key)

        self._documents[document.key].add_field(field)
        return field

    def add_signer(self, name: str, email: str=None, phone: str=None, deliver_via: str=None,
                   person_id=None, auth_sms: bool=False, auth_selfie: bool=False, auth_id: bool=False,
                   order: int = None):
        """
        Create and add a signer.
        This should have at least an email xor phone number.

        :param person_id: Optional
        :param name: Optional
        :param email: Optional
        :param phone: Optional
        :param auth_sms: Optional
        :param auth_selfie: Optional
        :param auth_id: Optional
        :param deliver_via: Optional
        :param order: Optional
        :return:
        """
        if phone is None and email is None:
            raise ValidationError('Packet must have either an email or phone number')

        packet = Packet.create(name=name,
                               person_id=person_id,
                               email=email,
                               phone=phone,
                               auth_sms=auth_sms,
                               auth_selfie=auth_selfie,
                               auth_id=auth_id,
                               deliver_via=deliver_via,
                               order=order)
        self._packets[packet.key] = packet
        return packet

    def assign_role(self, document_key: str, signer_id: str, role: str):
        if document_key not in self._documents:
            raise RuntimeError(f"No document found with key {document_key}!")
        if type(self._documents[document_key]) is not TemplateRef:
            raise RuntimeError(f"Document found with key {document_key} is not a Template!")
        if signer_id not in self._packets:
            raise RuntimeError(f"Signer {signer_id} does not have a corresponding packet")

        assignment = TemplateRefAssignment.create(role, signer_id)
        self._documents[document_key].assignments.append(assignment)

    def set_value(self, document_key: str, key: str, value: str):
        if document_key not in self._documents:
            raise RuntimeError(f"No document found with key {document_key}!")
        if type(self._documents[document_key]) is not TemplateRef:
            raise RuntimeError(f"Document found with key {document_key} is not a Template!")

        field_val = TemplateRefFieldValue.create(key, value)
        self._documents[document_key].field_values.append(field_val)

    def _compile_bundle(self) -> Bundle:
        packets = list(self._packets.values())
        documents = list(self._documents.values())
        bundle_out = Bundle.create(packets,
                                   documents,
                                   label=self._label,
                                   in_order=self._in_order,
                                   email_subject=self._email_subj,
                                   email_message=self._email_msg,
                                   is_test=self._is_test,
                                   cc_emails=self._cc_emails,
                                   custom_key=self._custom_key,
                                   team=self._team)
        return bundle_out

    def as_data(self):
        """
        Returns a Bundle as a python dictionary
        :return:
        """
        bundle = self._compile_bundle()
        return bundle.dict(exclude_unset=True, exclude_none=True)

    def as_json(self):
        """
        Returns a Bundle as a python dictionary
        :return:
        """
        bundle = self._compile_bundle()
        return bundle.json(exclude_unset=True, exclude_none=True)

