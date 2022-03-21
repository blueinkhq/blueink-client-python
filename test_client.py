from blueinkclient import Client
from requests import Response

# This will pull from environment vars
client = Client()

for api_call in client.bundles.list_iter(start_page=1, per_page=2):
    print(f"Bundles Call: {api_call.body}")

for api_call in client.persons.list_iter(start_page=1, per_page=2):
    print(f"Persons Call: {api_call.body}")

for api_call in client.templates.list_iter(start_page=1, per_page=2):
    print(f"Template Call: {api_call.body}")