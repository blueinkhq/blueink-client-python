from BlueInkClient import Client
from requests import Response

token_file = open("token.txt", 'r') # Expects plaintext token in this file. It's in .gitignore
assert token_file is not None, "Token File must exist for tests to run"

user_token = token_file.readline()
assert token_file is not None, "Token File must not be empty for tests to run"

client = Client(user_token=user_token)

resp = client.bundles.list()
print(f"HTTP Response\nCode: {resp.status_code}\nBody: {resp.content}")