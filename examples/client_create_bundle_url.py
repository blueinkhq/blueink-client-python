from src.blueink.client import Client
from src.blueink.constants import FIELD_KIND, DELIVER_VIA
from src.blueink.model.bundles import BundleHelper

print("\n*********************")
print("Bundle Creation via URL")
bh = BundleHelper(label="label2022",
                  email_subject="Subject",
                  email_message="MessageText",
                  is_test=True)
bh.add_cc("Homer.Simpson@example.com")
document = bh.add_document_by_url("https://www.irs.gov/pub/irs-pdf/fw9.pdf")
signer1 = bh.add_signer(name="Homer Simpson",
                        email="Homer.Simpson@example.com",
                        phone="505-555-5555",
                        deliver_via=DELIVER_VIA.EMAIL)
signer2 = bh.add_signer(name="Marge Simpson",
                        email="Marge.Simpson@example.com",
                        phone="505-555-5556",
                        deliver_via=DELIVER_VIA.EMAIL)

field1_id = bh.add_field(document=document,
                         x=1, y=15, w=60, h=20, p=3,
                         kind=FIELD_KIND.INPUT,
                         label="label1",
                         editors=[signer1, signer2])
field2_id = bh.add_field(document=document,
                         x=1, y=15, w=68, h=30, p=4,
                         kind=FIELD_KIND.ESIGNATURE,
                         label="label2",
                         editors=[signer1])

client = Client()
result = client.bundles.create_from_bundle_helper(bh)
print(f"Result: {result.status}: {result.data}")
