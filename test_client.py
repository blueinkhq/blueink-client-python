from blueinkclient import Client
from model.bundles import BundleBuilder
from requests import Response

# This will pull from environment vars
client = Client()
#
# for api_call in client.bundles.list_iter(start_page=1, per_page=2):
#     print(f"Bundles Call: {api_call.body}")

# for api_call in client.persons.list_iter(start_page=1, per_page=2):
#     print(f"Persons Call: {api_call.body}")
#
# for api_call in client.templates.list_iter(start_page=1, per_page=2):
#     print(f"Template Call: {api_call.body}")

bundle = BundleBuilder(label="label",
                       in_order=False,
                       email_subj="Subject",
                       email_msg="Message Text",
                       requester_name="Johnny Rotten",
                       requester_email="Johnny.Rotten@example.com",
                       is_test=True) \
    .add_cc("Homer.Simpson@example.com") \
    .start_document("w9", "https://www.irs.gov/pub/irs-pdf/fw9.pdf") \
    .add_field_to_document("inp", "inp-name", "label", 1, 15, 60, 20, 3, "email", 2, 30, ["signer-1"]) \
    .add_field_to_document("sig", "sig-01", "signature", 1, 15, 68, 30, 12, "email", 2, 30, ["signer-1"]) \
    .end_document() \
    .add_signer("Homer Simpson", "Homer.Simpson@example.com", "555-555-5555", False, True, True, "signer-1", "email") \
    .build()

# client.bundles.create(bundle_json)
print(f" BundleJSON: {bundle}")

# jsonfile = open(file="bundle.json",mode='w')
# jsonfile.write(str(bundle_json))
