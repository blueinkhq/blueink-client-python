from base64 import b64encode
from copy import deepcopy
from os.path import basename
from time import sleep

from munch import Munch

from blueink import BundleHelper, Client, PersonHelper
from blueink.constants import EVENT_TYPE
from blueink.utils.testcase import TestCase


# -----------------
# Bundle Subclient Tests
# -----------------
class TestClientBundle(TestCase):
    DOC_METHODS = Munch(
        FILE="FILE",
        PATH="PATH",
        URL="URL",
        B64="BASE64",
        BYTES="BYTES",
        TEMPLATE="TEMPLATE",
    )

    BUNDLE_LABELS = {
        DOC_METHODS.PATH: "A PATH Bundle!",
        DOC_METHODS.URL: "A URL Bundle!",
        DOC_METHODS.B64: "A B64 Bundle!",
        DOC_METHODS.BYTES: "A ByteArray Bundle!",
        DOC_METHODS.TEMPLATE: "A Template Bundle!",
        DOC_METHODS.FILE: "A FILE Bundle!",
    }

    EMAIL_SUBJECT = "A Test Bundle!"
    EMAIL_MESSAGE = "Email Message!"

    REAL_DOCUMENT_PATH = "w4.pdf"
    REAL_DOCUMENT_URL = "https://www.irs.gov/pub/irs-pdf/fw4.pdf"

    SIGNER01_KEY = "signer-01"
    SIGNER01_NAME = "Joe Schmoe"
    SIGNER01_EMAIL = "joe.schmoe@example.com"
    SIGNER01_PHONE = "505 555 5555"
    SIGNER01_DELIVERY = "email"

    FIELD01_LABEL = "An Input Field"
    FIELD01_KIND = "inp"
    FIELD01_X = 15
    FIELD01_Y = 20
    FIELD01_W = 16
    FIELD01_H = 8
    FIELD01_P = 1
    FIELD01_EDITORS = [SIGNER01_KEY]

    def _create_test_bundle_helper(self, method: str) -> (BundleHelper, str, str):
        """
        Returns:
            (BundleHelper, signerkey, fieldkey)
        """

        bh = BundleHelper(
            self.BUNDLE_LABELS[method],
            self.EMAIL_SUBJECT,
            self.EMAIL_MESSAGE,
            is_test=True,
        )

        # Add Document
        doc01_key = None
        if method == self.DOC_METHODS.PATH:
            doc01_key = bh.add_document_by_path(self.REAL_DOCUMENT_PATH)
        elif method == self.DOC_METHODS.URL:
            doc01_key = bh.add_document_by_url(self.REAL_DOCUMENT_URL)
        elif method == self.DOC_METHODS.B64:
            file = open(self.REAL_DOCUMENT_PATH, "rb")
            filename = basename(self.REAL_DOCUMENT_PATH)
            b64str = b64encode(file.read()).decode("utf-8")
            file.close()
            doc01_key = bh.add_document_by_b64(filename, b64str)
        elif method == self.DOC_METHODS.FILE:
            with open(self.REAL_DOCUMENT_PATH, "rb") as file:
                doc01_key = bh.add_document_by_file(file)
        elif method == self.DOC_METHODS.BYTES:
            filename = basename(self.REAL_DOCUMENT_PATH)

            with open(self.REAL_DOCUMENT_PATH, "rb") as file:
                byte_array = bytearray(file.read())

            doc01_key = bh.add_document_by_bytearray(byte_array, filename)

        # Add Signer 1
        signer01_key = bh.add_signer(
            key=self.SIGNER01_KEY,
            name=self.SIGNER01_NAME,
            email=self.SIGNER01_EMAIL,
            phone=self.SIGNER01_PHONE,
            deliver_via=self.SIGNER01_DELIVERY,
        )

        # Add Field
        field01_key = bh.add_field(
            document_key=doc01_key,
            x=self.FIELD01_X,
            y=self.FIELD01_Y,
            w=self.FIELD01_W,
            h=self.FIELD01_H,
            p=self.FIELD01_P,
            kind=self.FIELD01_KIND,
            editors=self.FIELD01_EDITORS,
            label=self.FIELD01_LABEL,
        )

        self._check_bundle_data(
            bh.as_data(), signerkey=signer01_key, fieldkey=field01_key
        )

        return bh, signer01_key, field01_key

    def _check_bundle_data(self, compiled_bundle: dict, signerkey, fieldkey):
        self.assert_in("documents", compiled_bundle)
        self.assert_len(compiled_bundle["documents"], 1)

        self.assert_in("fields", compiled_bundle["documents"][0])
        self.assert_len(compiled_bundle["documents"][0]["fields"], 1)

        field01 = compiled_bundle["documents"][0]["fields"][0]
        self.assert_len(field01["editors"], 1)
        self.assert_in("key", field01)
        self.assert_equal(field01["key"], fieldkey)
        self.assert_equal(field01["x"], self.FIELD01_X)
        self.assert_equal(field01["y"], self.FIELD01_Y)
        self.assert_equal(field01["w"], self.FIELD01_W)
        self.assert_equal(field01["h"], self.FIELD01_H)
        self.assert_equal(field01["page"], self.FIELD01_P)
        self.assert_equal(field01["kind"], self.FIELD01_KIND)
        self.assert_equal(field01["label"], self.FIELD01_LABEL)

        self.assert_in("packets", compiled_bundle)
        self.assert_len(compiled_bundle["packets"], 1)

        self.assert_equal(compiled_bundle["packets"][0]["key"], signerkey)

    def _poll_for_successful_file_processing(
        self,
        client: Client,
        bundle_id: str,
        expected_document_count: int,
        max_attempts=5,
        delay_between_seconds=5,
    ):
        attempt = 0
        while attempt < max_attempts:
            attempt = attempt + 1
            sleep(delay_between_seconds)

            resp = client.bundles.retrieve(bundle_id)
            if resp.status != 200:
                print(
                    f"Failed to get bundle {bundle_id} on attempt {attempt}"
                    f" of {max_attempts}"
                )
                continue

            ndocs = len(resp.data["documents"])
            if ndocs == expected_document_count:
                return True

        return False

    def test_roundtrip_url(self):
        bh, sk, fk = self._create_test_bundle_helper(method=self.DOC_METHODS.URL)

        client = Client(raise_exceptions=False)
        resp = client.bundles.create_from_bundle_helper(bh)
        self.assert_equal(resp.status, 201)

        has_all_docs = self._poll_for_successful_file_processing(
            client, resp.data.id, 1
        )
        self.assert_true(has_all_docs)

    def test_roundtrip_b64(self):
        bh, sk, fk = self._create_test_bundle_helper(method=self.DOC_METHODS.B64)

        client = Client(raise_exceptions=False)
        resp = client.bundles.create_from_bundle_helper(bh)
        self.assert_equal(resp.status, 201)

        has_all_docs = self._poll_for_successful_file_processing(
            client, resp.data.id, 1
        )
        self.assert_true(has_all_docs)

    def test_roundtrip_file(self):
        bh, sk, fk = self._create_test_bundle_helper(method=self.DOC_METHODS.FILE)

        client = Client(raise_exceptions=False)
        resp = client.bundles.create_from_bundle_helper(bh)
        self.assert_equal(resp.status, 201)
        has_all_docs = self._poll_for_successful_file_processing(
            client, resp.data.id, 1
        )
        self.assert_true(has_all_docs)

    def test_roundtrip_path(self):
        bh, sk, fk = self._create_test_bundle_helper(method=self.DOC_METHODS.PATH)

        client = Client(raise_exceptions=False)
        resp = client.bundles.create_from_bundle_helper(bh)
        self.assert_equal(resp.status, 201)
        has_all_docs = self._poll_for_successful_file_processing(
            client, resp.data.id, 1
        )
        self.assert_true(has_all_docs)

    def test_roundtrip_bytearray(self):
        bh, sk, fk = self._create_test_bundle_helper(method=self.DOC_METHODS.BYTES)

        client = Client(raise_exceptions=False)
        resp = client.bundles.create_from_bundle_helper(bh)
        self.assert_equal(resp.status, 201)
        has_all_docs = self._poll_for_successful_file_processing(
            client, resp.data.id, 1
        )
        self.assert_true(has_all_docs)

    # def test_roundtrip_template(self):
    #     bh = BundleHelper(self._bundle_label("TEMPLATE"),
    #                       self.EMAIL_SUBJECT,
    #                       self.EMAIL_MESSAGE,
    #                       is_test=True)
    #
    #     signer01_key = bh.add_signer(key=self.SIGNER01_KEY,
    #                                  name=self.SIGNER01_NAME,
    #                                  email=self.SIGNER01_EMAIL,
    #                                  phone=self.SIGNER01_PHONE,
    #                                  deliver_via=self.SIGNER01_DELIVERY)
    #
    #     assignments = {
    #         "signer-1": signer01_key,
    #     }
    #     initvals = {
    #         "inp001-a3Y3q": "MUH INIT VAL"
    #     }
    #
    #     # Add Document
    #     bh.add_document_template(template_id="e745bb78-7a87-4b9c-b3df-54373a1bb2c3",
    #                              assignments=assignments,
    #                              initial_field_values=initvals)
    #
    #     client = Client(raise_exceptions=False)
    #     resp = client.bundles.create_from_bundle_helper(bh)
    #     self.assert_equal(resp.status, 201)
    #
    #     has_all_docs = self._poll_for_successful_file_processing(client,
    #                                                              resp.data.id,
    #                                                              1)
    #     self.assert_true(has_all_docs)


# -----------------
# Person Subclient Tests
# -----------------
class TestClientPerson(TestCase):
    PERSON_NAME = "JOHN DOE"

    PERSON_MD_KEY01 = "KEY01"
    PERSON_MD_KEY02 = "KEY02"
    PERSON_MD_VAL01 = 12
    PERSON_MD_VAL02 = "VAL"
    PERSON_METADATA = {
        PERSON_MD_KEY01: PERSON_MD_VAL01,
        PERSON_MD_KEY02: PERSON_MD_VAL02,
    }

    PERSON_PHONES = ["505 555 5555"]
    PERSON_EMAILS = ["johndoe@example.com"]

    def test_person_create(self):
        ph = PersonHelper(
            name=self.PERSON_NAME,
            metadata=self.PERSON_METADATA,
            phones=self.PERSON_PHONES,
            emails=self.PERSON_EMAILS,
        )

        client = Client(raise_exceptions=False)
        resp = client.persons.create_from_person_helper(ph)
        self.assert_equal(resp.status, 201)


# -----------------
# Webhook Subclient tests
# -----------------
class TestClientWebhook(TestCase):
    WEBHOOK_01 = {
        "url": "https://www.example.com/01/",
        "enabled": True,
        "json": True,
        "event_types": [
            EVENT_TYPE.EVENT_BUNDLE_LAUNCHED,
            EVENT_TYPE.EVENT_BUNDLE_COMPLETE,
        ],
    }

    WEBHOOK_02 = {
        "url": "https://www.example.com/02/",
        "enabled": True,
        "json": True,
        "event_types": [
            EVENT_TYPE.EVENT_BUNDLE_DOCS_READY,
        ],
    }

    WEBHOOK_01_EXTRA_HEADER_A = {
        "name": "Courage_The_Cowardly_Webhook",
        "value": "Muriel Bagge",
        "order": 0,
    }

    WEBHOOK_01_EXTRA_HEADER_B = {
        "name": "Courage_The_Cowardly_Webhook",
        "value": "Eustace Bagge",
        "order": 1,
    }

    # -----------------
    # Webhook CRUD / Listing
    # -----------------
    def test_webhook_creation_raw(self):
        data = self.WEBHOOK_01

        client = Client(raise_exceptions=False)
        resp1 = client.webhooks.create(data=data)
        self.assert_equal(resp1.status, 201, resp1.data)

        resp_clean1 = client.webhooks.delete(resp1.data.id)
        self.assert_equal(resp_clean1.status, 204, resp_clean1.data)

    def test_webhook_listing(self):
        # Known to fail if > 50 webhooks exist; list_webhooks gives up to 50.

        client = Client(raise_exceptions=False)
        pre_create = client.webhooks.list()
        self.assert_equal(pre_create.status, 200)
        pre_create_len = len(pre_create.data)

        data1 = self.WEBHOOK_01
        resp1 = client.webhooks.create(data=data1)
        self.assert_equal(resp1.status, 201, resp1.data)

        data2 = self.WEBHOOK_02
        resp2 = client.webhooks.create(data=data2)
        self.assert_equal(resp1.status, 201, resp2.data)

        post_create = client.webhooks.list()
        self.assert_equal(post_create.status, 200)
        post_create_len = len(post_create.data)

        self.assert_equal(pre_create_len + 2, post_create_len)

        # Cleanup
        resp_clean1 = client.webhooks.delete(resp1.data.id)
        self.assert_equal(resp_clean1.status, 204, resp_clean1.data)

        resp_clean2 = client.webhooks.delete(resp2.data.id)
        self.assert_equal(resp_clean2.status, 204, resp_clean2.data)

    def test_webhook_retrieval(self):
        client = Client(raise_exceptions=False)

        data1 = self.WEBHOOK_01
        resp1 = client.webhooks.create(data=data1)
        self.assert_equal(resp1.status, 201, resp1.data)
        self.assert_equal(resp1.data["url"], data1["url"])

        resp2 = client.webhooks.retrieve(resp1.data.id)
        self.assert_equal(resp2.status, 200, resp2.data)

        self.assert_equal(resp2.data["url"], data1["url"])

        # Cleanup
        resp_clean1 = client.webhooks.delete(resp1.data.id)
        self.assert_equal(resp_clean1.status, 204, resp_clean1.data)

    def test_webhook_delete(self):
        # Known to fail if > 50 webhooks exist; list_webhooks gives up to 50.

        client = Client(raise_exceptions=False)
        resp0 = client.webhooks.list()
        self.assert_equal(resp0.status, 200)
        pre_create_len = len(resp0.data)

        data1 = self.WEBHOOK_01
        resp1 = client.webhooks.create(data=data1)
        self.assert_equal(resp1.status, 201, resp1.data)

        resp2 = client.webhooks.list()
        self.assert_equal(resp2.status, 200)
        post_create_len = len(resp2.data)
        self.assert_equal(pre_create_len + 1, post_create_len)

        resp3 = client.webhooks.delete(resp1.data.id)
        self.assert_equal(resp3.status, 204, resp3.data)

        resp4 = client.webhooks.list()
        self.assert_equal(resp4.status, 200)
        post_delete_len = len(resp4.data)

        self.assert_equal(pre_create_len, post_delete_len)

    def test_webhook_update(self):
        client = Client(raise_exceptions=False)

        data1 = self.WEBHOOK_01
        resp1 = client.webhooks.create(data=data1)
        self.assert_equal(resp1.status, 201, resp1.data)
        self.assert_equal(resp1.data["url"], data1["url"])

        resp2 = client.webhooks.retrieve(resp1.data.id)
        self.assert_equal(resp2.status, 200, resp2.data)

        self.assert_equal(resp2.data["url"], data1["url"])
        self.assert_equal(resp2.data["enabled"], data1["enabled"])
        self.assert_len(resp2.data["event_types"], len(data1["event_types"]))

        update_data = {
            "enabled": False,
            "event_types": [EVENT_TYPE.EVENT_PACKET_VIEWED],
        }
        resp3 = client.webhooks.update(resp1.data.id, update_data)
        self.assert_equal(resp3.status, 200, resp3.data)
        self.assert_equal(resp3.data["enabled"], update_data["enabled"])
        self.assert_len(resp3.data["event_types"], len(update_data["event_types"]))

        # Cleanup
        resp_clean1 = client.webhooks.delete(resp1.data.id)
        self.assert_equal(resp_clean1.status, 204, resp_clean1.data)

    # -----------------
    # Extraheader CRUD / Listing
    # -----------------
    def test_extraheader_creation_raw(self):
        data = self.WEBHOOK_01

        client = Client(raise_exceptions=False)
        resp1 = client.webhooks.create(data=data)
        self.assert_equal(resp1.status, 201, resp1.data)

        eh_data = deepcopy(self.WEBHOOK_01_EXTRA_HEADER_A)
        eh_data["webhook"] = resp1.data["id"]

        resp2 = client.webhooks.create_header(eh_data)
        self.assert_equal(resp2.status, 201, resp2.data)

        # Cleanup
        resp_clean1 = client.webhooks.delete(resp1.data.id)
        self.assert_equal(resp_clean1.status, 204, resp_clean1.data)

    def test_extraheader_listing(self):
        data1 = self.WEBHOOK_01
        data2 = self.WEBHOOK_02

        client = Client(raise_exceptions=False)
        # Create parent webhooks
        resp1a = client.webhooks.create(data=data1)
        self.assert_equal(resp1a.status, 201, resp1a.data)

        resp1b = client.webhooks.create(data=data2)
        self.assert_equal(resp1b.status, 201, resp1b.data)

        # setup and create headers under wh 1
        eh1_data = deepcopy(self.WEBHOOK_01_EXTRA_HEADER_A)
        eh1_data["webhook"] = resp1a.data["id"]
        eh2_data = deepcopy(self.WEBHOOK_01_EXTRA_HEADER_B)
        eh2_data["webhook"] = resp1a.data["id"]
        resp2a = client.webhooks.create_header(eh1_data)
        self.assert_equal(resp2a.status, 201, resp2a.data)
        resp2b = client.webhooks.create_header(eh2_data)
        self.assert_equal(resp2b.status, 201, resp2b.data)

        # Filter by webhook ID, 2 under wh 1, 0 under wh 2
        resp4a = client.webhooks.list_headers(webhook=resp1a.data.id)
        self.assert_equal(resp4a.status, 200, resp4a.data)
        self.assert_len(resp4a.data, 2)

        resp4b = client.webhooks.list_headers(webhook=resp1b.data.id)
        self.assert_equal(resp4b.status, 200, resp4b.data)
        self.assert_len(resp4b.data, 0)

        # Cleanup
        resp_clean1 = client.webhooks.delete(resp1a.data.id)
        self.assert_equal(resp_clean1.status, 204, resp_clean1.data)

        resp_clean2 = client.webhooks.delete(resp1b.data.id)
        self.assert_equal(resp_clean2.status, 204, resp_clean2.data)

    # -----------------
    # Events / Delivery Listing not tested; no CRUD functionality
    # -----------------

    # -----------------
    # Secret testing not implemented, will tamper with whoever runs this test suite
    # -----------------
