import copy
from datetime import datetime, timezone, timedelta

import pytest
from munch import Munch

from blueink.bundle_helper import BundleHelper
from blueink.model.bundles import ImportedDocument
from blueink.utils.testcase import TestCase


class TestBundleHelper(TestCase):

    DOCUMENT_CREATE_BY_METHOD = Munch(
        url="URL",
        pth="PATH",
        b64="BASE64",
    )

    BUNDLE_INIT_DATA = {
        "label": "TEST_BUNDLE",
        "email_subject": "EMAIL_SUBJECT",
        "email_message": "EMAIL_MESSAGE",
        "in_order": True,
        "is_test": False,
        "custom_key": "CUSTOM_KEY",
    }

    SIGNER_01_DATA = {
        "name": "Eli Vance",
        "email": "eli@blackmesa.gov",
        "phone": "505 555 5555",
        "deliver_via": "email",
        "person_id": "person-01",
        "auth_sms": False,
        "auth_selfie": False,
        "auth_id": False,
    }

    SIGNER_02_DATA = {
        "name": "Gordon Freeman",
        "email": "gordon@blackmesa.gov",
        "phone": "505 555 5556",
        "deliver_via": "email",
        "person_id": "person-02",
        "auth_sms": False,
        "auth_selfie": False,
        "auth_id": False,
    }

    FIELD_01_DATA = {
        "x": 15,
        "y": 20,
        "w": 10,
        "h": 12,
        "p": 1,
        "kind": "inp",
        "editors": [],
        "label": "MY_INPUT_01",
    }

    FIELD_02_DATA = {
        "x": 23,
        "y": 43,
        "w": 5,
        "h": 2,
        "p": 1,
        "kind": "inp",
        "editors": [],
        "label": "MY_INPUT_02",
    }

    DOCUMENT_01_URL = "https://www.example.com/example1.pdf"
    DOCUMENT_02_URL = "https://www.example.com/example2.pdf"

    REAL_DOCUMENT_PATH = "w4.pdf"
    REAL_DOCUMENT_URL = "https://www.irs.gov/pub/irs-pdf/fw4.pdf"

    def test_base_bundle(self):
        """Test creating a Bundle with no documents, no signers -- just the base Bundle"""
        input_data = copy.deepcopy(self.BUNDLE_INIT_DATA)
        bh = BundleHelper(**input_data)
        compiled_bundle = bh.as_data()

        for key, value in input_data.items():
            self.assert_equal(compiled_bundle[key], value)

    def test_adding_document_via_url(self):
        input_data = copy.deepcopy(self.BUNDLE_INIT_DATA)
        url01 = self.DOCUMENT_01_URL
        url02 = self.DOCUMENT_02_URL

        bh = BundleHelper(**input_data)
        bh.add_document_by_url(url01)
        bh.add_document_by_url(url02)

        compiled_bundle = bh.as_data()

        self.assert_in("documents", compiled_bundle)
        self.assert_len(compiled_bundle["documents"], 2)

        self.assert_in("file_url", compiled_bundle["documents"][0])
        self.assert_in("file_url", compiled_bundle["documents"][1])

        self.assert_equal(compiled_bundle["documents"][0]["file_url"], url01)
        self.assert_equal(compiled_bundle["documents"][1]["file_url"], url02)

    def test_adding_document_via_b64(self):
        input_data = copy.deepcopy(self.BUNDLE_INIT_DATA)
        url01 = self.DOCUMENT_01_URL
        url02 = self.DOCUMENT_02_URL

        bh = BundleHelper(**input_data)
        bh.add_document_by_url(url01)
        bh.add_document_by_url(url02)

        compiled_bundle = bh.as_data()

        self.assert_in("documents", compiled_bundle)
        self.assert_len(compiled_bundle["documents"], 2)

        self.assert_in("file_url", compiled_bundle["documents"][0])
        self.assert_in("file_url", compiled_bundle["documents"][1])

        self.assert_equal(compiled_bundle["documents"][0]["file_url"], url01)
        self.assert_equal(compiled_bundle["documents"][1]["file_url"], url02)

    def test_adding_fields(self):
        input_data = copy.deepcopy(self.BUNDLE_INIT_DATA)
        url01 = self.DOCUMENT_01_URL
        signer01_data = copy.deepcopy(self.SIGNER_01_DATA)
        signer02_data = copy.deepcopy(self.SIGNER_02_DATA)
        field01_data = copy.deepcopy(self.FIELD_01_DATA)
        field02_data = copy.deepcopy(self.FIELD_02_DATA)

        bh = BundleHelper(**input_data)
        doc01_key = bh.add_document_by_url(url01)
        signer01_key = bh.add_signer(**signer01_data)
        signer02_key = bh.add_signer(**signer02_data)

        field01_data["document_key"] = doc01_key
        field01_data["editors"].append(signer01_key)
        field01_data["editors"].append(signer02_key)
        bh.add_field(**field01_data)

        field02_data["document_key"] = doc01_key
        field02_data["editors"].append(signer01_key)
        bh.add_field(**field02_data)

        compiled_bundle = bh.as_data()

        self.assert_in("documents", compiled_bundle)
        self.assert_len(compiled_bundle["documents"], 1)

        self.assert_in("fields", compiled_bundle["documents"][0])
        self.assert_len(compiled_bundle["documents"][0]["fields"], 2)

        field01 = compiled_bundle["documents"][0]["fields"][0]
        self.assert_len(field01["editors"], 2)
        self.assert_in("key", field01)
        self.assert_equal(field01["x"], field01_data["x"])
        self.assert_equal(field01["y"], field01_data["y"])
        self.assert_equal(field01["w"], field01_data["w"])
        self.assert_equal(field01["h"], field01_data["h"])
        self.assert_equal(field01["page"], field01_data["p"])
        self.assert_equal(field01["kind"], field01_data["kind"])
        self.assert_equal(field01["label"], field01_data["label"])

        field02 = compiled_bundle["documents"][0]["fields"][1]
        self.assert_len(field02["editors"], 1)
        self.assert_in("key", field02)
        self.assert_equal(field02["x"], field02_data["x"])
        self.assert_equal(field02["y"], field02_data["y"])
        self.assert_equal(field02["w"], field02_data["w"])
        self.assert_equal(field02["h"], field02_data["h"])
        self.assert_equal(field02["page"], field02_data["p"])
        self.assert_equal(field02["kind"], field02_data["kind"])
        self.assert_equal(field02["label"], field02_data["label"])

        # Correct packets
        self.assert_in("packets", compiled_bundle)
        self.assert_len(compiled_bundle["packets"], 2)

        self.assert_equal(compiled_bundle["packets"][0]["key"], signer01_key)
        self.assert_equal(compiled_bundle["packets"][1]["key"], signer02_key)

        # Verify signer data transferred as expected
        for k, v in signer01_data.items():
            self.assert_equal(compiled_bundle["packets"][0][k], v)
        for k, v in signer02_data.items():
            self.assert_equal(compiled_bundle["packets"][1][k], v)

    def test_adding_auto_placements(self):
        """Test adding auto-placement fields to a document"""
        input_data = copy.deepcopy(self.BUNDLE_INIT_DATA)
        url01 = self.DOCUMENT_01_URL
        signer01_data = copy.deepcopy(self.SIGNER_01_DATA)

        bh = BundleHelper(**input_data)
        doc01_key = bh.add_document_by_url(url01)
        signer01_key = bh.add_signer(**signer01_data)

        # Add auto-placement for signature
        bh.add_auto_placement(
            document_key=doc01_key,
            kind="sig",
            search="Signature",
            w=20,
            h=5,
            offset_x=-5,
            offset_y=2,
            editors=[signer01_key],
        )

        # Add auto-placement for input field
        bh.add_auto_placement(
            document_key=doc01_key,
            kind="inp",
            search="Address",
            w=20,
            h=2,
            offset_x=8,
            offset_y=0,
            editors=[signer01_key],
        )

        compiled_bundle = bh.as_data()

        # Verify document exists
        self.assert_in("documents", compiled_bundle)
        self.assert_len(compiled_bundle["documents"], 1)

        # Verify auto_placements exist
        self.assert_in("auto_placements", compiled_bundle["documents"][0])
        self.assert_len(compiled_bundle["documents"][0]["auto_placements"], 2)

        # Verify first auto-placement (signature)
        auto_placement_1 = compiled_bundle["documents"][0]["auto_placements"][0]
        self.assert_equal(auto_placement_1["kind"], "sig")
        self.assert_equal(auto_placement_1["search"], "Signature")
        self.assert_equal(auto_placement_1["w"], 20)
        self.assert_equal(auto_placement_1["h"], 5)
        self.assert_equal(auto_placement_1["offset_x"], -5)
        self.assert_equal(auto_placement_1["offset_y"], 2)
        self.assert_in(signer01_key, auto_placement_1["editors"])

        # Verify second auto-placement (input)
        auto_placement_2 = compiled_bundle["documents"][0]["auto_placements"][1]
        self.assert_equal(auto_placement_2["kind"], "inp")
        self.assert_equal(auto_placement_2["search"], "Address")
        self.assert_equal(auto_placement_2["w"], 20)
        self.assert_equal(auto_placement_2["h"], 2)
        self.assert_equal(auto_placement_2["offset_x"], 8)
        self.assert_equal(auto_placement_2["offset_y"], 0)
        self.assert_in(signer01_key, auto_placement_2["editors"])

    def test_auto_placements_with_regular_fields(self):
        """Test that auto-placements and regular fields can coexist"""
        input_data = copy.deepcopy(self.BUNDLE_INIT_DATA)
        url01 = self.DOCUMENT_01_URL
        signer01_data = copy.deepcopy(self.SIGNER_01_DATA)
        field01_data = copy.deepcopy(self.FIELD_01_DATA)

        bh = BundleHelper(**input_data)
        doc01_key = bh.add_document_by_url(url01)
        signer01_key = bh.add_signer(**signer01_data)

        # Add a regular field
        field01_data["document_key"] = doc01_key
        field01_data["editors"].append(signer01_key)
        bh.add_field(**field01_data)

        # Add an auto-placement
        bh.add_auto_placement(
            document_key=doc01_key,
            kind="sig",
            search="Sign Here",
            w=25,
            h=6,
            offset_x=0,
            offset_y=3,
            editors=[signer01_key],
        )

        compiled_bundle = bh.as_data()

        # Verify both fields and auto_placements exist
        self.assert_in("documents", compiled_bundle)
        doc = compiled_bundle["documents"][0]

        self.assert_in("fields", doc)
        self.assert_len(doc["fields"], 1)

        self.assert_in("auto_placements", doc)
        self.assert_len(doc["auto_placements"], 1)

    def test_auto_placement_with_page_restriction(self):
        """Test auto-placement with page number restriction"""
        input_data = copy.deepcopy(self.BUNDLE_INIT_DATA)
        url01 = self.DOCUMENT_01_URL
        signer01_data = copy.deepcopy(self.SIGNER_01_DATA)

        bh = BundleHelper(**input_data)
        doc01_key = bh.add_document_by_url(url01)
        signer01_key = bh.add_signer(**signer01_data)

        # Add auto-placement restricted to page 2
        bh.add_auto_placement(
            document_key=doc01_key,
            kind="sig",
            search="Page 2 Signature",
            w=20,
            h=5,
            page=2,
            editors=[signer01_key],
        )

        compiled_bundle = bh.as_data()
        auto_placement = compiled_bundle["documents"][0]["auto_placements"][0]

        self.assert_equal(auto_placement["page"], 2)

    def test_auto_placement_with_attachment_types(self):
        """Test auto-placement with v_attachment_types restriction"""
        input_data = copy.deepcopy(self.BUNDLE_INIT_DATA)
        url01 = self.DOCUMENT_01_URL
        signer01_data = copy.deepcopy(self.SIGNER_01_DATA)

        bh = BundleHelper(**input_data)
        doc01_key = bh.add_document_by_url(url01)
        signer01_key = bh.add_signer(**signer01_data)

        bh.add_auto_placement(
            document_key=doc01_key,
            kind="att",
            search="Upload your document",
            w=20,
            h=5,
            v_attachment_types=["pdf", "png"],
            editors=[signer01_key],
        )

        compiled_bundle = bh.as_data()
        auto_placement = compiled_bundle["documents"][0]["auto_placements"][0]

        self.assert_equal(auto_placement["kind"], "att")
        self.assert_equal(auto_placement["v_attachment_types"], ["pdf", "png"])

    def test_field_with_attachment_types(self):
        """Test adding a field with v_attachment_types"""
        input_data = copy.deepcopy(self.BUNDLE_INIT_DATA)
        url01 = self.DOCUMENT_01_URL
        signer01_data = copy.deepcopy(self.SIGNER_01_DATA)

        bh = BundleHelper(**input_data)
        doc01_key = bh.add_document_by_url(url01)
        signer01_key = bh.add_signer(**signer01_data)

        bh.add_field(
            document_key=doc01_key,
            x=10,
            y=20,
            w=30,
            h=10,
            p=1,
            kind="att",
            editors=[signer01_key],
            v_attachment_types=["pdf", "docx"],
        )

        compiled_bundle = bh.as_data()
        field = compiled_bundle["documents"][0]["fields"][0]

        self.assert_equal(field["kind"], "att")
        self.assert_equal(field["v_attachment_types"], ["pdf", "docx"])

    def test_bundle_with_expires_iso_format(self):
        """Test that expires field is passed through in ISO format"""
        input_data = copy.deepcopy(self.BUNDLE_INIT_DATA)
        future_datetime = (datetime.now(tz=timezone.utc) + timedelta(days=30)).replace(
            hour=23, minute=59, second=59, microsecond=0
        )
        expires_iso = future_datetime.isoformat()

        bh = BundleHelper(**input_data, expires=expires_iso)
        compiled_bundle = bh.as_data()

        self.assert_in("expires", compiled_bundle)
        self.assert_equal(compiled_bundle["expires"], expires_iso)

    def test_bundle_without_expires(self):
        """Test that expires field is absent when not set"""
        input_data = copy.deepcopy(self.BUNDLE_INIT_DATA)
        bh = BundleHelper(**input_data)
        compiled_bundle = bh.as_data()

        self.assert_not_in("expires", compiled_bundle)

    def test_add_signer_with_witness_fields(self):
        """Test that requires_witness and witness_nominated_by pass through to the packet"""
        input_data = copy.deepcopy(self.BUNDLE_INIT_DATA)
        signer01_data = copy.deepcopy(self.SIGNER_01_DATA)

        bh = BundleHelper(**input_data)
        signer01_key = bh.add_signer(
            **signer01_data,
            requires_witness=True,
            witness_nominated_by="signer",
        )
        compiled_bundle = bh.as_data()

        self.assert_len(compiled_bundle["packets"], 1)
        packet = compiled_bundle["packets"][0]
        self.assert_equal(packet["key"], signer01_key)
        self.assert_in("requires_witness", packet)
        self.assert_equal(packet["requires_witness"], True)
        self.assert_in("witness_nominated_by", packet)
        self.assert_equal(packet["witness_nominated_by"], "signer")

    def test_add_signer_without_witness_fields(self):
        """Test that witness fields are absent on the packet when not set"""
        input_data = copy.deepcopy(self.BUNDLE_INIT_DATA)
        signer01_data = copy.deepcopy(self.SIGNER_01_DATA)

        bh = BundleHelper(**input_data)
        bh.add_signer(**signer01_data)
        compiled_bundle = bh.as_data()

        self.assert_len(compiled_bundle["packets"], 1)
        packet = compiled_bundle["packets"][0]
        self.assert_not_in("requires_witness", packet)
        self.assert_not_in("witness_nominated_by", packet)

    def test_adding_document_via_html(self):
        """Test adding a document using HTML content"""
        input_data = copy.deepcopy(self.BUNDLE_INIT_DATA)
        html_content = "<html><body><p>Test document</p></body></html>"

        bh = BundleHelper(**input_data)
        doc_key = bh.add_document_by_html(html_content)

        compiled_bundle = bh.as_data()

        self.assert_in("documents", compiled_bundle)
        self.assert_len(compiled_bundle["documents"], 1)

        doc = compiled_bundle["documents"][0]
        self.assert_in("file_html", doc)
        self.assert_equal(doc["file_html"], html_content)
        self.assert_equal(doc["key"], doc_key)

    def test_adding_document_via_html_with_filename(self):
        """Test adding an HTML document with a custom filename"""
        input_data = copy.deepcopy(self.BUNDLE_INIT_DATA)
        html_content = "<html><body><p>Test document</p></body></html>"

        bh = BundleHelper(**input_data)
        bh.add_document_by_html(html_content, filename="my_doc.pdf")

        compiled_bundle = bh.as_data()
        doc = compiled_bundle["documents"][0]

        self.assert_equal(doc["file_html"], html_content)
        self.assert_equal(doc["filename"], "my_doc.pdf")

    def test_adding_document_via_html_with_fields_mode(self):
        """Test adding an HTML document with html_fields_mode"""
        input_data = copy.deepcopy(self.BUNDLE_INIT_DATA)
        html_content = "<html><body><p>Test document</p></body></html>"

        bh = BundleHelper(**input_data)
        bh.add_document_by_html(html_content, html_fields_mode="blueink")

        compiled_bundle = bh.as_data()
        doc = compiled_bundle["documents"][0]

        self.assert_equal(doc["file_html"], html_content)
        self.assert_equal(doc["html_fields_mode"], "blueink")

    def test_field_with_v_regex(self):
        """Test adding a field with v_regex and v_regex_msg"""
        input_data = copy.deepcopy(self.BUNDLE_INIT_DATA)
        url01 = self.DOCUMENT_01_URL
        signer01_data = copy.deepcopy(self.SIGNER_01_DATA)

        bh = BundleHelper(**input_data)
        doc01_key = bh.add_document_by_url(url01)
        signer01_key = bh.add_signer(**signer01_data)

        bh.add_field(
            document_key=doc01_key,
            x=10,
            y=20,
            w=30,
            h=10,
            p=1,
            kind="inp",
            editors=[signer01_key],
            v_regex="^[A-Z]+$",
            v_regex_msg="Uppercase letters only",
        )

        compiled_bundle = bh.as_data()
        field = compiled_bundle["documents"][0]["fields"][0]

        self.assert_equal(field["v_regex"], "^[A-Z]+$")
        self.assert_equal(field["v_regex_msg"], "Uppercase letters only")

    def test_field_with_data_flow_tag(self):
        """Test adding a field with a data_flow_tag"""
        input_data = copy.deepcopy(self.BUNDLE_INIT_DATA)
        url01 = self.DOCUMENT_01_URL
        signer01_data = copy.deepcopy(self.SIGNER_01_DATA)

        bh = BundleHelper(**input_data)
        doc01_key = bh.add_document_by_url(url01)
        signer01_key = bh.add_signer(**signer01_data)

        bh.add_field(
            document_key=doc01_key,
            x=10,
            y=20,
            w=30,
            h=10,
            p=1,
            kind="inp",
            editors=[signer01_key],
            data_flow_tag="customer_email",
        )

        compiled_bundle = bh.as_data()
        field = compiled_bundle["documents"][0]["fields"][0]

        self.assert_equal(field["data_flow_tag"], "customer_email")

    def test_field_without_data_flow_tag(self):
        """Test that data_flow_tag is absent on the field when not set"""
        input_data = copy.deepcopy(self.BUNDLE_INIT_DATA)
        url01 = self.DOCUMENT_01_URL
        signer01_data = copy.deepcopy(self.SIGNER_01_DATA)

        bh = BundleHelper(**input_data)
        doc01_key = bh.add_document_by_url(url01)
        signer01_key = bh.add_signer(**signer01_data)

        bh.add_field(
            document_key=doc01_key,
            x=10,
            y=20,
            w=30,
            h=10,
            p=1,
            kind="inp",
            editors=[signer01_key],
        )

        compiled_bundle = bh.as_data()
        field = compiled_bundle["documents"][0]["fields"][0]

        self.assert_not_in("data_flow_tag", field)

    def test_bundle_with_tag_values(self):
        """Test that tag_values pass through to the compiled bundle"""
        input_data = copy.deepcopy(self.BUNDLE_INIT_DATA)
        tag_values = {"customer_email": "joe@example.com"}

        bh = BundleHelper(**input_data, tag_values=tag_values)
        compiled_bundle = bh.as_data()

        self.assert_in("tag_values", compiled_bundle)
        self.assert_equal(compiled_bundle["tag_values"], tag_values)

    def test_bundle_without_tag_values(self):
        """Test that tag_values are absent when not set"""
        input_data = copy.deepcopy(self.BUNDLE_INIT_DATA)
        bh = BundleHelper(**input_data)
        compiled_bundle = bh.as_data()

        self.assert_not_in("tag_values", compiled_bundle)


class TestImportedDocument(TestCase):
    def test_create_with_file_b64(self):
        """Test creating an ImportedDocument with file_b64"""
        doc = ImportedDocument.create(file_b64="dGVzdA==", filename="test.pdf")
        self.assert_not_none(doc.key)
        self.assert_equal(doc.file_b64, "dGVzdA==")
        self.assert_equal(doc.filename, "test.pdf")
        self.assert_none(doc.file_html)

    def test_create_with_file_html(self):
        """Test creating an ImportedDocument with file_html"""
        html = "<html><body><p>Test</p></body></html>"
        doc = ImportedDocument.create(file_html=html)
        self.assert_not_none(doc.key)
        self.assert_equal(doc.file_html, html)
        self.assert_none(doc.file_b64)

    def test_create_with_custom_key(self):
        """Test creating an ImportedDocument with a custom key"""
        doc = ImportedDocument.create(key="my-doc", file_b64="dGVzdA==")
        self.assert_equal(doc.key, "my-doc")

    def test_create_with_file_url_and_file_b64(self):
        """Test creating an ImportedDocument with file_url and file_b64"""
        doc = ImportedDocument.create(
            file_b64="dGVzdA==",
            file_url="https://example.com/test.pdf",
            filename="test.pdf",
        )
        self.assert_equal(doc.file_b64, "dGVzdA==")
        self.assert_equal(doc.file_url, "https://example.com/test.pdf")

    def test_validation_error_both_file_b64_and_file_html(self):
        """Test that providing both file_b64 and file_html raises a ValidationError"""
        with pytest.raises(Exception) as exc_info:
            ImportedDocument.create(
                file_b64="dGVzdA==",
                file_html="<html><body></body></html>",
            )
        self.assert_in("file_b64", str(exc_info.value))
        self.assert_in("file_html", str(exc_info.value))

    def test_validation_error_neither_file_b64_nor_file_html(self):
        """Test that providing neither file_b64 nor file_html raises a ValidationError"""
        with pytest.raises(Exception) as exc_info:
            ImportedDocument.create()
        self.assert_in("file_b64", str(exc_info.value))
        self.assert_in("file_html", str(exc_info.value))

    def test_validation_error_file_url_only(self):
        """Test that providing only file_url raises a ValidationError"""
        with pytest.raises(Exception):
            ImportedDocument.create(file_url="https://example.com/test.pdf")
