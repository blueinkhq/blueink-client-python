import sys
from pprint import pprint

from src.blueink import Client, constants, exceptions, BundleHelper

client = Client()

print("\n*********************")
print("Bundle Creation with a Template")
bh = BundleHelper(label="Example from Template",
                  email_subject="Here is your example Bundle",
                  email_message="Please sign. This bundle was created from a template",
                  is_test=True)

template_id = input("Please enter template ID: ")
# This will fail with an exception if the template ID does not exist
response = client.templates.retrieve(template_id)
template = response.data

doc_key = bh.add_document_template(template_id)

signer_key = bh.add_signer(name="Homer Simpson",
                        email="Homer.Simpson@example.com",
                        phone="505-555-5555",
                        deliver_via=constants.DELIVER_VIA.EMAIL)

bh.assign_role(doc_key, signer_key, template['roles'][0])

# FIXME - collect some initial data for fields

try:
    response = client.bundles.create_from_bundle_helper(bh)
except exceptions.HTTPError as e:
    print(f"Request failed: {e}")
    print("== Error Details: ==")
    try:
        pprint(e.response.json())
    except exceptions.JSONDecodeError:
        chars = 10000
        print(e.response.text[:chars])
        if len(e.response.text) > chars:
            print(f"\n== [TRUNCATED {len(e.response.text) - chars} characters] ==")
    sys.exit(1)
except exceptions.RequestException as e:
    print(f"Request failed: {e}")
    sys.exit(1)


print("== Bundle Created ==")
pprint(response.data)
