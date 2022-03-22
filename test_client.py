from blueinkclient import Client
from model.bundles import BundleBuilder
from requests import Response

# This will pull from environment vars
client = Client()

# # These test pagination. Collects IDs
# print("Paged Bundle Listing")
# ids = []
# for api_call in client.bundles.list_iter(start_page=1, per_page=5):
#     print(f"Paged Call: {api_call.data}")
#     for bundle in api_call.data:
#         ids.append(bundle.id)
# print(f"Found {len(ids)} bundle ids!")
# print("")
# print(f"Single bundle retrieval, id {ids[0]}")
# if len(ids) > 0:
#     single_bundle = client.bundles.retrieve(ids[0])
#     if single_bundle.status == 200:
#         print(single_bundle.data)
#
# for api_call in client.persons.list_iter(start_page=1, per_page=2):
#     print(f"Persons Call: {api_call.data}")
#
# for api_call in client.templates.list_iter(start_page=1, per_page=2):
#     print(f"Template Call: {api_call.data}")
# print("")
# print("")

print("Bundle Creation")
bundleBuilder = BundleBuilder(label="label",
                              email_subject="Subject",
                              is_test=True)
bundleBuilder.add_cc("Homer.Simpson@example.com")

doc_id = bundleBuilder.add_document("w9", "https://www.irs.gov/pub/irs-pdf/fw9.pdf")
signer_id1 = bundleBuilder.add_signer("Homer Simpson", "Homer.Simpson@example.com", "505-555-5555", False, True, True, "email")
signer_id2 = bundleBuilder.add_signer("Marge Simpson", "Marge.Simpson@example.com", "505-555-5556", False, True, True, "email")
bundleBuilder.add_field_to_document(doc_id, "inp", "inp-name", "label", 1, 15, 60, 20, 3, "email", 2, 30, [signer_id1, signer_id2])
bundleBuilder.add_field_to_document(doc_id, "sig", "sig-01", "signature", 1, 15, 68, 30, 12, "email", 2, 30, [signer_id1])

template_id = bundleBuilder.add_document_template("doc-02", "template-id000")
bundleBuilder.assign_signer(template_id, signer_id1, "customer1")
bundleBuilder.assign_signer(template_id, signer_id2, "customer2")
bundleBuilder.set_value(template_id, "var1", "val1")
bundleBuilder.set_value(template_id, "var2", "val2")

json = bundleBuilder.build()

print(f"BundleJSON: {json}")
result = client.bundles.create(json)
print(f"Result: {result.status}: {result.data}")

# jsonfile = open(file="bundle.json",mode='w')
# jsonfile.write(str(bundle))
