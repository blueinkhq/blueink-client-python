from src.blueink.client import Client
from src.blueink.model.persons import PersonHelper

from pprint import pprint

client = Client()

print("\n*********************")
print("Create A Person")

ph = PersonHelper()

metadata = {}
metadata["number"] = 1
metadata["string"] = "stringy"
metadata["dict"] = {}
metadata["dict"]["number"] = 2

ph.set_metadata(metadata)
ph.set_name("New Name Deleted")

result = client.persons.create_from_person_helper(ph)
pprint(f"Result: {result.status}: {result.data}")


result = client.persons.delete(result.data.id)
result = client.persons.delete("123")
pprint(f"Result: {result.status}: {result.data}")
