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

all_emails = ph.add_email("test@email.com")
pprint(all_emails)
all_emails.append("test2@email.com")
all_emails = ph.set_emails(all_emails)
pprint(all_emails)

result = client.persons.create_from_person_helper(ph)
pprint(f"Result Create:\n {result.status}: {result.data}")


result = client.persons.delete(result.data.id)

pprint(f"Result Delete\n: {result.status}: {result.data}")
