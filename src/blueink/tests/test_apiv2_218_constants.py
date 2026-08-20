from blueink.constants import FIELD_KIND, PACKET_STATUS
from blueink.model.bundles import Bundle
from blueink.utils.testcase import TestCase


class TestApiV218Constants(TestCase):
    def test_field_kind_includes_stamp(self):
        self.assert_equal(FIELD_KIND.STAMP, "stp")
        self.assert_in("stp", FIELD_KIND.values())

    def test_packet_status_includes_reassigned(self):
        self.assert_equal(PACKET_STATUS.REASSIGNED, "ra")
        self.assert_in("ra", PACKET_STATUS.values())

    def test_bundle_model_accepts_reassign_flags(self):
        bundle = Bundle(
            packets=[],
            documents=[],
            allow_signer_reassign=True,
            allow_chained_signer_reassign=False,
        )
        self.assert_equal(bundle.allow_signer_reassign, True)
        self.assert_equal(bundle.allow_chained_signer_reassign, False)
