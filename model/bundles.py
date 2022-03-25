import io

from marshmallow import Schema, post_dump
from marshmallow import fields as mmfields

"""
Developer Note:

Schema classes are for the Marshmallow serializer. 
Validation is being done through these as well.
"""


class ValidationError(RuntimeError):
    def __init__(self, error_text:str):
        super(ValidationError, self).__init__(error_text)


class FieldSchema(Schema):
    kind = mmfields.Str(required=True)
    key = mmfields.Str()
    label = mmfields.Str()
    page = mmfields.Int()
    x = mmfields.Int(required=True)
    y = mmfields.Int(required=True)
    w = mmfields.Int(required=True)
    h = mmfields.Int(required=True)
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
    key = mmfields.Str(required=True)
    deliver_via = mmfields.Str()

    class Meta:
        ordered = True


class TemplateRefAssignmentSchema(Schema):
    role = mmfields.Str(required=True)
    signer = mmfields.Str(required=True)

    class Meta:
        ordered = True


class TemplateRefFieldValueSchema(Schema):
    key = mmfields.Str(required=True)
    initial_value = mmfields.Str()

    class Meta:
        ordered = True


class DocumentSchema(Schema):
    key = mmfields.Str()

    # document related
    file_url = mmfields.URL()
    file_index = mmfields.Int()
    fields = mmfields.List(mmfields.Nested(FieldSchema))

    # template related. kinda weird but must be here, but
    # having a separate "TemplateRefSchema", child of DocumentSchema did not work out.
    # Perhaps a Marshmallow bug? Coded around this by including Template schema fields in Document
    # and the post_dump should clean up anythhing unused/null.
    template_id = mmfields.Str() # UUID to a valid template, required for Template
    assignments = mmfields.List(mmfields.Nested(TemplateRefAssignmentSchema)) # required for a template
    field_values = mmfields.List(mmfields.Nested(TemplateRefFieldValueSchema))

    class Meta:
        ordered = True

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        """
        Removes null values from the JSON.
        :param data:
        :param kwargs:
        :return:
        """
        return {
            key: value for key, value in data.items()
            if value is not None
        }


# This did not work out. Check DocumentSchema for explanation
# class TemplateRefSchema(DocumentSchema):
#     template_id = mmfields.Str()
#     assignments = mmfields.List(mmfields.Nested(TemplateRefAssignmentSchema))
#     field_values = mmfields.List(mmfields.Nested(TemplateRefFieldValueSchema))
#
#     class Meta:
#         ordered = True


class BundleSchema(Schema):
    label = mmfields.Str()
    in_order = mmfields.Bool()
    email_subject = mmfields.Str()
    email_message = mmfields.Str()
    cc_emails = mmfields.List(mmfields.Email)
    is_test = mmfields.Bool()
    packets = mmfields.List(mmfields.Nested(PacketSchema), required=True)
    documents = mmfields.List(mmfields.Nested(DocumentSchema), required=True)

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

        required_fields = [kind, x, y, w, h]
        if None in required_fields:
            raise ValidationError(f"kind, x, y, w, h attributes are required for '{type(self).__name__}' object")

        allowed_kinds = ["att", "cbx", "chk", "dat", "ini", "inp", "sdt", "sel", "sig", "snm", "txt"]
        if kind not in allowed_kinds:
            raise ValidationError(f"kind '{kind}' is invalid. Kind must be one of the following: {allowed_kinds}")

    def add_editor(self, editor:str):
        self.editors.append(editor)


class Document:
    def __init__(self, key, url=None, file_index=None):
        self.key = key
        self.file_url = url
        self.file_index = file_index
        self.fields = []

        required_fields = [key]
        if None in required_fields:
            raise ValidationError(f"key attribute is required for '{type(self).__name__}' object")

    def add_field(self, field: Field):
        self.fields.append(field)


class TemplateRefAssignment:
    def __init__(self, role, signer):
        self.role = role
        self.signer = signer

        required_fields = [role, signer]
        if None in required_fields:
            raise ValidationError(f"role and signer attributes are required for '{type(self).__name__}' object")


class TemplateRefFieldValue:
    def __init__(self, key:str , initial_value:str ):
        self.key = key
        self.initial_value=initial_value

        required_fields = [key, initial_value]
        if None in required_fields:
            raise ValidationError(f"key and initial_value attributes are required for '{type(self).__name__}' object")


class TemplateRef(Document):
    def __init__(self, key:str, template_id, assignments:[TemplateRefAssignment] = [], field_values:[TemplateRefFieldValue] = []):
        super(TemplateRef, self).__init__(key, None)
        self.template_id = template_id
        self.assignments = assignments
        self.field_values = field_values

        required_fields = [assignments, field_values]
        if None in required_fields:
            raise ValidationError(f"kind, x, y, w, h attributes are required for '{type(self).__name__}' object")
        # for field in required_fields:
        #     if type(field) == list:
        #         if len(field) == 0:
        #             raise ValidationError(f"One or more of required list fields (assignments, field_values) is empty.")


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

        required_fields = [key]
        if None in required_fields:
            raise ValidationError(f"key attribute is required for '{type(self).__name__}' object")


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

        required_fields = [packets, documents]
        if None in required_fields:
            raise ValidationError(f"kind, x, y, w, h attributes are required for '{type(self).__name__}' object")
        for field in required_fields:
            if type(field) == list:
                if len(field) == 0:
                    raise ValidationError(f"One or more of required list fields (packets, documents) is empty.")


class BundleBuilder:
    def __init__(self,
                 label: str = None,
                 email_subject: str = None,
                 email_message: str = None,
                 in_order: bool = False,
                 is_test: bool = False):
        self._label = label
        self._in_order = in_order
        self._email_subj = email_subject
        self._email_msg = email_message
        self._cc_emails = []
        self._is_test = is_test
        self._documents = {}
        self._packets = {}

        # for file uploads, index should match those in the document "file_index" field
        self.file_names = []
        self.file_types = []
        self.files = []

    def add_cc(self, email:str):
        self._cc_emails.append(email)
        return self

    def add_document(self, key:str, url:str) -> str:
        '''
        Add a document via url, with unique key.
        :param key:
        :param url:
        :return:
        '''
        if key in self._documents.keys():
            raise RuntimeError(f"Document with key {key} already added!")

        self._documents[key] = Document(key, url=url)
        return key

    def add_document_by_file(self, key:str, file:io.BufferedReader, file_name:str, mime_type:str) -> str:
        '''
        Add a document via url, with unique key.
        :param file:
        :param key:
        :param url:
        :return:
        '''
        if key in self._documents.keys():
            raise RuntimeError(f"Document with key {key} already added!")

        file_index = len(self.files)

        if type(file) == io.BufferedReader and file.readable():
            self.files.append(file)
            self.file_names.append(file_name)
            self.file_types.append(mime_type)
            print(f"Attaching file {file_index}: {file_name}")
        else:
            raise RuntimeError(f"File unreadable.")

        self._documents[key] = Document(key, file_index=file_index)
        return key

    def add_document_by_path(self, key:str, file_path:str, mime_type:str) -> str:
        '''
        Add a document via url, with unique key.
        :param file_path:
        :param key:
        :return:
        '''

        file = open(file_path, 'rb')
        return self.add_document_by_file(key, file, file.name, mime_type)

    def add_document_by_bytearray(self, key:str, byte_array:bytearray, file_name:str,  mime_type:str) -> str:
        '''
        Add a document via url, with unique key.
        :param key:
        :param url:
        :return:
        '''

        bytes = io.BytesIO(byte_array)
        file = io.BufferedReader(bytes, len(byte_array))

        return self.add_document_by_file(key, file,file_name, mime_type)

    def add_document_template(self, key:str, template_id:str):
        if key in self._documents.keys():
            raise RuntimeError(f"Document with key {key} already added!")
        template = TemplateRef(key, template_id)
        self._documents[key] = template
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
        return key

    def assign_signer(self, document_key:str, signer_id:str, role:str):
        if document_key not in self._documents:
            raise RuntimeError(f"No document found with key {document_key}!")
        if type(self._documents[document_key]) is not TemplateRef:
            raise RuntimeError(f"Document found with key {document_key} is not a Template!")
        if signer_id not in self._packets:
            raise RuntimeError(f"Signer {signer_id} does not have a corresponding packet")

        assignment = TemplateRefAssignment(role, signer_id)
        self._documents[document_key].assignments.append(assignment)

    def set_value(self, document_key:str, key:str, value:str):
        if document_key not in self._documents:
            raise RuntimeError(f"No document found with key {document_key}!")
        if type(self._documents[document_key]) is not TemplateRef:
            raise RuntimeError(f"Document found with key {document_key} is not a Template!")

        field_val = TemplateRefFieldValue(key, value)
        self._documents[document_key].field_values.append(field_val)

    def build_json(self):
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
