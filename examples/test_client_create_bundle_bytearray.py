from src.blueink.client import Client
from src.blueink.model.bundles import BundleHelper


pdf_bytearray = bytearray()
with open("fw4.pdf", 'rb') as pdf_file:
    byte = pdf_file.read(1)
    while byte:
        pdf_bytearray += byte
        byte = pdf_file.read(1)


print("\n*********************")
print("Bundle Creation via file upload")
bh = BundleHelper(label="label2022b",
                  email_subject="Subject",
                  email_message="MessageText",
                  is_test=True)

bh.add_cc("Homer.Simpson@example.com")
doc_id1 = bh.add_document_by_bytearray("fw4-1", pdf_bytearray, "fw4.pdf", "application/pdf")
signer_id1 = bh.add_signer("Homer Simpson", "Homer.Simpson@example.com", "505-555-5555", False, True, True, "email")
signer_id2 = bh.add_signer("Marge Simpson", "Marge.Simpson@example.com", "505-555-5556", False, True, True, "email")
bh.add_field(doc_id1, "inp", "inp-name", "label", 1, 15, 60, 20, 3, "email", 2, 30, [signer_id1, signer_id2])
bh.add_field(doc_id1, "sig", "sig-01", "signature", 1, 15, 68, 30, 12, "email", 2, 30, [signer_id1])


# Make the post!
client = Client()
result = client.bundles.create_from_bundle_helper(bh)
print(f"Result: {result.status}: {result.data}")
