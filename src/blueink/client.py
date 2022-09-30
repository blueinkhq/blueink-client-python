import io
import json
from os import environ
from typing import List

from munch import Munch

from . import endpoints
from .bundle_helper import BundleHelper
from .constants import (
    BUNDLE_STATUS,
    DEFAULT_BASE_URL,
    ENV_BLUEINK_API_URL,
    ENV_BLUEINK_PRIVATE_API_KEY
)
from .paginator import PaginatedIterator
from .person_helper import PersonHelper
from .request_helper import NormalizedResponse, RequestHelper


def _build_params(page: int = None, per_page: int = None, **query_params):
    params = dict(**query_params)
    if page is not None:  # page could be zero, although Blueink pagination is 1-indexed
        params["page"] = page

    if per_page:
        params["per_page"] = per_page

    return params


class Client:
    def __init__(self, private_api_key: str = None, base_url: str = None,
                 raise_exceptions: bool = True):
        """Initialize a Client instance to access the Blueink eSignature API

        Args:
            private_api_key: the private API key used to access the Blueink API.
                If no value is provided, then the environment is checked for a variable
                named "BLUEINK_PRIVATE_API_KEY".
            base_url: override the API base URL. If not supplied, we check the
                environment variable BLUEINK_API_URL. If that is empty, the default
                value of "https://api.blueink.com/api/v2" is used.
            raise_exceptions (Default True): raise HTTPError if code != 200. Otherwise
            return as NormalizedResponse objects.

        Returns:
            A Client instance

        Raises:
            ValueError if a private API key is neither passed during instantiation
            nor specified via the environment.
        """
        if not private_api_key:
            private_api_key = environ.get(ENV_BLUEINK_PRIVATE_API_KEY)

        if not private_api_key:
            raise ValueError(
                "A Blueink Private API Key must be provided on Client initialization"
                " or specified via the environment variable"
                " {ENV_BLUEINK_PRIVATE_API_KEY}"
            )

        if not base_url:
            base_url = environ.get(ENV_BLUEINK_API_URL)

        if not base_url:
            base_url = DEFAULT_BASE_URL

        self._request_helper = RequestHelper(private_api_key, raise_exceptions)

        self.bundles = self._Bundles(base_url, self._request_helper)
        self.persons = self._Persons(base_url, self._request_helper)
        self.packets = self._Packets(base_url, self._request_helper)
        self.templates = self._Templates(base_url, self._request_helper)

    class _SubClient:
        def __init__(self, base_url: str, requests_helper: RequestHelper):
            self._base_url = base_url
            self._requests = requests_helper

        def build_url(self, endpoint: str, **kwargs):
            """Shortcut to build a URL using endpoints.URLBuilder

            Args:
                endpoint: one of the API endpoints, e.g. endpoints.BUNDLES.create
                **kwargs: the arg name should be one of the keys in endpoints.
                interpolations, and the arg value will be substituted for the named
                placeholder in the endpoint str

            Returns:
                The URL as a str

            Raises:
                ValueError if one of the kwargs is not a valid endpoint
                interpolation key
            """
            # All of our current endpoints take 1 parameter, max
            if len(kwargs) > 1:
                raise ValueError('Only one interpolation parameter is allowed')

            try:
                url = endpoints.URLBuilder(self._base_url, endpoint).build(**kwargs)
            except KeyError:
                arg_name = list(kwargs.keys())[0]
                raise ValueError(f'Invalid substitution argument "{arg_name}"'
                                 f' provided for endpoint "{endpoint}"')

            return url

    class _Bundles(_SubClient):
        def _prepare_files(self, file_list: [io.BufferedReader]):
            if isinstance(file_list, dict):
                file_list = [file_list]

            files_data = []
            if file_list:
                for idx, file_dict in enumerate(file_list):
                    if "file" in file_dict:
                        print("Actual File")
                        fh = file_dict["file"]
                        if not isinstance(fh, io.BufferedReader):
                            raise ValueError(
                                f"Bad type for file {idx}. Expected an io.BufferedReader"
                                f" (e.g. an open file handle)"
                            )
                        field_name = f"files[{idx}]"
                        files_data.append((field_name, (file_dict.get("filename"),
                                                        fh,
                                                        file_dict.get("content_type"))))
                    elif "file_b64" in file_dict:
                        print("B64 represented File")

                        b64 = file_dict["file_b64"]
                        field_name = f"files[{idx}]"
                        files_data.append((field_name, (file_dict.get("filename"),
                                                        b64,
                                                        file_dict.get("content_type"))))

            return files_data

        def create(self, data: dict,
                   files: List[io.BufferedReader] = []) -> NormalizedResponse:
            """ Post a Bundle to the BlueInk application.

            Args:
                data: raw data for Bundle, expressed as a python dict
                files: list of file-like objects

            Returns:
                NormalizedResponse object
            """
            if not data:
                raise ValueError("data is required")

            url = self.build_url(endpoints.BUNDLES.CREATE)

            if not files:
                response = self._requests.post(url, json=data)
            else:
                files_data = self._prepare_files(files)
                if not files_data:
                    raise ValueError("No valid file data provided")

                bundle_request_data = {"bundle_request": json.dumps(data)}

                response = self._requests.post(url,
                                               data=bundle_request_data,
                                               files=files_data)

            return response

        def create_from_bundle_helper(self,
                                      bdl_helper: BundleHelper) -> NormalizedResponse:
            """ Post a Bundle to the BlueInk application.

            Provided as a convenience to simplify posting of a Bundle. This is the
            recommended way to create a Bundle.

            Args:
                bdl_helper: BundleHelper that has been configured as desired.

            Returns:
                NormalizedResponse object

            """
            data = bdl_helper.as_data()
            files = bdl_helper.files
            return self.create(data=data, files=files)

        def paged_list(self, page: int = 1, per_page: int = 50,
                       related_data: bool = False, **query_params) -> PaginatedIterator:
            """Returns an iterable object such that you may lazily fetch a number of
            Bundles

            Typical Usage:
                for page in client.bundles.paged_list():
                    page.body -> munch of json

            Args:
                page: what page to start iterator at
                per_page: max number of bundles per page
                related_data: toggles whether or not to provide metadata along with
                bundles (events, files, data)

            Returns:
                PaginatedIterator object, compliant with python iterables
            """
            iterator = PaginatedIterator(paged_api_function=self.list,
                                         page=page,
                                         per_page=per_page,
                                         related_data=related_data,
                                         **query_params)
            return iterator

        def list(self, page: int = None, per_page: int = None,
                 related_data: bool = False, **query_params) -> NormalizedResponse:
            """ Returns a list of bundles

            Args:
                page: which page to fetch
                per_page: how many bundles to fetch
                related_data: (default false), returns events, files, data if true
                query_params: Additional query params to be put onto the request

            Returns:
                NormalizedResponse object
            """
            url = self.build_url(endpoints.BUNDLES.LIST)
            response = self._requests.get(url,
                                          params=_build_params(page,
                                                               per_page,
                                                               **query_params))

            if related_data:
                for bundle in response.data:
                    self._attach_additional_data(bundle)

            return response

        def _attach_additional_data(self, bundle):
            if type(bundle) == Munch and bundle.id is not None:
                bundle_id = bundle.id

                events_response = self.list_events(bundle_id)
                if events_response.status == 200:
                    bundle.events = events_response.data

                if bundle.status == BUNDLE_STATUS.COMPLETE:
                    files_response = self.list_files(bundle_id)
                    bundle.files = files_response.data

                    data_response = self.list_data(bundle_id)
                    bundle.data = data_response.data

        def retrieve(self, bundle_id: str,
                     related_data: bool = False) -> NormalizedResponse:
            """Request a single bundle

            Args:
                bundle_id: bundle slug
                related_data: (default false), returns events, files, data if true

            Returns:
                NormalizedResponse object
            """
            url = self.build_url(endpoints.BUNDLES.RETRIEVE, bundle_id=bundle_id)
            response = self._requests.get(url)

            if related_data:
                bundle = response.data
                self._attach_additional_data(bundle)

            return response

        def cancel(self, bundle_id: str) -> NormalizedResponse:
            """Cancel a bundle given bundle slug

            Args:
                bundle_id: denotes which bundle to cancel

            Returns:
                NormalizedResponse object

            """
            url = self.build_url(endpoints.BUNDLES.CANCEL, bundle_id=bundle_id)
            return self._request.put(url)

        def list_events(self, bundle_id: str) -> NormalizedResponse:
            """Return a list of events for the supplied bundle corresponding to the id

            Args:
                bundle_id: which bundle to return events for

            Returns:
                NormalizedResponse object
            """
            url = self.build_url(endpoints.BUNDLES.LIST_EVENTS, bundle_id=bundle_id)
            return self._requests.get(url)

        def list_files(self, bundle_id: str) -> NormalizedResponse:
            """Return a list of files for the supplied bundle corresponding to the id

            Args:
                bundle_id: which bundle to return files for

            Returns:
                NormalizedResponse object
            """
            url = self.build_url(endpoints.BUNDLES.LIST_FILES, bundle_id=bundle_id)
            return self._requests.get(url)

        def list_data(self, bundle_id: str) -> NormalizedResponse:
            """Return a data for the supplied bundle corresponding to the id

            Args:
                bundle_id: which bundle to return data for

            Returns:
                NormalizedResponse object
            """
            url = self.build_url(endpoints.BUNDLES.LIST_DATA, bundle_id=bundle_id)
            return self._requests.get(url)

    class _Persons(_SubClient):
        def create(self, data: dict, **kwargs) -> NormalizedResponse:
            """Create a person (eg. signer) record.

            Args:
                data: A dictionary definition of a person

            Returns:
                NormalizedResponse object
            """
            if "name" not in data or not data["name"]:
                raise ValueError("A name is required to create a Person")

            # Merge the kwargs with the given data
            data = {**data, **kwargs}

            url = self.build_url(endpoints.PERSONS.CREATE)
            return self._requests.post(url, json=data)

        def create_from_person_helper(self, person_helper: PersonHelper,
                                      **kwargs) -> NormalizedResponse:
            """Create a person using PersonHelper convenience object

            Args:
                person_helper: PersonHelper setup of a person

            Return:
                NormalizedResponse object
            """
            return self.create(person_helper.as_dict(**kwargs))

        def paged_list(self, page: int = 1, per_page: int = 50,
                       **query_params) -> PaginatedIterator:
            """Return an iterable object such that you may lazily fetch a number of
            Persons (signers)

            Typical Usage:
                for page in client.persons.paged_list():
                    page.body -> munch of json

            Args:
                page: start page (default 1)
                per_page: max # of results per page (default 50)
                query_params: Additional query params to be put onto the request

            Returns:
                PaginatedIterator object
            """

            iterator = PaginatedIterator(paged_api_function=self.list,
                                         page=page,
                                         per_page=per_page,
                                         **query_params)
            return iterator

        def list(self, page: int = None, per_page: int = None,
                 **query_params) -> NormalizedResponse:
            """Return a list of persons (signers).

            Args:
                page:
                per_page:
                query_params: Additional query params to be put onto the request

            Returns:
                NormalizedResponse object
            """
            url = self.build_url(endpoints.PERSONS.LIST)
            return self._requests.get(url,
                                      params=_build_params(page,
                                                           per_page,
                                                           **query_params))

        def retrieve(self, person_id: str) -> NormalizedResponse:
            """Retrieve details on a singular person

            Args:
                person_id: identifying which signer to retrieve

            Returns:
                NormalizedResponse object
            """
            url = self.build_url(endpoints.PERSONS.RETRIEVE, person_id=person_id)
            return self._requests.get(url)

        def update(self, person_id: str, data: dict,
                   partial: bool = False) -> NormalizedResponse:
            """Update a Person (signer)'s record

            Args:
                person_id:
                data: a dictionary representation of person's data
                partial: Whether to do a partial update

            Returns:
                NormalizedResponse object
            """
            url = self.build_url(endpoints.PERSONS.UPDATE, person_id=person_id)
            if partial:
                response = self._requests.patch(url, json=data)
            else:
                response = self._requests.put(url, json=data)
            return response

        def delete(self, person_id: str) -> NormalizedResponse:
            """Delete a person (signer)

            Args:
                person_id:

            Returns:
                NormalizedResponse object
            """
            url = self.build_url(endpoints.PERSONS.DELETE, person_id=person_id)
            return self._requests.delete(url)

    class _Packets(_SubClient):
        def update(self, packet_id: str, data: dict) -> NormalizedResponse:
            """Update a Packet

            Note: this always performs a partial update (PATCH) because that is
            the only method supported by the Blueink API for this endpoint

            Args:
                packet_id: the ID of the Packet
                data: the updated field values for the Packet

            Returns:
                A NormalizedResponse, with the updated packet as `data`

            Raises:
                 exceptions.RequestException (or a more specific exception class)
                 if an error occured
            """
            url = self.build_url(endpoints.PACKETS.UPDATE, packet_id=packet_id)
            return self._requests.patch(url, json=data)

        def embed_url(self, packet_id: str) -> NormalizedResponse:
            """Create an embedded signing URL

            deliver_via on the Packet must be set to "embed" for this request
            to succeed.

            Args:
                packet_id: the ID of the Packet.

            Returns:
                A NormalizedResponse
            """
            url = self.build_url(endpoints.PACKETS.EMBED_URL, packet_id=packet_id)
            return self._requests.post(url)

        def retrieve_coe(self, packet_id: str) -> NormalizedResponse:
            url = self.build_url(endpoints.PACKETS.RETRIEVE_COE, packet_id=packet_id)
            return self._requests.get(url)

        def remind(self, packet_id: str) -> NormalizedResponse:
            """Send a reminder to this Packet

            Args:
                packet_id: the ID of the Packet

            Returns:
                A NormalizedResponse
            """
            url = self.build_url(endpoints.PACKETS.REMIND, packet_id=packet_id)
            self._requests.put(url)

    class _Templates(_SubClient):
        def __init__(self, base_url, private_api_key):
            super().__init__(base_url, private_api_key)

        def paged_list(self, page: int = 1, per_page: int = 50,
                       **query_params) -> PaginatedIterator:
            """return an iterable object containing a list of templates

            Typical Usage:
                for page in client.templates.paged_list():
                    page.body -> munch of json

            Args:
                page: start page (default 1)
                per_page: max # of results per page (default 50)
                query_params: Additional query params to be put onto the request

            Returns:
                PaginatedIterator object
            """
            iterator = PaginatedIterator(paged_api_function=self.list,
                                         page=page,
                                         per_page=per_page,
                                         **query_params)
            return iterator

        def list(self, page: int = None, per_page: int = None,
                 **query_params) -> NormalizedResponse:
            """Return a list of Templates.

            Args:
                page:
                per_page:
                query_params: Additional query params to be put onto the request

            Returns:
                NormalizedResponse object
            """
            url = self.build_url(endpoints.TEMPLATES.LIST)
            return self._requests.get(url, params=_build_params(page,
                                                                per_page,
                                                                **query_params))

        def retrieve(self, template_id: str) -> NormalizedResponse:
            """Return a singular Template by id.

            Args:
                template_id:

            Returns:
                NormalizedResponse object
            """
            url = self.build_url(endpoints.TEMPLATES.RETRIEVE, template_id=template_id)
            return self._requests.get(url)
