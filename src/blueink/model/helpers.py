import io

from src.blueink.constants import ATTACHMENT_TYPE, BUNDLE_ORDER, BUNDLE_STATUS, DELIVER_VIA, FIELD_KIND, PACKET_STATUS, \
    V_PATTERN
from src.blueink.model.bundles import Document, TemplateRef, Field, Packet, TemplateRefAssignment, \
    TemplateRefFieldValue, Bundle, BundleSchema


class BundleHelper:
    ATTACHMENT_TYPE = ATTACHMENT_TYPE
    BUNDLE_ORDER = BUNDLE_ORDER
    BUNDLE_STATUS = BUNDLE_STATUS
    DELIVER_VIA = DELIVER_VIA
    FIELD_KIND = FIELD_KIND
    PACKET_STATUS = PACKET_STATUS
    V_PATTERN = V_PATTERN

    def __init__(self,
                 label: str = None,
                 email_subject: str = None,
                 email_message: str = None,
                 in_order: bool = False,
                 is_test: bool = False,
                 custom_key: str = None,
                 team: str = None):
        self._label = label
        self._in_order = in_order
        self._email_subj = email_subject
        self._email_msg = email_message
        self._cc_emails = []
        self._is_test = is_test
        self._documents = {}
        self._packets = {}
        self._custom_key = custom_key
        self._team = team

        # for file uploads, index should match those in the document "file_index" field
        self.file_names = []
        self.file_types = []
        self.files = []

    def add_cc(self, email:str):
        self._cc_emails.append(email)
        return self

    def add_document_by_url(self, key:str, url:str) -> str:
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

    def add_field(self, document_key:str, kind:str, key:str, label:str, page:int, x:int, y:int, w:int, h:int, v_pattern:int, v_min:int, v_max:int, editors: [str]):
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

    def add_signer(self, name: str, email: str, phone: str, auth_sms:bool, auth_selfie: bool, auth_id: bool,
                   deliver_via: str, person_id: str = None, order: int = None):
        key = f"signer-{(len(self._packets) + 1)}"
        packet = Packet(name, email, phone, auth_sms, auth_selfie, auth_id, key, deliver_via, person_id, order)
        self._packets[key] = packet
        return key

    def assign_role(self, document_key:str, signer_id:str, role:str):
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

    def as_data(self):
        bundle_out = Bundle(self._label,
                            self._in_order,
                            self._email_subj,
                            self._email_msg,
                            self._is_test,
                            self._cc_emails,
                            self._packets.values(),
                            self._documents.values(),
                            self._custom_key,
                            self._team)

        schema = BundleSchema()

        return schema.dumps(bundle_out)