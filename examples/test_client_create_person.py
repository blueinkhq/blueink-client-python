import json

from src.blueink.client import Client
from src.blueink.model.persons import PersonHelper

from pprint import pprint

client = Client()

ph = PersonHelper()

# Make up some metadata to add to the person
metadata = {}
metadata["number"] = 1
metadata["string"] = "stringy"
metadata["dict"] = {}
metadata["dict"]["number"] = 2

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
result = client.persons.create_from_person_helper(ph)
pprint(f"Result Create: {result.status}: {result.data}")

# Delete the person from your account and check the result
result = client.persons.delete(result.data.id)

# pprint(f"Result Delete: {result.status}: {result.data}")
