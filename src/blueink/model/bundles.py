from copy import deepcopy

from marshmallow import Schema, post_dump
from marshmallow import fields as mmf

from src.blueink.constants import (
    BUNDLE_STATUS,
    DELIVER_VIA,
    FIELD_KIND,
    PACKET_STATUS,
)

"""
Developer Note:

Schema classes are for the Marshmallow serializer. 
Validation is being done through these as well.
"""


class ValidationError(RuntimeError):
    def __init__(self, error_text:str):
        super(ValidationError, self).__init__(error_text)


class HiddenEmptyFieldsSchemaMixin:
    @post_dump
    def remove_empties(self, data, many):
        new_data = deepcopy(data)
        for key, value in data.items():
            if value is None:
                new_data.pop(key)

        return new_data


class FieldSchema(Schema):
    kind = mmf.Str(required=True)
    key = mmf.Str()
    label = mmf.Str()
    page = mmf.Int()
    x = mmf.Int(required=True)
    y = mmf.Int(required=True)
    w = mmf.Int(required=True)
    h = mmf.Int(required=True)
    v_pattern = mmf.Str()
    v_min = mmf.Int()
    v_max = mmf.Int()
    editors: mmf.List(mmf.Str())

    class Meta:
        ordered = True


class PacketSchema(Schema, HiddenEmptyFieldsSchemaMixin):
    name = mmf.Str()
    email = mmf.Email()
    phone = mmf.Str()
    auth_sms = mmf.Bool()
    auth_selfie = mmf.Bool()
    auth_id = mmf.Bool()
    key = mmf.Str(required=True)
    deliver_via = mmf.Str()
    person_id = mmf.Str(required=False)
    order = mmf.Int(required=False)

    class Meta:
        ordered = True


class TemplateRefAssignmentSchema(Schema):
    role = mmf.Str(required=True)
    signer = mmf.Str(required=True)

    class Meta:
        ordered = True


class TemplateRefFieldValueSchema(Schema):
    key = mmf.Str(required=True)
    initial_value = mmf.Str()

    class Meta:
        ordered = True


class DocumentSchema(Schema):
    key = mmf.Str()

    # document related
    file_url = mmf.URL()
    file_index = mmf.Int()
    fields = mmf.List(mmf.Nested(FieldSchema))

    # template related. kinda weird but must be here, but
    # having a separate "TemplateRefSchema", child of DocumentSchema did not work out.
    # Perhaps a Marshmallow bug? Coded around this by including Template schema fields in Document
    # and the post_dump should clean up anythhing unused/null.
    template_id = mmf.Str() # UUID to a valid template, required for Template
    assignments = mmf.List(mmf.Nested(TemplateRefAssignmentSchema)) # required for a template
    field_values = mmf.List(mmf.Nested(TemplateRefFieldValueSchema))

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


class BundleSchema(Schema, HiddenEmptyFieldsSchemaMixin):
    label = mmf.Str()
    in_order = mmf.Bool()
    email_subject = mmf.Str()
    email_message = mmf.Str()
    cc_emails = mmf.List(mmf.Email)
    is_test = mmf.Bool()
    packets = mmf.List(mmf.Nested(PacketSchema), required=True)
    documents = mmf.List(mmf.Nested(DocumentSchema), required=True)
    custom_key = mmf.Str()
    team = mmf.Str()

    class Meta:
        ordered = True


class Field:
    KIND = FIELD_KIND

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
    DELIVER_VIA = DELIVER_VIA
    STATUS = PACKET_STATUS

    def __init__(self, name:str, email:str, phone:str, auth_sms:bool, auth_selfie:bool, auth_id:bool, key:str,
                 deliver_via:str, person_id: str, order: int):
        self.name = name
        self.email = email
        self.phone = phone
        self.auth_sms = auth_sms
        self.auth_selfie = auth_selfie
        self.auth_id = auth_id
        self.key = key
        self.deliver_via = deliver_via
        self.person_id = person_id
        self.order = order

        required_fields = [key]
        if None in required_fields:
            raise ValidationError(f"key attribute is required for '{type(self).__name__}' object")


class Bundle:
    STATUS = BUNDLE_STATUS

    def __init__(self, label: str, in_order: bool, email_subject: str, email_message: str, is_test: bool,
                 cc_emails: [str], packets: [Packet], documents: [Document], custom_key: str, team: str):

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
        self.custom_key = custom_key
        self.team = team

        required_fields = [packets, documents]
        if None in required_fields:
            raise ValidationError(f"kind, x, y, w, h attributes are required for '{type(self).__name__}' object")
        for field in required_fields:
            if type(field) == list:
                if len(field) == 0:
                    raise ValidationError(f"One or more of required list fields (packets, documents) is empty.")

        if self.in_order:
            order_indices = []
            for packet in self.packets:
                if packet.order is None:
                    raise ValidationError(f'Bundle is set to be ordered but one or more packets (of {len(self.packets)})'
                                          f' do not have an order index: {packet.name}')
                if packet.order in order_indices:
                    raise ValidationError('Two or more packets cannot have the same order index.')
                order_indices.append(packet.order)

            for i in [i for i in range(0, len(self.packets))]:
                if i not in order_indices:
                    raise ValidationError('Malformed packet ordering. Check that packets have '
                                          'sensible indices (eg. no skipped index)')
