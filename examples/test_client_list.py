from src.BlueInkClient.client import Client

client = Client()

# # These test pagination. Collects IDs
print("\n*********************")
print("Paged Bundle Listing")
ids = []
for api_call in client.bundles.pagedlist(start_page=1, per_page=5, getAdditionalData=True):
    print(f"Paged Call: {api_call.data}")
    for bundle in api_call.data:
        ids.append(bundle.id)
print(f"Found {len(ids)} bundle ids!")
print("")
print(f"---> Single bundle retrieval, id {ids[0]}")
if len(ids) > 0:
    single_bundle = client.bundles.retrieve(ids[0], getAdditionalData=True)
    if single_bundle.status == 200:
        print(single_bundle.data)

print("\n*********************")
print("Paged Persons Listing")
for api_call in client.persons.pagedlist(start_page=1, per_page=2):
    print(f"Persons Call: {api_call.data}")

print("\n*********************")
print("Paged Templates Listing")
for api_call in client.templates.pagedlist(start_page=1, per_page=2):
    print(f"Template Call: {api_call.data}")