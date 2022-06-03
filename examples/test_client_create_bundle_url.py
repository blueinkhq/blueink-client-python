from src.blueink.client import Client
from src.blueink.model.bundles import BundleHelper

print("\n*********************")
print("Bundle Creation via URL")
bh = BundleHelper(label="label2022",
                  email_subject="Subject",
                  email_message="MessageText",
                  is_test=True)
bh.add_cc("Homer.Simpson@example.com")
doc_id1 = bh.add_document_by_url("w9", "https://www.irs.gov/pub/irs-pdf/fw9.pdf")
signer_id1 = bh.add_signer("Homer Simpson", "Homer.Simpson@example.com", "505-555-5555", False, True, True, "email")
signer_id2 = bh.add_signer("Marge Simpson", "Marge.Simpson@example.com", "505-555-5556", False, True, True, "email")
bh.add_field(doc_id1, "inp", "inp-name", "label", 1, 15, 60, 20, 3, "email", 2, 30, [signer_id1, signer_id2])
bh.add_field(doc_id1, "sig", "sig-01", "signature", 1, 15, 68, 30, 12, "email", 2, 30, [signer_id1])


client = Client()
result = client.bundles.create_from_bundle_helper(bh)
print(f"Result: {result.status}: {result.data}")
