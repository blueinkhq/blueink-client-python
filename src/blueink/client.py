import io
import json
from os import environ

from munch import Munch
from .bundle_helper import BundleHelper
from . import endpoints
from .constants import BUNDLE_STATUS, DEFAULT_BASE_URL, ENV_BLUEINK_API_URL, ENV_BLUEINK_PRIVATE_API_KEY
from .person_helper import PersonHelper
from .paginator import PaginatedIterator
from .request_helper import NormalizedResponse, RequestHelper


def _build_params(page=None, per_page=None, **query_params):
    params = dict(**query_params)
    if page is not None:  # page could be zero, although Blueink pagination is 1-indexed
        params["page"] = page

    if per_page:
        params["per_page"] = per_page

    return params


class Client:
    def __init__(self, override_base_url=None, override_private_api_key=None):
        """

        :param override_base_url: Provide or override value provided by environmental variable. If none supplied, will
        use default "https://api.blueink.com/api/v2" if no env var BLUEINK_API_URL found.
        :param override_private_api_key: Provide or override value provided by environmental variable. If none supplied,
        will use env var BLUEINK_PRIVATE_API_KEY
        """
        if override_private_api_key:
            private_api_key = override_private_api_key
        else:
            private_api_key = environ.get(ENV_BLUEINK_PRIVATE_API_KEY)

        if not private_api_key:
            raise ValueError(
                "A Blueink Private API Key must be provided on Client initialization or "
                + f"specified via the environment variable {ENV_BLUEINK_PRIVATE_API_KEY}"
            )

        try:
            base_url = override_base_url if override_base_url else environ[ENV_BLUEINK_API_URL]
        except KeyError:
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

            url = endpoints.URLBuilder(self._base_url, endpoints.bundles.create).build()

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
            url = endpoints.URLBuilder(self._base_url, endpoints.bundles.list).build()
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
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.bundles.retrieve)
                    .interpolate(endpoints.interpolations.bundle_id, bundle_id)
                    .build()
            )

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
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.bundles.cancel)
                    .interpolate(endpoints.interpolations.bundle_id, bundle_id)
                    .build()
            )

            return self._request.put(url)

        def list_events(self, bundle_id) -> NormalizedResponse:
            """
            Returns a list of events for the supplied bundle corresponding to the id
            :param bundle_id:
            :return:
            """
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.bundles.list_events)
                    .interpolate(endpoints.interpolations.bundle_id, bundle_id)
                    .build()
            )

            return self._requests.get(url)

        def list_files(self, bundle_id) -> NormalizedResponse:
            """
            Returns a list of files for the supplied bundle corresponding to the id
            :param bundle_id:
            :return:
            """
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.bundles.list_files)
                    .interpolate(endpoints.interpolations.bundle_id, bundle_id)
                    .build()
            )

            return self._requests.get(url)

        def list_data(self, bundle_id) -> NormalizedResponse:
            """
            Returns a list of data fields for the supplied bundle corresponding to the id
            :param bundle_id:
            :return:
            """
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.bundles.list_data)
                    .interpolate(endpoints.interpolations.bundle_id, bundle_id)
                    .build()
            )

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

            url = endpoints.URLBuilder(self._base_url, endpoints.persons.create).build()
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
            url = endpoints.URLBuilder(self._base_url, endpoints.persons.list).build()
            response = self._requests.get(url, params=_build_params(page, per_page, **query_params))

            return response

        def retrieve(self, person_id: str) -> NormalizedResponse:
            """
            Retrieves details on a singular person
            :param person_id:
            :return:
            """
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.persons.retrieve)
                    .interpolate(endpoints.interpolations.person_id, person_id)
                    .build()
            )
            return self._requests.get(url)

        def update(self, person_id: str, data: dict) -> NormalizedResponse:
            """
            :param person_id:
            :param data: a full dictionary representation of person
            :return:
            """
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.persons.full_update)
                    .interpolate(endpoints.interpolations.person_id, person_id)
                    .build()
            )

            return self._requests.put(url, json=data)

        def partial_update(self, person_id: str, data: dict) -> NormalizedResponse:
            """

            :param person_id:
            :param data: a partial dictionary representation of person
            :return:
            """
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.persons.partial_update)
                    .interpolate(endpoints.interpolations.person_id, person_id)
                    .build()
            )
            return self._requests.patch(url, json=data)

        def delete(self, person_id: str) -> NormalizedResponse:
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.persons.delete)
                    .interpolate(endpoints.interpolations.person_id, person_id)
                    .build()
            )
            return self._requests.delete(url)

    class _Packets(_SubClient):
        def update(self, packet_id: str, data: dict) -> NormalizedResponse:
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.packets.full_update)
                    .interpolate(endpoints.interpolations.person_id, packet_id)
                    .build()
            )
            return self._requests.patch(url, json=data)

        def delete(self, person_id: str) -> NormalizedResponse:
            """
            Deletes a person
            :param person_id:
            :return:
            """
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.packets.delete)
                    .interpolate(endpoints.interpolations.person_id, person_id)
                    .build()
            )
            return self._requests.delete(url)

        def remind(self, packet_id: str) -> NormalizedResponse:
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.packets.remind)
                    .interpolate(endpoints.interpolations.packet_id, packet_id)
                    .build()
            )
            return self._requests.put(url)

        def retrieve_coe(self, packet_id: str) -> NormalizedResponse:
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.packets.retrieve_coe)
                    .interpolate(endpoints.interpolations.packet_id, packet_id)
                    .build()
            )
            return self._requests.get(url)

        def remind(self, packet_id: str) -> NormalizedResponse:
            """
            Sends a reminder to the contact channel on this packet
            :param packet_id:
            :return:
            """
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.packets.remind)
                    .interpolate(endpoints.interpolations.packet_id, packet_id)
                    .build()
            )
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
            url = endpoints.URLBuilder(self._base_url, endpoints.templates.list).build()
            return self._requests.get(url, params=_build_params(page, per_page, **query_params))

        def retrieve(self, template_id: str) -> NormalizedResponse:
            """
            Retrieves a singular template with this id
            :param template_id:
            :return:
            """
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.templates.retrieve)
                    .interpolate(endpoints.interpolations.template_id, template_id)
                    .build()
            )
            return self._requests.get(url)
