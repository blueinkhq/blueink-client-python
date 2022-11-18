from blueink.person_helper import PersonHelper
from blueink.utils.testcase import TestCase


class TestPersonHelper(TestCase):
    NAME = "JOHN DOE"

    MD_KEY01 = "KEY01"
    MD_KEY02 = "KEY02"
    MD_VAL01 = 12
    MD_VAL02 = "VAL"
    METADATA = {
        MD_KEY01: MD_VAL01,
        MD_KEY02: MD_VAL02,
    }

    PHONES = ["505 555 5555"]
    EMAILS = ["johndoe@example.com"]

    def _check_values(self, data: dict):
        self.assert_equal(data["name"], self.NAME)

        self.assert_in("channels", data)
        self.assert_len(data["channels"], 2)

        has_phone = False
        has_email = False
        for cc in data["channels"]:
            if cc["kind"] == "em":
                self.assert_in("email", cc)
                self.assert_equal(cc["email"], self.EMAILS[0])
                has_email = True
            elif cc["kind"] == "mp":
                self.assert_in("phone", cc)
                self.assert_equal(cc["phone"], self.PHONES[0])
                has_phone = True

        self.assert_true(has_email)
        self.assert_true(has_phone)

        self.assert_in("metadata", data)
        self.assert_len(data["metadata"], 2)
        self.assert_in(self.MD_KEY01, data["metadata"])
        self.assert_equal(data["metadata"][self.MD_KEY01], self.MD_VAL01)
        self.assert_in(self.MD_KEY02, data["metadata"])
        self.assert_equal(data["metadata"][self.MD_KEY02], self.MD_VAL02)

    def test_atomic(self):
        ph = PersonHelper()
        ph.set_name(self.NAME)
        ph.set_metadata(self.METADATA)
        ph.set_phones(self.PHONES)
        ph.set_emails(self.EMAILS)

        self._check_values(ph.as_dict())

    def test_all_in_one(self):
        ph = PersonHelper(
            name=self.NAME,
            metadata=self.METADATA,
            phones=self.PHONES,
            emails=self.EMAILS,
        )

        self._check_values(ph.as_dict())
