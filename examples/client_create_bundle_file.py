from src.blueink.client import Client

# This will pull from environment vars
from src.blueink.constants import DELIVER_VIA, FIELD_KIND
from src.blueink.model.bundles import BundleHelper

client = Client()

print("\n*********************")
print("Bundle Creation via file upload")
bh = BundleHelper(label="label2022",
                  email_subject="Subject",
                  email_message="MessageText",
                  is_test=True)

bh.add_cc("Homer.Simpson@example.com")

doc1 = bh.add_document_by_path("fw4.pdf", "application/pdf")
signer1 = bh.add_signer(name="Homer Simpson",
                        email="Homer.Simpson@example.com",
                        phone="505-555-5555",
                        deliver_via=DELIVER_VIA.EMAIL)
signer2 = bh.add_signer(name="Marge Simpson",
                        email="Marge.Simpson@example.com",
                        phone="505-555-5556",
                        deliver_via=DELIVER_VIA.EMAIL)
field1 = bh.add_field(document=doc1,
                      x=1, y=15, w=60, h=20, p=3,
                      kind=FIELD_KIND.INPUT,
                      label="label1",
                      editors=[signer1, signer2])
field2 = bh.add_field(document=doc1,
                      x=1, y=15, w=68, h=30, p=4,
                      kind=FIELD_KIND.ESIGNATURE,
                      label="label2",
                      editors=[signer1])

doc2 = bh.add_document_by_path("fw4.pdf", "application/pdf")
field3 = bh.add_field(document=doc2,
                         x=1, y=15, w=60, h=20, p=3,
                         kind=FIELD_KIND.INPUT,
                         label="label3",
                         editors=[signer1, signer2])

result = client.bundles.create_from_bundle_helper(bh)
print(f"Result: {result.status}: {result.data}")
