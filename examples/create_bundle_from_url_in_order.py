import sys
from pprint import pprint

from src.blueink import BundleHelper, Client, constants, exceptions

print("\n*********************")
print("Bundle Creation via URL")
bh = BundleHelper(
    label="label2022",
    email_subject="Subject",
    email_message="MessageText",
    is_test=True,
    in_order=True,
)

bh.add_cc("Homer.Simpson@example.com")

doc1 = bh.add_document_by_url("https://www.irs.gov/pub/irs-pdf/fw9.pdf")

signer1 = bh.add_signer(
    name="Homer Simpson",
    email="Homer.Simpson@example.com",
    phone="505-555-5555",
    deliver_via=constants.DELIVER_VIA.EMAIL,
)

signer2 = bh.add_signer(
    name="Marge Simpson",
    email="Marge.Simpson@example.com",
    phone="505-555-5556",
    deliver_via=constants.DELIVER_VIA.EMAIL,
)

field1 = bh.add_field(
    doc1,
    x=1,
    y=15,
    w=60,
    h=20,
    p=3,
    kind=constants.FIELD_KIND.INPUT,
    label="label1",
    editors=[signer1, signer2],
)

field2 = bh.add_field(
    doc1,
    x=1,
    y=15,
    w=68,
    h=30,
    p=4,
    kind=constants.FIELD_KIND.ESIGNATURE,
    label="label2",
    editors=[signer1],
)

client = Client()

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
