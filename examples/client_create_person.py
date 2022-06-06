import json
from copy import deepcopy
from requests.exceptions import HTTPError
from pprint import pprint

from src.blueink.client import Client
from src.blueink.person_helper import PersonHelper

client = Client()

ph = PersonHelper()

# Try and create a person without setting anything up
#  this is expected to error
try:
    result = client.persons.create_from_person_helper(ph)
except HTTPError as e:
    print(e)
    pprint(e.response.text)
except Exception as e:
    print("Error:")
    print(e)

# Make up some metadata to add to the person
metadata = {}
metadata["number"] = 1
metadata["string"] = "stringy"
metadata["dict"] = {}
metadata["dict"]["number"] = 2
metadata["list"] = []
metadata["list"].append(3)

# Set the metadata of the person
ph.set_metadata(metadata)

# Set the persons name
ph.set_name("New Name")

# Add email contacts for the person
ph.add_email("test@email.com")
ph.add_email("test2@email.com")
ph.add_email("test3@email.com")

# Get all of the emails for the person
all_current_emails = ph.get_emails()

# Remove an email from the list
all_current_emails.remove("test@email.com")

# Overwrite the existing email list with this new list
#   Effectively removing test@email.com list
ph.set_emails(all_current_emails)

# Add phone number contact for the person
ph.add_phone("5055551212")
ph.add_phone("5055551213")
ph.add_phone("5055551214")

# Get all of the phone numbers for the person
all_current_phones = ph.get_phones()

# Remove a phone number from the list
all_current_phones.pop()

# Overwrite the existing email list with this new list
#   Effectively removing last phone number
ph.set_phones(all_current_phones)

# Create the person and check the result
try:
    result = client.persons.create_from_person_helper(ph)
    pprint(f"Result Create: {result.status}: {result.data}")
except HTTPError as e:
    print(e)
    pprint(e.response.text)
except Exception as e:
    print("Error:")
    print(e)

# Change the persons name and call update
result.data.name = "Second Name"

"""
 The channels in the response include both email and phone
  If we want to update with this data we need to remove the ones
  that are blank
"""
new_channels = []
for channel in result.data.channels:
    new_channel = deepcopy(channel)
    for key, value in channel.items():
        # Remove the key/value pairs that are not valid
        if not value:
            new_channel.pop(key)
    new_channels.append(new_channel)

# Set the channels to the recreated channels without the invalid keys
result.data.channels = new_channels

try:
    result = client.persons.update(result.data.id, result.data)
    pprint(f"Result Update: {result.status}: {result.data}")
except HTTPError as e:
    print(e)
    pprint(e.response.text)
except Exception as e:
    print("Error:")
    print(e)


# Retrieve the person
try:
    result = client.persons.retrieve(result.data.id)
    pprint(f"Result Retrieve: {result.status}: {result.data}")
except HTTPError as e:
    print(e)
    pprint(e.response.text)
except Exception as e:
    print("Error:")
    print(e)


# Perform a partial update to change the name again
third_name = {"name": "Third Name"}
try:
    result = client.persons.partial_update(result.data.id, third_name)
    pprint(f"Result Partial Update: {result.status}: {result.data}")
except HTTPError as e:
    print(e)
    pprint(e.response.text)
except Exception as e:
    print("Error:")
    print(e)

# Delete the person from your account and check the result
try:
    result = client.persons.delete(result.data.id)
    pprint(f"Result Delete: {result.status}: {result.data}")
except HTTPError as e:
    print(e)
    pprint(e.response.text)
except Exception as e:
    print("Error:")
    print(e)

"""
Create a person and pass extra arguments
if using a older version of sdk that doesn't
support certain new API parameters you can add them
this way in the person helper
If calling another method that just takes a dict
add them to the dict directly
"""
try:
    ph = PersonHelper(name="New Person")
    result = client.persons.create_from_person_helper(ph, hidden_person=True)
    pprint(f"Result Create With Extra Args: {result.status}: {result.data}")
    result = client.persons.delete(result.data.id)
    pprint(f"Result Delete: {result.status}: {result.data}")
except HTTPError as e:
    print(e)
    pprint(e.response.text)
except Exception as e:
    print("Error:")
    print(e)
