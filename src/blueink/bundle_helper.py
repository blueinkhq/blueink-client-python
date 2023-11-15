import io
from base64 import b64encode
from os.path import basename
from typing import List

from blueink.model.bundles import (
    Bundle,
    Document,
    Field,
    Packet,
    TemplateRef,
    TemplateRefAssignment,
    TemplateRefFieldValue,
    ValidationError,
)


class BundleHelper:
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
        """Helper class to aid building a Bundle.

        After documents/signers/fields added, use as_data() or as_json() to compile the Bundle either as a python dict or json string.

        Args:
            label:
            email_subject:
            email_message:
            in_order:
            is_test:
            custom_key:
            team:
        """
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

    def add_document_by_url(self, url: str, **additional_data) -> str:
        """Add a file using a URL

        Args:
            url:
            additional_data:

        Returns:
            Document Key
        """
        document = Document.create(file_url=url, **additional_data)
        self._documents[document.key] = document
        return document.key

    def add_document_by_path(self, file_path: str, **additional_data) -> str:
        """Add a file using a file path. File context used, should safely open/close file

        Args:
            file_path:
            additional_data:

        Returns:
            Document Key
        """
        filename = basename(file_path)

        with open(file_path, "rb") as file:
            b64str = b64encode(file.read()).decode("utf-8")

        return self.add_document_by_b64(filename, b64str, **additional_data)

    def add_document_by_file(self, file: io.FileIO, **additional_data) -> str:
        """Add a file using a file path. File context used, should safely open/close file

        Args:
            file:
            additional_data:

        Returns:
            Document Key
        """
        filename = file.name

        file.seek(0)
        b64str = b64encode(file.read()).decode("utf-8")
        file.flush()

        return self.add_document_by_b64(filename, b64str, **additional_data)

    def add_document_by_b64(self, filename: str, b64str: str, **additional_data):
        """Add a file using a b64 string; utf-8 encoded

        Args:
            filename:
            b64str:
            additional_data:

        Returns:
            Document Key
        """
        file_index = len(self.files)

        document = Document.create(
            filename=filename, file_b64=b64str, **additional_data
        )
        print(f"doc -- {document.key}")
        self._documents[document.key] = document
        return document.key

    def add_document_by_bytearray(
        self, filename: str, byte_array: bytearray, **additional_data
    ) -> str:
        """Add a file using a python bytearray object

        Args:
            byte_array:
            filename:
            additional_data:

        Returns:
            Document Key
        """

        bytes = io.BytesIO(byte_array)
        with io.BufferedReader(bytes, len(byte_array)) as file:
            b64str = b64encode(file.read()).decode("utf-8")

        return self.add_document_by_b64(filename, b64str, **additional_data)

    def add_document_template(
        self,
        template_id: str,
        assignments: dict,
        initial_field_values: dict,
        **additional_data,
    ) -> str:
        """Create and add a template reference

        Args:
            template_id: Template UUID from BlueInk
            assignments: dict going from Role to signer ID
            initial_field_values: dict going from docfield key to initial value

        Returns:
            document key
        """
        if template_id in self._documents.keys():
            raise RuntimeError(
                f"Document/Template with id {template_id} already added."
            )

        assigns = []
        for role, signer in assignments.items():
            ref = TemplateRefAssignment.create(role=role, signer=signer)
            assigns.append(ref)

        vals = []
        for field_key, init_val in initial_field_values.items():
            fieldval = TemplateRefFieldValue.create(
                key=field_key, initial_value=init_val
            )
            vals.append(fieldval)

        template = TemplateRef.create(
            template_id=template_id,
            assignments=assigns,
            field_values=vals,
            **additional_data,
        )

        self._documents[template.key] = template
        return template.key

    def add_field(
        self,
        document_key: str,
        x: int,
        y: int,
        w: int,
        h: int,
        p: int,
        kind: str,
        editors: List[str] = None,
        label: str = None,
        v_pattern: str = None,
        v_min: int = None,
        v_max: int = None,
        key=None,
        **additional_data,
    ):
        """Create and add a field to a particular document.

        Args
            document:
            x:
            y:
            w:
            h:
            p:
            kind:
            label: Optional
            v_pattern: Optional
            v_min: Optional
            v_max: Optional
            editors: Optional
            key: Optional
            additional_data: Optional and will append any additional kwargs to the json of the field

        Returns:
             Field key [str]
        """
        if document_key not in self._documents:
            raise RuntimeError(f"No document found with key {document_key}!")

        field = Field.create(
            x,
            y,
            w,
            h,
            p,
            kind,
            label=label,
            v_pattern=v_pattern,
            v_min=v_min,
            v_max=v_max,
            key=key,
            **additional_data,
        )
        for packet_key in editors:
            field.add_editor(packet_key)

        self._documents[document_key].add_field(field)
        return field.key

    def add_signer(
        self,
        name: str,
        email: str = None,
        phone: str = None,
        deliver_via: str = None,
        person_id=None,
        auth_sms: bool = False,
        auth_selfie: bool = False,
        auth_id: bool = False,
        order: int = None,
        key=None,
        **additional_data,
    ):
        """Create and add a signer. With at least an email xor phone number.

        Args:
            key:
            person_id: Optional
            name: Optional
            email: Optional
            phone: Optional
            auth_sms: Optional
            auth_selfie: Optional
            auth_id: Optional
            deliver_via: Optional
            order: Optional
            additional_data: Optional and will append any additional kwargs to the json of the signer

        Returns:
             Packet key
        """
        if phone is None and email is None:
            raise ValidationError("Packet must have either an email or phone number")

        packet = Packet.create(
            name=name,
            person_id=person_id,
            email=email,
            phone=phone,
            auth_sms=auth_sms,
            auth_selfie=auth_selfie,
            auth_id=auth_id,
            deliver_via=deliver_via,
            order=order,
            key=key,
            **additional_data,
        )
        self._packets[packet.key] = packet
        return packet.key

    def assign_role(
        self, document_key: str, signer_key: str, role: str, **additional_data
    ):
        """Assign a signer to a particular role in a template

        Args:
            document_key:
            signer_key:
            role:
            additional_data: Optional and will append any additional kwargs to the json of the ref assignment
        """
        if document_key not in self._documents:
            raise RuntimeError(f"No document found with key {document_key}!")
        if type(self._documents[document_key]) is not TemplateRef:
            raise RuntimeError(
                f"Document found with key {document_key} is not a Template!"
            )
        if signer_key not in self._packets:
            raise RuntimeError(
                f"Signer {signer_key} does not have a corresponding packet"
            )

        assignment = TemplateRefAssignment.create(role, signer_key, **additional_data)
        self._documents[document_key].add_assignment(assignment)

    def set_value(self, document_key: str, key: str, value: str, **additional_data):
        """Set a field's value in a document.

        Args:
            document_key:
            key:
            value:
            additional_data: Optional and will append any additional kwargs to the json of the field value
        """
        if document_key not in self._documents:
            raise RuntimeError(f"No document found with key {document_key}!")
        if type(self._documents[document_key]) is not TemplateRef:
            raise RuntimeError(
                f"Document found with key {document_key} is not a Template!"
            )

        field_val = TemplateRefFieldValue.create(key, value, **additional_data)
        self._documents[document_key].field_values.append(field_val)

    def _compile_bundle(self, **additional_data) -> Bundle:
        """
        Builds a Bundle object complete with all the packets (signers) and documents added through the course
        of this BundleHelper's usage cycle.

        :param additional_data: Optional and will append any additional kwargs to the json of the bundle
        :return:
        """
        packets = list(self._packets.values())
        documents = list(self._documents.values())
        bundle_out = Bundle.create(
            packets,
            documents,
            label=self._label,
            in_order=self._in_order,
            email_subject=self._email_subj,
            email_message=self._email_msg,
            is_test=self._is_test,
            cc_emails=self._cc_emails,
            custom_key=self._custom_key,
            team=self._team,
            **additional_data,
        )
        return bundle_out

    def as_data(self, **additional_data):
        """Return a Bundle as a python dictionary

        Args:
            additional_data: extra data to append to a bundle, as a dict

        Returns:
            Bundle as dictionary
        """
        bundle = self._compile_bundle(**additional_data)
        return bundle.dict(exclude_unset=True, exclude_none=True)

    def as_json(self, **additional_data):
        """Return a Bundle as a json

        Args:
            additional_data: extra data to append to a bundle, as a dict

        Returns:
            Bundle as json
        """
        bundle = self._compile_bundle(**additional_data)
        return bundle.json(exclude_unset=True, exclude_none=True)
