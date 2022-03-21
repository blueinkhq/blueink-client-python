import json


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
        self.editors = []

    def add_editor(self, editor:str):
        self.editors.append(editor)

    def __str__(self):
        json.dumps(vars(self))


class Document:
    def __init__(self, key, url):
        self.key = key
        self.file_url = url
        self.fields = []

    def add_field(self, field: Field):
        self.fields.append(field)

    def __str__(self):
        json.dumps(vars(self))


class Packet:
    def __init__(self, name:str, email:str, phone:str, auth_sms:bool, auth_selfie:bool, auth_id:bool, key:str, deliver_via:str):
        self.name = name
        self.email = email
        self.phone = phone
        self.auth_sms = auth_sms
        self.auth_selfie = auth_selfie
        self.auth_id = auth_id
        self.key = key
        self.deliver_via = deliver_via

    def __str__(self):
        json.dumps(vars(self))


class Bundle:
    def __init__(self,
                 label: str,
                 in_order: bool,
                 email_subj: str,
                 email_msg: str,
                 requester_name: str,
                 requester_email: str,
                 is_test: bool,
                 cc_emails: [str],
                 packets: [Packet],
                 documents: [Document]):

        self.label = label
        self.in_order = in_order
        self.email_subject = email_subj
        self.email_message = email_msg
        self.requester_name = requester_name
        self.requester_email = requester_email
        self.cc_emails = cc_emails
        self.is_test = is_test
        self.packets = packets
        self.documents = documents

    def __str__(self):
        json.dumps(vars(self))


class BundleBuilder:
    def __init__(self,
                 label: str,
                 in_order: bool,
                 email_subj: str,
                 email_msg: str,
                 requester_name: str,
                 requester_email: str,
                 is_test: bool):
        self._label = label,
        self._in_order = in_order,
        self._email_subj = email_subj,
        self._email_msg = email_msg,
        self._requester_name = requester_name,
        self._requester_email = requester_email,
        self._cc_emails:[] = [str]
        self._is_test = is_test
        self._documents = [Document]
        self._packets = [Packet]

        self._live_document:Document = None

    def add_cc(self, email):
        self._cc_emails.append(email)
        return self

    def start_document(self, key, url):
        if self._live_document is None:
            self._live_document = Document(key, url)
        else:
            self.end_document()

        return self

    def add_field_to_document(self, kind:str, key:str, label:str, page:int, x:int, y:int, w:int, h:int, v_pattern:int, v_min:int, v_max:int, editors: [str]):
        if self._live_document is None:
            raise RuntimeError("No document started!")

        field = Field(kind, key, label, page, x, y, w, h, v_pattern, v_min, v_max)
        for editor in editors:
            field.add_editor(editor)

        self._live_document.add_field(field)
        return self

    def abort_document(self):
        self._live_document = None
        return self

    def end_document(self):
        if self._live_document is not None:
            self._documents.append(self._live_document)
            self._live_document = None
        else:
            raise RuntimeError("No document started!")

        return self

    def add_signer(self, name: str, email: str, phone: str, auth_sms:bool, auth_selfie: bool, auth_id: bool, key: str, deliver_via: str):
        packet = Packet(name, email, phone, auth_sms, auth_selfie, auth_id, key, deliver_via)
        self._packets.append(packet)
        return self

    def build_json(self):
        bundle_out = Bundle(self._label,
                            self._in_order,
                            self._email_subj,
                            self._email_msg,
                            self._requester_name,
                            self._requester_email,
                            self._is_test,
                            self._cc_emails,
                            self._packets,
                            self._documents)

        return str(bundle_out)
