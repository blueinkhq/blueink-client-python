import io
import json
from os import environ

from munch import Munch

from . import endpoints
from .bundle_helper import BundleHelper
from .constants import BUNDLE_STATUS, DEFAULT_BASE_URL, ENV_BLUEINK_API_URL, ENV_BLUEINK_PRIVATE_API_KEY
from .paginator import PaginatedIterator
from .person_helper import PersonHelper
from .request_helper import NormalizedResponse, RequestHelper


def _build_params(page=None, per_page=None, **query_params):
    params = dict(**query_params)
    if page is not None:  # page could be zero, although Blueink pagination is 1-indexed
        params["page"] = page

    if per_page:
        params["per_page"] = per_page

    return params


class Client:
    def __init__(self, private_api_key=None, base_url=None):
        """Initialize a Client instance to access the Blueink eSignature API

        Args:
            private_api_key: the private API key used to access the Blueink API.
                If no value is provided, then the environment is checked for a variable named
                "BLUEINK_PRIVATE_API_KEY".
            base_url: override the API base URL. If not supplied, we check the environment variable
                BLUEINK_API_URL. If that is empty, the default value of "https://api.blueink.com/api/v2"
                is used.

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
                "A Blueink Private API Key must be provided on Client initialization or "
                f"specified via the environment variable {ENV_BLUEINK_PRIVATE_API_KEY}"
            )

        if not base_url:
            base_url = environ.get(ENV_BLUEINK_API_URL)

        if not base_url:
            base_url = DEFAULT_BASE_URL

        self._request_helper = RequestHelper(private_api_key)

        self.bundles = self._Bundles(base_url, self._request_helper)
        self.persons = self._Persons(base_url, self._request_helper)
        self.packets = self._Packets(base_url, self._request_helper)
        self.templates = self._Templates(base_url, self._request_helper)

    class _SubClient:
        def __init__(self, base_url, requests_helper):
            self._base_url = base_url
            self._requests = requests_helper

        def build_url(self, endpoint: str, **kwargs):
            """Shortcut to build a URL using endpoints.URLBuilder

            Args:
                endpoint: one of the API endpoints, e.g. endpoints.BUNDLES.create
                **kwargs: the arg name should be one of the keys in endpoints.interpolations, and the arg
                    value will be substituted for the named placeholder in the endpoint str

            Returns:
                The URL as a str

            Raises:
                ValueError if one of the kwargs is not a valid endpoint interpolation key
            """
            # All of our current endpoints take 1 parameter, max
            if len(kwargs) > 1:
                raise ValueError('Only one interpolation parameter is allowed')

            try:
                url = endpoints.URLBuilder(self._base_url, endpoint).build(**kwargs)
            except KeyError:
                arg_name = list(kwargs.keys())[0]
                raise ValueError(f'Invalid substitution argument "{arg_name}" provided for endpoint "{endpoint}"')

            return url

    class _Bundles(_SubClient):
        def _prepare_files(self, file_list):
            if isinstance(file_list, dict):
                file_list = [file_list]

            files_data = []
            if file_list:
                for idx, file_dict in enumerate(file_list):
                    try:
                        fh = file_dict["file"]
                    except KeyError:
                        raise ValueError("Each file dict must have a 'file' key that is a file-like object")

                    if not isinstance(fh, io.BufferedReader):
                        raise ValueError(
                            f"Bad type for file {idx}. Expected an io.BufferedReader (e.g. an open file handle)"
                        )

                    field_name = f"files[{idx}]"
                    files_data.append((field_name, (file_dict.get("filename"), fh, file_dict.get("content_type"))))

            return files_data

        def create(self, data: dict, files=[]) -> NormalizedResponse:
            """
            Post a Bundle to the BlueInk application.
            :param data: python dict, typically from BundleHelper.as_data()
            :param files: list of file-like streams (optional)
            :return:
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

                response = self._requests.post(url, data=bundle_request_data, files=files_data)

            return response

        def create_from_bundle_helper(self, bundle_helper: BundleHelper) -> NormalizedResponse:
            """
            Post a Bundle to the BlueInk application. Convenience method as bundle_helper has files/filenames if
            creating a Bundle that way
            :param bundle_helper:
            :return:
            """
            data = bundle_helper.as_data()
            files = bundle_helper.files
            return self.create(data=data, files=files)

        def paged_list(self, page=1, per_page=50, related_data=False, **query_params) -> PaginatedIterator:
            """
            returns an iterable object such that you can do

            for page in client.bundles.paged_list():
                page.body -> munch of json

            :param page: start page (default 1)
            :param per_page: max # of results per page (default 50)
            :param related_data: (default false), returns events, files, data if true
            :param query_params: Additional query params to be put onto the request
            :return:
            """
            iterator = PaginatedIterator(paged_api_function=self.list,
                                         page=page,
                                         per_page=per_page,
                                         related_data=related_data,
                                         **query_params)
            return iterator

        def list(self, page=None, per_page=None, related_data=False, **query_params) -> NormalizedResponse:
            """
            Returns a list of bundles
            :param page: (optional)
            :param per_page: (optional)
            :param related_data: (default false), returns events, files, data if true
            :param query_params: Additional query params to be put onto the request
            :return:
            """
            url = self.build_url(endpoints.BUNDLES.LIST)
            response = self._requests.get(url, params=_build_params(page, per_page, **query_params))

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

        def retrieve(self, bundle_id, related_data=False) -> NormalizedResponse:
            """
            Requests a single bundle
            :param bundle_id: bundle slug
            :param related_data: (default false), returns events, files, data if true
            :return:
            """
            url = self.build_url(endpoints.BUNDLES.RETRIEVE, bundle_id=bundle_id)
            response = self._requests.get(url)

            if related_data:
                bundle = response.data
                self._attach_additional_data(bundle)

            return response

        def cancel(self, bundle_id) -> NormalizedResponse:
            """
            Cancels a bundle given bundle slug
            :param bundle_id:
            :return:
            """
            url = self.build_url(endpoints.BUNDLES.CANCEL, bundle_id=bundle_id)
            return self._request.put(url)

        def list_events(self, bundle_id) -> NormalizedResponse:
            """
            Returns a list of events for the supplied bundle corresponding to the id
            :param bundle_id:
            :return:
            """
            url = self.build_url(endpoints.BUNDLES.LIST_EVENTS, bundle_id=bundle_id)
            return self._requests.get(url)

        def list_files(self, bundle_id) -> NormalizedResponse:
            """
            Returns a list of files for the supplied bundle corresponding to the id
            :param bundle_id:
            :return:
            """
            url = self.build_url(endpoints.BUNDLES.LIST_FILES, bundle_id=bundle_id)
            return self._requests.get(url)

        def list_data(self, bundle_id) -> NormalizedResponse:
            """
            Returns a list of data fields for the supplied bundle corresponding to the id
            :param bundle_id:
            :return:
            """
            url = self.build_url(endpoints.BUNDLES.LIST_DATA, bundle_id=bundle_id)
            return self._requests.get(url)

    class _Persons(_SubClient):
        def create(self, data: dict, **kwargs) -> NormalizedResponse:
            """
            Creates a person.
            :param data: A dictionary definition of a person
            :return:
            """
            if "name" not in data or not data["name"]:
                raise ValueError("A name is required to create a Person")

            # Merge the kwargs with the given data
            data = {**data, **kwargs}

            url = self.build_url(endpoints.PERSONS.CREATE)
            return self._requests.post(url, json=data)

        def create_from_person_helper(self, person_helper: PersonHelper, **kwargs) -> NormalizedResponse:
            """
            Creates a person.
            :param person_helper: PersonHelper setup of a person
            :return:
            """
            return self.create(person_helper.as_dict(**kwargs))

        def paged_list(self, page=1, per_page=50, **query_params) -> PaginatedIterator:
            """
            returns an iterable object such that you can do

            for page in client.persons.paged_list():
                page.body -> munch of json

            :param page: start page (default 1)
            :param per_page: max # of results per page (default 50)
            :param query_params: Additional query params to be put onto the request
            :return:
            """

            iterator = PaginatedIterator(paged_api_function=self.list,
                                         page=page,
                                         per_page=per_page,
                                         **query_params)
            return iterator

        def list(self, page=None, per_page=None, **query_params) -> NormalizedResponse:
            """
            Returns a list of persons. Optionally supply the page number and results per page.
            :param page:
            :param per_page:
            :param query_params: Additional query params to be put onto the request
            :return:
            """
            url = self.build_url(endpoints.PERSONS.LIST)
            return self._requests.get(url, params=_build_params(page, per_page, **query_params))

        def retrieve(self, person_id: str) -> NormalizedResponse:
            """
            Retrieves details on a singular person
            :param person_id:
            :return:
            """
            url = self.build_url(endpoints.PERSONS.RETRIEVE, person_id=person_id)
            return self._requests.get(url)

        def update(self, person_id: str, data: dict, partial=False) -> NormalizedResponse:
            """
            :param person_id:
            :param data: a full dictionary representation of person
            :return:
            """
            url = self.build_url(endpoints.PERSONS.UPDATE, person_id=person_id)
            if partial:
                response = self._requests.patch(url, json=data)
            else:
                response = self._requests.put(url, json=data)
            return response

        def delete(self, person_id: str) -> NormalizedResponse:
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
                 exceptions.RequestException (or a more specific exception class) if an error occured
            """
            url = self.build_url(endpoints.PACKETS.UPDATE, packet_id=packet_id)
            return self._requests.patch(url, json=data)

        def embed_url(self, packet_id: str) -> NormalizedResponse:
            """Create an embedded signing URL

            deliver_via on the Packet must be set to "embed" for this request to succeed.

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

        def paged_list(self, page=1, per_page=50, **query_params) -> PaginatedIterator:
            """
            returns an iterable object such that you can do

            for page in client.templates.paged_list():
                page.body -> munch of json

            :param page: start page (default 1)
            :param per_page: max # of results per page (default 50)
            :param query_params: Additional query params to be put onto the request
            :return:
            """
            iterator = PaginatedIterator(paged_api_function=self.list,
                                         page=page,
                                         per_page=per_page,
                                         **query_params)
            return iterator

        def list(self, page=None, per_page=None, **query_params) -> NormalizedResponse:
            """
            Retrieves a list of templates, optionally for a page and # of results per page
            :param page:
            :param per_page:
            :param query_params: Additional query params to be put onto the request
            :return:
            """
            url = self.build_url(endpoints.TEMPLATES.LIST)
            return self._requests.get(url, params=_build_params(page, per_page, **query_params))

        def retrieve(self, template_id: str) -> NormalizedResponse:
            """
            Retrieves a singular template with this id
            :param template_id:
            :return:
            """
            url = self.build_url(endpoints.TEMPLATES.RETRIEVE, template_id=template_id)
            return self._requests.get(url)
