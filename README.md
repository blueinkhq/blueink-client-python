# blueink-client-python
A Python client library for the BlueInk API.

## Installation
To install this library, run the following command:
```bash
pip install blueinkclient
```

## Usage
Usage is super simple. To use this code, you have a few choices regarding URL and your private API key.

By default the client will search for two environment variables. On Linux and MacOS you will need to include ```BLUEINK_API_URL``` and ```BLUEINK_PRIVATE_API_KEY``` in your .bashrc (or equivalent) shell config script. On Windows, you will need to add two environment variables through either the UI or the command prompt. 

If this does not suit you, the client constructor also accepts two override parameters for these either positionally or using kwargs. By default the URL will go to ```https://api.blueink.com/api/v2``` so you can simply input your API key. It is, however, strongly suggested that you use environmental variables as to not hardcode any credentials.

The client can be imported using the following import statement. Initializing a client is a one-liner:
```python
from BlueInkClient.client import Client

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
Bundles can be easily created using the ```BundleBuilder``` class. Using the BundleBuilder class you can either specify a URL for documents, include a file for document upload, or include a bytearray for your document.

Below is an example of using a URL for a document:

```python
from BlueInkClient.client import Client
from BlueInkClient.model.bundles import BundleHelper

bh = BundleHelper(label="label2022",
                  email_subject="Subject",
                  email_message="MessageText",
                  is_test=True)
bh.add_cc("Homer.Simpson@example.com")
doc_id1 = bh.add_document_by_url("w9", "https://www.irs.gov/pub/irs-pdf/fw9.pdf")
signer_id1 = bh.add_signer("Homer Simpson", "Homer.Simpson@example.com", "505-555-5555", False, True, True,
                           "email")
signer_id2 = bh.add_signer("Marge Simpson", "Marge.Simpson@example.com", "505-555-5556", False, True, True,
                           "email")
bh.add_field(doc_id1, "inp", "inp-name", "label", 1, 15, 60, 20, 3, "email", 2, 30,
             [signer_id1, signer_id2])
bh.add_field(doc_id1, "sig", "sig-01", "signature", 1, 15, 68, 30, 12, "email", 2, 30,
             [signer_id1])

client = Client()
result = client.bundles.create_from_bundle_helper(bh)
```

If you were to use a file, you supply a path and content type instead of a URL:
```python
doc_id1 = bh.add_document_by_path("fw9-1","fw9.pdf","application/pdf")
```

If you are not coming from a filesystem (perhaps you're pulling from a DB client), you might have a bytearray object. Below, you have the bytearray and filename ```fw9.pdf```
```python
doc_id1 = bh.add_document_by_bytearray("fw9-1",pdf_bytearray, "fw9.pdf", "application/pdf")
```
#### Retrieval
Getting a single bundle is fairly easy. They can be accessed with a single call. To get the additional data (events, files, data), set the getAdditionalData flag to True.

```python
response = client.bundles.retrieve(bundle_id, getAdditionalData=True)
bundle = response.data
bundleid = bundle.id

# additional data fields (only exist if getAdditionalData==True)
events = bundle.events
files = bundle.files
data = bundle.data

```
#### Listing
Listing has several options regarding pagination. You can also choose to append the additional data on each retrieved bundle as you can with single fetches. ```client.bundles.pagedList()``` returns an iterator object that lazy loads subsequent pages. If no parameters are set, it will start at page 0 and have up to 50 bundles per page.

```python
# EXAMPLE: Collecting all bundle IDs
ids = []
for api_call in client.bundles.pagedlist(start_page=1, per_page=5, getAdditionalData=True):
    print(f"Paged Call: {api_call.data}")
    for bundle in api_call.data:
        ids.append(bundle.id)
```
### Persons
Creating a person record is simpler than creating or updating a bundle. There is no current 'builder' for this record. Instead, pass in the raw JSON data to the following client calls:
```python
client.persons.create(json_string)
client.persons.update(json_string)
client.persons.partial_update(json_string)
```

To delete a person record, one only needs the ID from the record:
```python
client.persons.delete(person_id)
```

### Packets
Packets can be updated. Reminders may be triggered, and COEs can be retrieve using the client:
```python
# Retrieval
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
for page in client.templates.pagedlist():
    page.data # templates in page
# single
template_response = client.templates.retrieve(template_id)


```