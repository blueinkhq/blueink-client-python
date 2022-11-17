from base64 import b64encode
from os.path import basename
from time import sleep

from munch import Munch
from src.blueink import Client, BundleHelper, PersonHelper
from src.blueink.utils.testcase import TestCase


class TestClient(TestCase):
    DOC_METHODS = Munch(
        PATH="PATH",
        URL="URL",
        B64="BASE64",
        TEMPLATE="TEMPLATE",
    )

    BUNDLE_LABEL_URL = "A URL Bundle Label!"
    BUNDLE_LABEL_PATH = "A PATH Bundle Label!"
    BUNDLE_LABEL_B64 = "A B64 Bundle Label!"
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

    # Person Data
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

    def _bundle_label(self, method: str):
        if method == self.DOC_METHODS.PATH:
            return self.BUNDLE_LABEL_PATH
        elif method == self.DOC_METHODS.URL:
            return self.BUNDLE_LABEL_URL
        elif method == self.DOC_METHODS.B64:
            return self.BUNDLE_LABEL_B64

    def _create_test_bundle_helper(self, method: str) -> (BundleHelper, str, str):
        """
        Returns:
            (BundleHelper, signerkey, fieldkey)
        """

        bh = BundleHelper(
            self._bundle_label(method),
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

    def test_roundtrip_path(self):
        bh, sk, fk = self._create_test_bundle_helper(method=self.DOC_METHODS.PATH)

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
