# blueink-client-python
![Tests](https://github.com/blueinkhq/blueink-client-python/actions/workflows/helper-tests.yml/badge.svg)
![Style Checks](https://github.com/blueinkhq/blueink-client-python/actions/workflows/style-checks.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/blueink-client-python.svg)](https://pypi.org/project/blueink-client-python/)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

A Python client library for the BlueInk eSignature API.

## Overview

This README provides a narrative overview of using the Blueink Python client, and
includes examples for many common use cases.

Additional resources that might be useful include:

* Examples at [blueink-client-python-examples](https://github.com/blueinkhq/blueink-client-python-examples)
repo on GitHub.
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

The Client also has two modes of operations. By default the Client will raise HTTPError
exceptions whenever there's an issue between the client and server (eg. HTTP4xx,
HTTP5xx errors). These come from the `requests` module. If within your application
you already handle exceptions coming out of `requests` then you should be good.
If you set `raise_exceptions = False` then these  will be returned as
`NormalizedResponse` objects which are also used for successful communications. See
below for information about these objects.

```python
# In your python code, create an instance of the blueink Client
from blueink import Client

client = Client(raise_exceptions=False)
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
 * `webhooks`

 The methods correspond to common REST operations:
 * `list()`
 * `retrieve()`
 * `create()`
 * `update()`
 * `delete()`

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

  The json data returned via the API call is accessible via the `data` attribute. The
  `data` attribute supports dictionary access and dot-notation access (for convenience
  and less typing).

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
  the Python Requests library, it's accessible as `original_response`.

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

See "Requests that Return Lists > Pagination" below.

### Requests that Return Lists

#### Filtering and Searching

Some Blueink [API endpoints](https://blueink.com/r/api-docs/) support searching and / or
filtering. In those cases, you can pass querystring parameters to the `list(...)` or
`paged_list(...)` method on those resources.

For example:

```python
from blueink import Client, constants

client = Client()

# Retrieve Bundles with a status of "Complete"
response = client.bundles.list(status=constants.BUNDLE_STATUS.COMPLETE)
complete_bundles = response.data

# Retrieve Bundles with a status or "Complete" or "Started"
statuses = ",".join([
    constants.BUNDLE_STATUS.COMPLETE,
    constants.BUNDLE_STATUS.STARTED
])
response = client.bundles.list(status__in=statuses)
complete_or_started_bundles = response.data

# Retrieve Bundles matching a search of "example.com" (which will match signer email
# addresses). We can pass pagination parameters too.
response = client.bundles.list(per_page=10, page=2, search="example.com")
matching_bundles = response.data

# Filtering / searching works with pagination iterators / paged_list() calls as well
iterator = client.bundles.paged_list(search="example.com")
for paged_response in iterator:
    for bundle in paged_response.data:
        print(bundle.id)
```

#### Pagination

Blueink API calls that return a list of results are paginated - ie, if there
are a lot of results, you need to make multiple requests to retrieve all of those
results, including a `page_number` parameter (and optionally a `page_size` parameter)
in each request.

The details of Blueink pagination scheme can be found in the
[API documentation](https://blueink.com/r/api-docs/pagination/):

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

## Client Method Index
Parameters can be found using autocomplete within your IDE. Creates/Updates take a
Python dictionary as the data field, unless special named methods like
```create_from_bundle_helper``` indicate otherwise. List methods can take query params
as kwargs.

### Bundle Related
* Create via ```client.bundles.create(...)``` or ```client.bundles.create_from_bundle_helper(...)```
* List via ```client.bundles.list(...)``` or ```client.bundles.paged_list(...)```
* Retrieve via ```client.bundles.retrieve(...)```
* Cancel via ```client.bundles.cancel(...)```
* List Events via ```client.bundles.list_events(...)```
* List Files via ```client.bundles.list_files(...)```
* List Data via ```client.bundles.list_data(...)```

### Person Related
* Create via ```client.persons.create(...)``` or ```client.persons.create_from_person_helper(...)```
* List via ```client.persons.list(...)``` or ```client.persons.paged_list(...)```
* Retrieve via ```client.persons.retrieve(...)```
* Delete via ```client.persons.delete(...)```
* Update via ```client.persons.update(...)```

### Packet Related
* Update via ```client.packets.update(...)```
* Create Embedded Signing URL via ```client.packets.embed_url(...)```
* Retrieve COE via ```client.packets.retrieve_coe(...)```
* Remind via ```client.packets.remind(...)```

### Template Related
* List via ```client.templates.list(...)``` or ```client.templates.paged_list(...)```
* Retrieve via ```client.templates.retrieve(...)```

### Webhook Related

#### Webhook Client Methods
* Create via ```client.webhooks.create(...)```
* List via ```client.webhooks.list(...)```
* Retrieve via ```client.webhooks.retrieve(...)```
* Delete via ```client.webhooks.delete(...)```
* Update via ```client.webhooks.update(...)```

#### WebhookExtraHeader Client Methods
* Create via ```client.webhooks.create_header(...)```
* List via ```client.webhooks.list_headers(...)```
* Retrieve via ```client.webhooks.retrieve_header(...)```
* Delete via ```client.webhooks.delete_header(...)```
* Update via ```client.webhooks.update_header(...)```

#### WebhookEvent Client Methods
* List via ```client.webhooks.list_events(...)```
* Retrieve via ```client.webhooks.retrieve_event(...)```

#### WebhookDelivery Client Methods
* List via ```client.webhooks.list_deliveries(...)```
* Retrieve via ```client.webhooks.retrieve_delivery(...)```

## Detailed Guide and Examples

### Bundles

#### Creating Bundles with the BundleHelper

When creating a Bundle via the API, you need to pass quite a bit of data in the
`client.bundle.create(...)` request. To ease the construction of that data, this
library provides a `BundleHelper` class.

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
# the Blueink platform can download the document to include in the Bundle
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

# 0) Add a document using a URL to a web resource:
doc0_key = bh.add_document_by_url("https://www.example.com/example.pdf")

# 1) Add a document using a path to the file in the local filesystem
doc1_key = bh.add_document_by_path("/path/to/file/example.pdf")

# 2) Add a document using a UTF-8 encoded Base64 string:
filename, pdf_b64 = read_a_file_into_b64_string()
doc02_key = bh.add_document_by_b64(filename, pdf_b64)

# 3) Add a document that you have already read into a Python bytearray object
filename, pdf_bytearray = read_a_file_into_bytearray()
doc03_key = bh.add_document_by_bytearray(filename, pdf_bytearray)

# 4) Add a document as a File object. Make sure to use 'with' or suitably close the file
#    after creating the document.
with open("/path/to/file/example.pdf", 'rb') as file:
    doc04_key = bh.add_document_by_file(file)
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
    result = client.persons.update(result.data.id, third_name, True)
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
### Webhooks

Webhooks can be interacted with via several methods. Webhooks also have related objects, such as
```WebhookExtraHeaders```, ```WebhookEvents```, and ```WebhookDeliveries``` which have their own
methods to interact with.

```python
from copy import deepcopy

from requests import HTTPError
from src.blueink import Client
from src.blueink.constants import EVENT_TYPE

WEBHOOK_01 = {
    "url": "https://www.example.com/01/",
    "enabled": True,
    "json": True,
    "event_types": [
        EVENT_TYPE.EVENT_BUNDLE_LAUNCHED,
        EVENT_TYPE.EVENT_BUNDLE_COMPLETE,
    ]
}

WEBHOOK_01_UPDATE = {
    "enabled": False,
    "event_types": [
        EVENT_TYPE.EVENT_PACKET_VIEWED
    ]
}

WEBHOOK_01_EXTRA_HEADER_A = {
    "name": "Courage_The_Cowardly_Webhook",
    "value": "Muriel Bagge",
    "order": 0,
}

client = Client()

# --------------
# Attempt posting a new Webhook
# --------------
try:
    create_resp = client.webhooks.create(data=WEBHOOK_01)
    webhook = create_resp.data
    print(f"Created webhook {webhook.id}")
except HTTPError as e:
    print("Error Creating Webhook: ")
    print(e)

# --------------
# Update Webhook
# --------------
try:
    update_resp = client.webhooks.update(webhook.id, WEBHOOK_01_UPDATE)
    webhook = update_resp.data
    print(f"Updated webhook {webhook.id}")
except HTTPError as e:
    print("Error Updating Webhook: ")
    print(e)

# --------------
# Create and add an ExtraHeader to the above Webhook
# --------------
extra_header_data = deepcopy(WEBHOOK_01_EXTRA_HEADER_A)
extra_header_data["webhook"] = webhook.id
try:
    header_create_resp = client.webhooks.create_header(data=extra_header_data)
    header = header_create_resp.data
    print(f"Added ExtraHeader {header} to {webhook.id}")
except HTTPError as e:
    print("Error Creating ExtraHeader: ")
    print(e)


# --------------
# List Webhooks
# --------------
try:
    list_resp = client.webhooks.list()
    webhook_list = list_resp.data

    print(f"Found {len(webhook_list)} Webhooks")
    for wh in webhook_list:
        print(f" - Webhook ID: {wh.id} to {wh.url}")


except HTTPError as e:
    print("Error Listing Webhooks: ")
    print(e)

# --------------
# Delete webhook
# --------------
try:
    delete_resp = client.webhooks.delete(webhook.id)
    print(f"Deleted Webhook {webhook.id}")
except HTTPError as e:
    print(f"Error Deleting Webhooks {webhook.id}")
    print(e)
```
