# blueink-client-python

A Python client library for the BlueInk eSignature API.

## Overview

This README provides a narrative overview of using the Blueink Python client, and
includes examples for many common use cases. 

Additional resources that might be useful include:

* Examples in the `examples/` directory of this repository
* The detailed [Blueink API Documentation](https://blueink.com/r/api-docs/), for
  details on the data returned by each API call.

For detailed documentation for each method call, please consult the source code,
or rely on auto-complete in your favorite editor / IDE. The code is well commented and
includes Python type annotations, which most IDEs understand.


## Installation

To install this library, run the following command:

```bash
pip install blueink-client-python
```

## Basic Usage

Requests to the Blueink API are made via an instance of the `blueink.Client` class. The
`blueink.Client` needs a Blueink private API key. By default the Client looks for
the private key in an environment variable named `BLUEINK_PRIVATE_API_KEY`. 

```bash
# In your shell, or in .bashrc or similar
export BLUEINK_PRIVATE_API_KEY=YOUR_PRIVATE_API_KEY_HERE
```

```python
# In your python code, create an instance of the blueink Client
from blueink import Client

client = Client()
```

Setting the private key via the environment is strongly recommended (to avoid
the possiblity of hard-coding your private key in your source code). However, you
can also pass the private key when instantiating a Client, like so:


```python
from blueink import Client

client = Client("YOUR_PRIVATE_API_KEY")
```

### Making API Calls

Making API calls with a client instance is easy. For example, to retrieve a list of
Bundles, do:

```python
response = client.bundles.list()

bundles = response.data
for bundle in bundles:
  print(bundle.id)
```

The Client class follows a RESTful pattern for making API calls, like so: 
`client.[resource].[method]`.

The supported "resources" are:
 * `bundles`
 * `persons`
 * `packets` 
 * `templates`

 The methods correspond to common REST operations: 
 * `list`
 * `retrieve`
 * `create`
 * `update`
 * `delete`.

However, note that:
* Not all resources support all methods. 
* Some resources support one-off methods that are unique to that resource. 
  For example the `bundles` resource allows you to retrieve a list of events on 
  the Bundle by calling `client.bundles.list_events()`.

Detailed documentation for each resource is below.

### Responses

API calls return a `NormalizedResponse` instance. The `NormalizedResponse` provides
the following attributes.

* **response.data**

  The json data returned via the API call is accessible via the data attribute. The data
  attribute supports dictionary access and dot-notation access (for convenience and less
  typing)

  ```python
  response = client.bundles.retrieve("some bundle ID")
  
  bundle_data = response.data
  print(bundle_data['id'])  # dictionary-style access
  print(bundle_data.id)     # dot notation access
  ```
  
* **response.request**

  The request that led to this response. Under-the-hood, the Blueink client library
  uses the [Python Requests Library](https://requests.readthedocs.io/). `response.request`
  is an instance of `requests.PreparedRequest`.

* **response.original_response**

  Similarly, if you need access to the original response as returned by 
  Python Requests library, it's accessible as `original_response`.

* **response.pagination**

  Most API calls that return a list of data returned paginated results. If so, 
  information about the pagination is included in the `pagination` attribute. 

  Pagination Example:

  ```python
  response = client.persons.list()
  
  pagination = response.pagination
  print(pagination.page_number, ' - current page number')
  print(pagination.total_pages, ' - total pages')
  print(pagination.per_page, ' - results per page')
  print(pagination.total_results, ' - total results')
  ```

See [Lists and Pagination](lists-and-pagination) below.

### Lists and Pagination

Blueink API calls that return a list of results are paginated - ie, if there
are a lot of results, you need to make multiple requests to retrieve all of those 
results, including a page_number parameter (and optionally a page_size parameter) 
in each request.

The details of Blueink pagination scheme can be found in the 
[API documentation](/r/api-docs/pagination/):

This client library provides convenience methods to make looping over
paginated results easier. Whenever there is a `list()` method available for a resource,
there is a corresponding `paged_list()` method available that returns a
`PaginatedIterator` helper class to make processing the results easier. 

You can mostly ignore the details of how the `PaginatedIterator` works. Instead, here 
is an example of looping over a paginated set of Bundles:

```python
# Loop over all of the Bundles in your account, and print their IDs
iterator = client.bundles.paged_list()
for paged_response in iterator:
    pg = paged_response.pagination
    print(f"Fetched page {pg.page_number} of {pg.total_pages} total pages")

    for bundle in paged_response.data:
        print(bundle.id)
```

## Detailed Guide and Examples

### Bundles

#### Creating Bundles with the BundleHelper

When creating a Bundle via the API, you need to pass a lot of data in the 
`bundle.create(...)` request. This library provides a `BundleHelper` class to ease the
construction of that data. 

Below is an example of using `BundleHelper` to create a Bundle with 1 document,
and 2 signers. In this example, the uploaded document is specified via a URL.

```python
from blueink import BundleHelper, Client, constants

# Create a BundleHelper instance, and initialize some basic settings on the Bundle
bh = BundleHelper(label="Test Bundle 01",
                  email_subject="Please sign this test bundle",
                  email_message="Here is a test bundle. Please sign it.",
                  is_test=True)

# Add a CC recipient, that will receive a copy of the completed docs
bh.add_cc("bart.simpson@example.com")

# Add a document to the Bundle by providing a publicly accessible URL where
# Blueink can download the document to include in the Bundle
doc_key = bh.add_document_by_url("https://www.irs.gov/pub/irs-pdf/fw9.pdf")

signer1_key = bh.add_signer(
    name="Homer Simpson",
    email="homer.simpson@example.com",
)

signer2_key = bh.add_signer(
    name="Marge Simpson",
    email="marge.simpson@example.com",
)

# Add a field that both signers can edit
bh.add_field(
    document_key=doc_key,
    x=1, y=15, w=60, h=20, p=3,
    kind=constants.FIELD_KIND.INPUT,
    label="Please enter some text",
    editors=[signer1_key, signer2_key]
)

# Add a signature field for signer1
bh.add_field(
    document_key=doc_key,
    x=1, y=15, w=68, h=30, p=4,
    kind=constants.FIELD_KIND.ESIGNATURE,
    label="Sign Here",
    editors=[signer1_key]
)

client = Client()
response = client.bundles.create_from_bundle_helper(bh)
print(f"Status: {response.status}. Created bundle with ID {response.data.id}")
```

Using the `BundleHelper`, you can add files to a Bundle in multiple ways:

```python
bh = BundleHelper(...)

# Add a document using a path to the file in the local filesystem
doc1_key = bh.add_document_by_path("/path/to/file/fw4.pdf", "application/pdf")

# Add a document that you have already read into a Python bytearray object
pdf_bytearray = read_a_file_into_a_bytearray()
doc2_key = bh.add_document_by_bytearray(pdf_bytearray, "fw4.pdf", "application/pdf")
```


#### Retrieval

Getting a single bundle is fairly easy. They can be accessed with a single call. To get
the additional data (events, files, data), set the related_data flag to True.

```python
response = client.bundles.retrieve(bundle_id, related_data=True)
bundle = response.data
bundle_id = bundle.id

# additional data fields (only exist if related_data==True)
events = bundle.events
files = bundle.files
data = bundle.data

```

#### Listing

Listing has several options regarding pagination. You can also choose to append the
additional data on each retrieved
bundle as you can with single fetches. ```client.bundles.paged_list()``` returns an
iterator object that lazy loads
subsequent pages. If no parameters are set, it will start at page 0 and have up to 50
bundles per page.

```python
# EXAMPLE: Collecting all bundle IDs
ids = []
for api_call in client.bundles.paged_list(start_page=1, per_page=5, related_data=True):
    print(f"Paged Call: {api_call.data}")
    for bundle in api_call.data:
        ids.append(bundle.id)
```

### Persons

Creating a person is similar to a creating a Bundle. There is a PersonHelper to help
create a person

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

Packets can be updated. Reminders may be triggered, and COEs can be retrieve using the
client:

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
