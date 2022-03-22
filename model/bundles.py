from marshmallow import Schema
from marshmallow import fields as mmfields


class FieldSchema(Schema):
    kind = mmfields.Str()
    key = mmfields.Str()
    label = mmfields.Str()
    page = mmfields.Int()
    x = mmfields.Int()
    y = mmfields.Int()
    w = mmfields.Int()
    h = mmfields.Int()
    v_pattern = mmfields.Str()
    v_min = mmfields.Int()
    v_max = mmfields.Int()
    editors: mmfields.List(mmfields.Str())

    class Meta:
        ordered = True


class PacketSchema(Schema):
    name = mmfields.Str()
    email = mmfields.Email()
    phone = mmfields.Str()
    auth_sms = mmfields.Bool()
    auth_selfie = mmfields.Bool()
    auth_id = mmfields.Bool()
    key = mmfields.Str()
    deliver_via = mmfields.Str()

    class Meta:
        ordered = True


class DocumentSchema(Schema):
    key = mmfields.Str()
    file_url = mmfields.URL()
    fields = mmfields.List(mmfields.Nested(FieldSchema))

    class Meta:
        ordered = True


class BundleSchema(Schema):
    label = mmfields.Str()
    in_order = mmfields.Bool()
    email_subject = mmfields.Str()
    email_message = mmfields.Str()
    # requester_name = mmfields.Str()
    # requester_email = mmfields.Str()
    cc_emails = mmfields.List(mmfields.Email)
    is_test = mmfields.Bool()
    packets = mmfields.List(mmfields.Nested(PacketSchema))
    documents = mmfields.List(mmfields.Nested(DocumentSchema))

    class Meta:
        ordered = True


class TemplateRefAssignmentSchema(Schema):
    role = mmfields.Str()
    signer = mmfields.Str()

    class Meta:
        ordered = True


class TemplateRefFieldValueSchema(Schema):
    key = mmfields.Str()
    initial_value = mmfields.Str()

    class Meta:
        ordered = True


class TemplateRefSchema(DocumentSchema):
    key = mmfields.Str()
    template_id = mmfields.Str()
    assignments = mmfields.List(mmfields.Nested(TemplateRefAssignmentSchema))
    field_values = mmfields.List(mmfields.Nested(TemplateRefFieldValueSchema))

    class Meta:
        ordered = True


class Field:
    def __init__(self, kind:str, key:str, label:str, page:int, x:int, y:int, w:int, h:int, v_pattern:int, v_min:int, v_max:int):
        self.kind = kind
        self.key = key
        self.label = label
        self.page = page
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.v_pattern = v_pattern
        self.v_min = v_min
        self.v_max = v_max
        self.editors: [str] = []

    def add_editor(self, editor:str):
        self.editors.append(editor)


class Document:
    def __init__(self, key, url):
        self.key = key
        self.file_url = url
        self.fields = []

    def add_field(self, field: Field):
        self.fields.append(field)


class TemplateRefAssignment:
    def __init__(self, role, signer):
        self.role = role
        self.signer = signer


class TemplateRefFieldValue:
    def __init__(self, key:str , initial_value:str ):
        self.key = key
        self.initial_value=initial_value


class TemplateRef(Document):
    def __init__(self, key:str, template_id, assignments:[TemplateRefAssignment] = [], field_values:[TemplateRefFieldValue] = []):
        super(TemplateRef, self).__init__(key, None)
        self.template_id = template_id
        self.assignments = assignments
        self.field_values = field_values


class Packet:
    def __init__(self, name:str, email:str, phone:str, auth_sms:bool, auth_selfie:bool, auth_id:bool, key:str,
                 deliver_via:str):
        self.name = name
        self.email = email
        self.phone = phone
        self.auth_sms = auth_sms
        self.auth_selfie = auth_selfie
        self.auth_id = auth_id
        self.key = key
        self.deliver_via = deliver_via


class Bundle:
    def __init__(self, label: str, in_order: bool, email_subject: str, email_message: str, is_test: bool, cc_emails: [str], packets: [Packet], documents: [Document]):

        self.label = label
        self.in_order = in_order
        self.email_subject = email_subject
        self.email_message = email_message
        # self.requester_name = requester_name
        # self.requester_email = requester_email
        self.cc_emails = cc_emails
        self.is_test = is_test
        self.packets = packets
        self.documents = documents


class BundleBuilder:
    def __init__(self,
                 label: str = None,
                 email_subject: str = None,
                 email_message: str = None,
                 in_order: bool = False,
                 is_test: bool = False):
        self._label = label,
        self._in_order = in_order,
        self._email_subj = email_subject,
        self._email_msg = email_message,
        self._cc_emails = []
        self._is_test = is_test
        self._documents = {}
        self._packets = {}

    def add_cc(self, email):
        self._cc_emails.append(email)
        return self

    def add_document(self, key, url) -> str:
        '''
        Add a document via url, with unique key.
        :param key:
        :param url:
        :return:
        '''
        if key in self._documents.keys():
            raise RuntimeError(f"Document with key {key} already added!")

        self._documents[key] = Document(key, url)
        return key

    def add_document_template(self, key, template_id):
        if key in self._documents.keys():
            raise RuntimeError(f"Document with key {key} already added!")

        self._documents[key] = TemplateRef(key, template_id)
        return key

    def add_field_to_document(self, document_key:str, kind:str, key:str, label:str, page:int, x:int, y:int, w:int, h:int, v_pattern:int, v_min:int, v_max:int, editors: [str]):
        if document_key not in self._documents:
            raise RuntimeError(f"No document found with key {document_key}!")

        field = Field(kind, key, label, page, x, y, w, h, v_pattern, v_min, v_max)
        for editor in editors:
            field.add_editor(editor)

        field_keys = [field.key for field in self._documents[document_key].fields]
        if key in field_keys:
            raise RuntimeError(f"Document {document_key} already has a field named {key}")

        self._documents[document_key].fields.append(field)
        return key

    def add_signer(self, name: str, email: str, phone: str, auth_sms:bool, auth_selfie: bool, auth_id: bool, deliver_via: str):
        key = f"signer-{(len(self._packets) + 1)}"
        packet = Packet(name, email, phone, auth_sms, auth_selfie, auth_id, key, deliver_via)
        self._packets[key] = packet
        print(f"generated signer with key '{key}'")
        return key

    def assign_signer(self, document_key:str, signer_id, role):
        if document_key not in self._documents:
            raise RuntimeError(f"No document found with key {document_key}!")
        if type(self._documents[document_key]) is not TemplateRef:
            raise RuntimeError(f"Document found with key {document_key} is not a Template!")
        if signer_id not in self._packets:
            raise RuntimeError(f"Signer {signer_id} does not have a corresponding packet")

        assignment = TemplateRefAssignment(role, signer_id)
        self._documents[document_key].assignments.append(assignment)
        print(f"Assigned {signer_id} to role {role} in document {document_key}")

    def set_value(self, document_key, key, value):
        if document_key not in self._documents:
            raise RuntimeError(f"No document found with key {document_key}!")
        if type(self._documents[document_key]) is not TemplateRef:
            raise RuntimeError(f"Document found with key {document_key} is not a Template!")

        field_val = TemplateRefFieldValue(key, value)
        self._documents[document_key].field_values.append(field_val)

    def build(self):
        bundle_out = Bundle(self._label,
                            self._in_order,
                            self._email_subj,
                            self._email_msg,
                            self._is_test,
                            self._cc_emails,
                            self._packets.values(),
                            self._documents.values())

        schema = BundleSchema()

        return schema.dumps(bundle_out)
