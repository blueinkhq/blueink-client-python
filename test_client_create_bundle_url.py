from blueinkclient import Client
from model.bundles import BundleBuilder

print("\n*********************")
print("Bundle Creation via URL")
bundleBuilder = BundleBuilder(label="label2022",
                              email_subject="Subject",
                              email_message="MessageText",
                              is_test=True)
bundleBuilder.add_cc("Homer.Simpson@example.com")
doc_id1 = bundleBuilder.add_document("w9", "https://www.irs.gov/pub/irs-pdf/fw9.pdf")
signer_id1 = bundleBuilder.add_signer("Homer Simpson", "Homer.Simpson@example.com", "505-555-5555", False, True, True, "email")
signer_id2 = bundleBuilder.add_signer("Marge Simpson", "Marge.Simpson@example.com", "505-555-5556", False, True, True, "email")
bundleBuilder.add_field_to_document(doc_id1, "inp", "inp-name", "label", 1, 15, 60, 20, 3, "email", 2, 30, [signer_id1, signer_id2])
bundleBuilder.add_field_to_document(doc_id1, "sig", "sig-01", "signature", 1, 15, 68, 30, 12, "email", 2, 30, [signer_id1])

# template_id = bundleBuilder.add_document_template("doc-02", "template-id000")
# bundleBuilder.assign_signer(template_id, signer_id1, "customer1")
# bundleBuilder.assign_signer(template_id, signer_id2, "customer2")
# bundleBuilder.set_value(template_id, "var1", "val1")
# bundleBuilder.set_value(template_id, "var2", "val2")


client = Client()
result = client.bundles.create(bundleBuilder)
print(f"Result: {result.status}: {result.data}")
