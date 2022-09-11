# blueink-client-python
A Python client library for the BlueInk API.

## Installation
To install this library, run the following command:
```bash
pip install blueink-client-python
```

## Usage
Usage is super simple. To use this code, you have a few choices regarding URL and your private API key.

By default the client will search for two environment variables. On Linux and MacOS you will need to include ```BLUEINK_API_URL``` and ```BLUEINK_PRIVATE_API_KEY``` in your .bashrc (or equivalent) shell config script. On Windows, you will need to add two environment variables through either the UI or the command prompt. 

If this does not suit you, the client constructor also accepts two override parameters for these either positionally or using kwargs. By default the URL will go to ```https://api.blueink.com/api/v2``` so you can simply input your API key. It is, however, strongly suggested that you use environmental variables as to not hardcode any credentials.

The client can be imported using the following import statement. Initializing a client is a one-liner:
```python
from blueink import Client

client = Client()
# or, positionally:
client = Client("https://example.com/api", "YOUR_PRIVATE_API_KEY")
# or, kwargs style (default URL is https://api.blueink.com/api/v2)
client = Client(override_private_api_key="YOUR_PRIVATE_API_KEY")
```

Client calls all return a "MunchedResult" where any data from the HTTP response is dot-accessible. 

For a call: 
```python
response = client.example.retrieve(0)
```

Say for instance you get back JSON:
```json
{
  "title": "This is a title",
  "text": "This is body text"
}
```

This json would be accessible similarly to a dot-dict, eg:
```python
title = response.data.title
print(title)
##OUT: "This is a title"
```



### Bundles
#### Creation
Bundles can be easily created using the ```BundleHelper``` class. Using the BundleBuilder class you can either specify a URL for documents, include a file for document upload, or include a bytearray for your document.

Below is an example of using a URL for a document:

```python
from src.blueink.client import Client
from src.blueink.constants import FIELD_KIND, DELIVER_VIA
from src.blueink.model.bundles import BundleHelper

print("\n*********************")
print("Bundle Creation via URL")
bh = BundleHelper(label="label2022",
                  email_subject="Subject",
                  email_message="MessageText",
                  is_test=True)
bh.add_cc("Homer.Simpson@example.com")
document = bh.add_document_by_url("https://www.irs.gov/pub/irs-pdf/fw9.pdf")
signer1 = bh.add_signer(name="Homer Simpson",
                        email="Homer.Simpson@example.com",
                        phone="505-555-5555",
                        deliver_via=DELIVER_VIA.EMAIL)
signer2 = bh.add_signer(name="Marge Simpson",
                        email="Marge.Simpson@example.com",
                        phone="505-555-5556",
                        deliver_via=DELIVER_VIA.EMAIL)

field1 = bh.add_field(document=document,
                         x=1, y=15, w=60, h=20, p=3,
                         kind=FIELD_KIND.INPUT,
                         label="label1",
                         editors=[signer1, signer2])
field2 = bh.add_field(document=document,
                         x=1, y=15, w=68, h=30, p=4,
                         kind=FIELD_KIND.ESIGNATURE,
                         label="label2",
                         editors=[signer1])

client = Client()
result = client.bundles.create_from_bundle_helper(bh)
print(f"Result: {result.status}: {result.data}")
```

If you were to use a file, you supply a path and content type instead of a URL:
```python
document = bh.add_document_by_path("fw4.pdf", "application/pdf")
```

If you are not coming from a filesystem (perhaps you're pulling from a DB client), you might have a bytearray object. Below, you have the bytearray and filename ```fw9.pdf```
```python
document = bh.add_document_by_bytearray(pdf_bytearray, "fw4.pdf", "application/pdf")
```
#### Retrieval
Getting a single bundle is fairly easy. They can be accessed with a single call. To get the additional data (events, files, data), set the related_data flag to True.

```python
response = client.bundles.retrieve(bundle_id, related_data=True)
bundle = response.data
bundleid = bundle.id

# additional data fields (only exist if related_data==True)
events = bundle.events
files = bundle.files
data = bundle.data

```
#### Listing
Listing has several options regarding pagination. You can also choose to append the additional data on each retrieved bundle as you can with single fetches. ```client.bundles.paged_list()``` returns an iterator object that lazy loads subsequent pages. If no parameters are set, it will start at page 0 and have up to 50 bundles per page.

```python
# EXAMPLE: Collecting all bundle IDs
ids = []
for api_call in client.bundles.paged_list(start_page=1, per_page=5, related_data=True):
    print(f"Paged Call: {api_call.data}")
    for bundle in api_call.data:
        ids.append(bundle.id)
```
### Persons
Creating a person is similar to a creating a Bundle. There is a PersonHelper to help create a person
```python
import json
from copy import deepcopy
from requests.exceptions import HTTPError
from pprint import pprint

from blueink.client import Client
from blueink.person_helper import PersonHelper

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


```

### Packets
Packets can be updated. Reminders may be triggered, and COEs can be retrieve using the client:
```python
# Retrieve
client.packets.retrieve(packet_id)

# Update
client.packets.update(packet_id, packet_json)

# Remind
client.packets.remind(packet_id)

# Get COE
client.packets.retrieve_coe(packet_id)
```

### Templates
Templates can be listed (non-paged), listed (paged) or retrieved singly:

```python
# non paged
templates_list_response = client.templates.list()
# paged
for page in client.templates.paged_list():
    page.data  # templates in page
# single
template_response = client.templates.retrieve(template_id)


```