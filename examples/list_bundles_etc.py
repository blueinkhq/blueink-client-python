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
iterator = client.bundles.paged_list(page=1, per_page=5, status=constants.BUNDLE_STATUS.COMPLETE)
for paged_response in iterator:
    print(f"Page {page}, {len(paged_response.data)} Bundles")
    for bundle in paged_response.data:
        ids.append(bundle.id)
    page += 1
print(f"Found {len(ids)} bundle ids!")
print("")

if len(ids) > 0:
    print(f"---> Single bundle retrieval, id {ids[0]}")
    response = client.bundles.retrieve(ids[0], related_data=True)
    single_bundle = response.data
    print(f"{single_bundle.id}: {single_bundle.status}")

print("\n*********************\nPaged Persons Listing")
page = 1
for paged_response in client.persons.paged_list(page=1, per_page=2):
    print(f"Page {page}, {len(paged_response.data)} Persons")
    page += 1

print("\n*********************\nPaged Templates Listing")
page = 1
for paged_response in client.templates.paged_list(page=1, per_page=2):
    print(f"Page {page}, {len(paged_response.data)} Templates")
    page += 1
