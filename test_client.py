from blueinkclient import Client
from requests import Response

# This will pull from environment vars
client = Client()

resp = client.bundles.list()
print(f"Single List: HTTP Response\nCode: {resp.http_response_code}\nBody: {resp.body}")

list_iter = client.bundles.list_iter(start_page=0,
                                     per_page=5)

print("Iters:")
for api_call in list_iter:
    print(api_call.api_response.body)
