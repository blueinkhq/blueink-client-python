from src.blueink import BundleHelper, Client, constants

# Create a BundleHelper instance, and initialize some basic settings on the Bundle
bh = BundleHelper(label="Test Bundle 01",
                  email_subject="Please sign this test bundle",
                  email_message="Here is a test bundle. Please sign it.",
                  is_test=True)

# Add a CC recipient, that will receive a copy of the completed docs
bh.add_cc("bart.simpson@example.com")

# Add a document to the Bundle by providing a publicly accessible URL where
# the Blueink platform can download the document to include in the Bundle
doc_key = bh.add_document_by_path("fw2.pdf")

signer1_key = bh.add_signer(
    name="Homer Simpson",
    email="homer.simpson@example.com",
)

signer2_key = bh.add_signer(
    name="Marge Simpson",
    email="marge.simpson@example.com",
)

# Add a field that both signers can edit
bh.add_field(
    document_key=doc_key,
    x=1, y=15, w=60, h=20, p=3,
    kind=constants.FIELD_KIND.INPUT,
    label="Please enter some text",
    editors=[signer1_key, signer2_key]
)

# Add a signature field for signer1
bh.add_field(
    document_key=doc_key,
    x=1, y=15, w=68, h=30, p=4,
    kind=constants.FIELD_KIND.ESIGNATURE,
    label="Sign Here",
    editors=[signer1_key]
)

client = Client()
response = client.bundles.create_from_bundle_helper(bh)
print(f"Status: {response.status}. Created bundle with ID {response.data.id}")
