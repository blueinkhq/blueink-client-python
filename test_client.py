from BlueInkClient import Client
from requests import Response

# This will pull from environment vars
client = Client()

resp = client.bundles.list()
print(f"HTTP Response\nCode: {resp.status_code}\nBody: {resp.content}")