from src.blueink import Client, constants

client = Client()


print("\n*********************\nList Bundles")
response = client.bundles.list()
print(f"Retrieved {len(response.data)} Bundles")
print(f"Here are the first 3:")
for bundle in response.data[:3]:
    print(f"{bundle.id} {bundle.status}")

print("\n*********************\nList Bundles - filtering by status")
response = client.bundles.list(status=constants.BUNDLE_STATUS.COMPLETE)
print(f"Retrieved {len(response.data)} Complete Bundles")
print(f"Here are the first 2:")
for bundle in response.data[:3]:
    print(f"{bundle.id} {bundle.status}")

# These test pagination. Collects IDs
print("\n*********************\nPaged Bundle Listing")
ids = []
page = 1
for api_call in client.bundles.paged_list(start_page=1, per_page=5, status=constants.BUNDLE_STATUS.COMPLETE):
    # print(f"Paged Call: {api_call.data}")
    print(f"Page {page}, {len(api_call.data)} Bundles")
    for bundle in api_call.data:
        ids.append(bundle.id)
    page += 1
print(f"Found {len(ids)} bundle ids!")
print("")

print(f"---> Single bundle retrieval, id {ids[0]}")
if len(ids) > 0:
    single_bundle = client.bundles.retrieve(ids[0], related_data=True)
    print(f"{bundle.id}: {bundle.status}")

print("\n*********************\nPaged Persons Listing")
for api_call in client.persons.paged_list(start_page=1, per_page=2):
    print(f"Page {page}, {len(api_call.data)} Persons")

print("\n*********************\nPaged Templates Listing")
for api_call in client.templates.paged_list(start_page=1, per_page=2):
    print(f"Page {page}, {len(api_call.data)} Templates")
