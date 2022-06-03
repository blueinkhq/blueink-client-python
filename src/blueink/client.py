import json
from os import environ
from munch import Munch
from . import endpoints
from .constants import BUNDLE_STATUS, DEFAULT_BASE_URL, ENV_BLUEINK_API_URL, ENV_BLUEINK_PRIVATE_API_KEY
from .model.bundles import BundleHelper
from .model.persons import PersonHelper
from .paginator import PaginatedIterator
from .tokenizedrequests import (
    tget,
    tpost,
    tpost_formdata,
    tput,
    tpatch,
    tdelete,
    MunchedResponse,
    build_pagination_params,
)


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

        self.bundles = self._Bundles(base_url, private_api_key)
        self.persons = self._Persons(base_url, private_api_key)
        self.packets = self._Packets(base_url, private_api_key)
        self.templates = self._Templates(base_url, private_api_key)

    class _SubClient:
        def __init__(self, base_url, private_api_key):
            self._base_url = base_url
            self._private_api_key = private_api_key

    class _Bundles(_SubClient):
        def __init__(self, base_url, private_api_key):
            super().__init__(base_url, private_api_key)

        def create(self, data: dict, files=[], file_names=[], file_types=[]) -> MunchedResponse:
            """
            Post a Bundle to the BlueInk application.
            :param data: python dict, typically from BundleHelper.as_data()
            :param files: list of file-like streams (optional)
            :param file_names: - list of file names, ordered same as files (optional)
            :param file_types: - list of file types, ordered same as files (optional)
            :return:
            """
            url = endpoints.URLBuilder(self._base_url, endpoints.bundles.create).build()

            json_data = json.dumps(data)

            if len(files) == 0:
                response = tpost(url, self._private_api_key, json_data)
            else:
                response = tpost_formdata(url, self._private_api_key, json_data, files, file_names, file_types)

            return response

        def create_from_bundle_helper(self, bundle_helper: BundleHelper) -> MunchedResponse:
            """
            Post a Bundle to the BlueInk application. Convenience method as bundle_helper has files/filenames if
            creating a Bundle that way
            :param bundle_helper:
            :return:
            """
            data = bundle_helper.as_data()
            files = bundle_helper.files
            file_names = bundle_helper.file_names
            file_types = bundle_helper.file_types

            return self.create(data=data, files=files, file_names=file_names, file_types=file_types)

        def paged_list(self, start_page=0, per_page=50, related_data=False) -> PaginatedIterator:
            """
            returns an iterable object such that you can do

            for page in client.bundles.paged_list():
                page.body -> munch of json

            :param related_data:
            :param start_page:
            :param per_page:
            :return:
            """
            params = [start_page, per_page, related_data]
            paged_call = PaginatedIterator(self.list, params, 0)
            return paged_call

        def list(self, page=None, per_page=None, related_data=False) -> MunchedResponse:
            """
            Returns a list of bundles
            :param page: (optional)
            :param per_page: (optional)
            :param related_data: (default false), returns events, files, data if true
            :return:
            """
            response = None
            if page is None and per_page is None:
                url = endpoints.URLBuilder(self._base_url, endpoints.bundles.list).build()
                response = tget(url, self._private_api_key)
            else:
                url = endpoints.URLBuilder(self._base_url, endpoints.bundles.list).build()
                url_params = build_pagination_params(page, per_page)

                response = tget(url, self._private_api_key, url_params)

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

        def retrieve(self, bundle_id, related_data=False) -> MunchedResponse:
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

            response = tget(url, self._private_api_key)

            if related_data:
                bundle = response.data
                self._attach_additional_data(bundle)

            return response

        def cancel(self, bundle_id) -> MunchedResponse:
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

            return tput(url, self._private_api_key)

        def list_events(self, bundle_id) -> MunchedResponse:
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.bundles.list_events)
                .interpolate(endpoints.interpolations.bundle_id, bundle_id)
                .build()
            )

            return tget(url, self._private_api_key)

        def list_files(self, bundle_id) -> MunchedResponse:
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.bundles.list_files)
                .interpolate(endpoints.interpolations.bundle_id, bundle_id)
                .build()
            )

            return tget(url, self._private_api_key)

        def list_data(self, bundle_id) -> MunchedResponse:
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.bundles.list_data)
                .interpolate(endpoints.interpolations.bundle_id, bundle_id)
                .build()
            )

            return tget(url, self._private_api_key)

    class _Persons(_SubClient):
        def __init__(self, base_url, api_key):
            super().__init__(base_url, api_key)

        def create(self, data: dict) -> MunchedResponse:
            """
            Creates a person.
            :param data: A dictionary definition of a person
            :return:
            """
            data_json = json.dumps(data)
            url = endpoints.URLBuilder(self._base_url, endpoints.persons.create).build()
            return tpost(url, self._private_api_key, data_json)

        def create_from_person_helper(self, person_helper: PersonHelper) -> MunchedResponse:
            """
            Creates a person.
            :param person_helper: PersonHelper setup of a person
            :return:
            """
            return self.create(person_helper.as_dict())

        def paged_list(self, start_page=0, per_page=50) -> PaginatedIterator:
            """
            returns an iterable object such that you can do

            for page in client.persons.paged_list():
                page.body -> munch of json

            :param start_page:
            :param per_page:
            :return:
            """
            params = [start_page, per_page]
            paged_call = PaginatedIterator(self.list, params, 0)
            return paged_call

        def list(self, page=None, per_page=None) -> MunchedResponse:
            response = None
            if page is None and per_page is None:
                url = endpoints.URLBuilder(self._base_url, endpoints.persons.list).build()
                response = tget(url, self._private_api_key)

            else:
                url = endpoints.URLBuilder(self._base_url, endpoints.persons.list).build()
                url_params = build_pagination_params(page, per_page)

                response = tget(url, self._private_api_key, url_params)

            return response

        def retrieve(self, person_id: str) -> MunchedResponse:
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.persons.retrieve)
                .interpolate(endpoints.interpolations.person_id, person_id)
                .build()
            )
            return tget(url, self._private_api_key)

        def update(self, person_id: str, data: dict) -> MunchedResponse:
            """

            :param person_id:
            :param data: dictionary representation of person
            :return:
            """
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.persons.full_update)
                .interpolate(endpoints.interpolations.person_id, person_id)
                .build()
            )
            return tput(url, self._private_api_key, json.dumps(data))

        def partial_update(self, person_id: str, data: dict) -> MunchedResponse:
            """

            :param person_id:
            :param data: JSON string of person
            :return:
            """
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.persons.partial_update)
                .interpolate(endpoints.interpolations.person_id, person_id)
                .build()
            )
            return tpatch(url, self._private_api_key, json.dumps(data))

        def delete(self, person_id: str) -> MunchedResponse:
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.persons.delete)
                .interpolate(endpoints.interpolations.person_id, person_id)
                .build()
            )
            return tdelete(url, self._private_api_key)

    class _Packets(_SubClient):
        def __init__(self, base_url, private_api_key):
            super().__init__(base_url, private_api_key)

        def update(self, packet_id: str, data: str) -> MunchedResponse:
            """

            :param packet_id:
            :param data: JSON of packet
            :return:
            """
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.packets.update)
                .interpolate(endpoints.interpolations.packet_id, packet_id)
                .build()
            )
            return tpatch(url, self._private_api_key, data)

        def remind(self, packet_id: str) -> MunchedResponse:
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.packets.remind)
                .interpolate(endpoints.interpolations.packet_id, packet_id)
                .build()
            )
            return tput(url, self._private_api_key)

        def retrieve_coe(self, packet_id: str) -> MunchedResponse:
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.packets.retrieve_coe)
                .interpolate(endpoints.interpolations.packet_id, packet_id)
                .build()
            )
            return tget(url, self._private_api_key)

    class _Templates(_SubClient):
        def __init__(self, base_url, private_api_key):
            super().__init__(base_url, private_api_key)

        def paged_list(self, start_page=0, per_page=50) -> PaginatedIterator:
            """
            returns an iterable object such that you can do

            for page in client.bundles.paged_list():
                page.body -> munch of json

            :param start_page:
            :param per_page:
            :return:
            """
            params = [start_page, per_page]
            paged_call = PaginatedIterator(self.list, params, 0)
            return paged_call

        def list(self, page=None, per_page=None) -> MunchedResponse:
            response = None
            if page is None and per_page is None:
                url = endpoints.URLBuilder(self._base_url, endpoints.templates.list).build()
                response = tget(url, self._private_api_key)

            else:
                url = endpoints.URLBuilder(self._base_url, endpoints.templates.list).build()
                url_params = build_pagination_params(page, per_page)

                response = tget(url, self._private_api_key, url_params)

            return response

        def retrieve(self, template_id: str) -> MunchedResponse:
            url = (
                endpoints.URLBuilder(self._base_url, endpoints.templates.retrieve)
                .interpolate(endpoints.interpolations.template_id, template_id)
                .build()
            )
            return tget(url, self._private_api_key)
