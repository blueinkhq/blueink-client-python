import copy

from munch import Munch

from blueink.bundle_helper import BundleHelper
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
