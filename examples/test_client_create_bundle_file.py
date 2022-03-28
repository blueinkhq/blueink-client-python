from src.BlueInkClient.blueinkclient import Client
from src.BlueInkClient.model.bundles import BundleBuilder

# This will pull from environment vars
client = Client()

print("\n*********************")
print("Bundle Creation via file upload")
bundleBuilder = BundleBuilder(label="label2022",
                              email_subject="Subject",
                              email_message="MessageText",
                              is_test=True)

bundleBuilder.add_cc("Homer.Simpson@example.com")

doc_id1 = bundleBuilder.add_document_by_path("fw9-1","fw9.pdf","application/pdf")
signer_id1 = bundleBuilder.add_signer("Homer Simpson", "Homer.Simpson@example.com", "505-555-5555", False, True, True, "email")
signer_id2 = bundleBuilder.add_signer("Marge Simpson", "Marge.Simpson@example.com", "505-555-5556", False, True, True, "email")
bundleBuilder.add_field_to_document(doc_id1, "inp", "inp-name", "label", 1, 15, 60, 20, 3, "email", 2, 30, [signer_id1, signer_id2])
bundleBuilder.add_field_to_document(doc_id1, "sig", "sig-01", "signature", 1, 15, 68, 30, 12, "email", 2, 30, [signer_id1])

doc_id2 = bundleBuilder.add_document_by_path("fw9-2","fw9.pdf","application/pdf")
bundleBuilder.add_field_to_document(doc_id2, "inp", "inp-name", "label2", 1, 15, 60, 20, 3, "email", 2, 30, [signer_id1, signer_id2])

result = client.bundles.create(bundleBuilder)
print(f"Result: {result.status}: {result.data}")