import copy

from src.blueink import BundleHelper
from src.blueink.utils.testcase import TestCase


class TestBundleHelper(TestCase):

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
        "label": "MY_INPUT_01"
    }

    FIELD_02_DATA = {
        "x": 23,
        "y": 43,
        "w": 5,
        "h": 2,
        "p": 1,
        "kind": "inp",
        "editors": [],
        "label": "MY_INPUT_02"
    }

    DOCUMENT_01_URL = "https://www.example.com/example1.pdf"
    DOCUMENT_02_URL = "https://www.example.com/example2.pdf"

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

        # Bundle and Field correctly populated, probably can use reflection
        # to be more thorough.
        self.assert_in("documents", compiled_bundle)
        self.assert_len(compiled_bundle["documents"], 1)

        self.assert_in("fields", compiled_bundle["documents"][0])
        self.assert_len(compiled_bundle["documents"][0]["fields"], 2)

        field01 = compiled_bundle["documents"][0]["fields"][0]
        self.assert_equal(field01_data["label"], field01["label"])
        self.assert_len(field01["editors"], 2)

        field02 = compiled_bundle["documents"][0]["fields"][1]
        self.assert_equal(field02_data["label"], field02["label"])
        self.assert_len(field02["editors"], 1)

        # Correct packets
        self.assert_in("packets", compiled_bundle)
        self.assert_len(compiled_bundle["packets"], 2)

        self.assert_equal(compiled_bundle["packets"][0]["key"], signer01_key)
        self.assert_equal(compiled_bundle["packets"][1]["key"], signer02_key)
