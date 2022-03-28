import sys
from . import endpoints
from os import environ
from munch import Munch
from .tokenizedrequests import (tget, tpost, tpost_formdata, tput, tpatch, tdelete, MunchedResponse, build_pagination_params)
from .model.bundles import BundleBuilder
from .paginator import PaginatedIterator


class Client:
    def __init__(self, override_base_url=None, override_private_api_key=None):
        """

        :param override_base_url: Provide or override value provided by environmental variable. If none supplied, will
        use default "https://api.blueink.com/api/v2" if no env var BLUEINK_API_URL found.
        :param override_private_api_key: Provide or override value provided by environmental variable. If none supplied,
        will use env var BLUEINK_PRIVATE_API_KEY
        """
        private_api_key = override_private_api_key if override_private_api_key is not None else environ['BLUEINK_PRIVATE_API_KEY']
        base_url = None
        try:
            base_url = override_base_url if override_base_url is not None else environ['BLUEINK_API_URL']
        except KeyError:
            base_url = "https://api.blueink.com/api/v2"
            print(f"Environment variable 'BLUEINK_API_URL' not supplied -- defaulting to {base_url}", file=sys.stderr)

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

        def create(self, bundle_builder:BundleBuilder) -> MunchedResponse:
            """
            Post a Bundle to the BlueInk application.
            :param bundle_builder: 
            :return:
            """
            url = endpoints.URLBuilder(self._base_url, endpoints.bundles.create) \
                .build()

            response = None
            json = bundle_builder.build_json()
            if len(bundle_builder.files) == 0:
                response = tpost(url, self._private_api_key, json)
            else:
                response = tpost_formdata(url, self._private_api_key, json, bundle_builder.files, bundle_builder.file_names, bundle_builder.file_types)
            return response

        def pagedlist(self, start_page=0, per_page=50, getAdditionalData=False) -> PaginatedIterator:
            '''
            returns an iterable object such that you can do

            for page in client.bundles.list_iter():
                page.body -> munch of json

            :param getAdditionalData:
            :param start_page:
            :param per_page:
            :return:
            '''
            params = [start_page, per_page, getAdditionalData]
            paged_call = PaginatedIterator(self.list, params, 0)
            return paged_call

        def list(self, page=None, per_page=None, getAdditionalData=False) -> MunchedResponse:
            """
            Returns a list of bundles
            :param page: (optional)
            :param per_page: (optional)
            :param getAdditionalData: (default false), returns events, files, data if true
            :return:
            """
            response = None
            if page is None and per_page is None:
                url = endpoints.URLBuilder(self._base_url, endpoints.bundles.list) \
                    .build()
                response = tget(url, self._private_api_key)
            else:
                url = endpoints.URLBuilder(self._base_url, endpoints.bundles.list) \
                    .build()
                url_params = build_pagination_params(page, per_page)

                response = tget(url, self._private_api_key, url_params)

            if getAdditionalData:
                for bundle in response.data:
                    self._attach_additional_data(bundle)

            return response

        def _attach_additional_data(self, bundle):
            if type(bundle) == Munch and bundle.id is not None:
                bundle_id = bundle.id

                events_response = self.list_events(bundle_id)
                if events_response.status == 200:
                    bundle.events = events_response.data

                if bundle.status == "co":
                    files_response = self.list_files(bundle_id)
                    bundle.files = files_response.data

                    data_response = self.list_data(bundle_id)
                    bundle.data = data_response.data

        def retrieve(self, bundle_id, getAdditionalData=False) -> MunchedResponse:
            """
            Requests a single bundle
            :param bundle_id: bundle slug
            :param getAdditionalData: (default false), returns events, files, data if true
            :return:
            """
            url = endpoints.URLBuilder(self._base_url, endpoints.bundles.retrieve)\
                .interpolate(endpoints.interpolations.bundle_id, bundle_id)\
                .build()

            response = tget(url, self._private_api_key)

            if getAdditionalData:
                bundle = response.data
                self._attach_additional_data(bundle)

            return response

        def cancel(self, bundle_id) -> MunchedResponse:
            """
            Cancels a bundle given bundle slug
            :param bundle_id:
            :return:
            """
            url = endpoints.URLBuilder(self._base_url, endpoints.bundles.cancel) \
                .interpolate(endpoints.interpolations.bundle_id, bundle_id)\
                .build()

            return tput(url, self._private_api_key)

        def list_events(self, bundle_id) -> MunchedResponse:
            url = endpoints.URLBuilder(self._base_url, endpoints.bundles.list_events) \
                .interpolate(endpoints.interpolations.bundle_id, bundle_id)\
                .build()

            return tget(url, self._private_api_key)

        def list_files(self, bundle_id) -> MunchedResponse:
            url = endpoints.URLBuilder(self._base_url, endpoints.bundles.list_files) \
                .interpolate(endpoints.interpolations.bundle_id, bundle_id)\
                .build()

            return tget(url, self._private_api_key)

        def list_data(self, bundle_id) -> MunchedResponse:
            url = endpoints.URLBuilder(self._base_url, endpoints.bundles.list_data) \
                .interpolate(endpoints.interpolations.bundle_id, bundle_id)\
                .build()

            return tget(url, self._private_api_key)

    class _Persons(_SubClient):
        def __init__(self, base_url, api_key):
            super().__init__(base_url, api_key)

        def create(self, data) -> MunchedResponse:
            """
            Creates a person.
            :param data: JSON string for a person
            :return:
            """
            url = endpoints.URLBuilder(self._base_url, endpoints.persons.create)\
                .build()
            return tpost(url, self._private_api_key, data)

        def pagedlist(self, start_page=0, per_page=50) -> PaginatedIterator:
            '''
            returns an iterable object such that you can do

            for page in client.persons.list_iter():
                page.body -> munch of json

            :param start_page:
            :param per_page:
            :return:
            '''
            params = [start_page, per_page]
            paged_call = PaginatedIterator(self.list, params, 0)
            return paged_call

        def list(self, page=None, per_page=None) -> MunchedResponse:
            response = None
            if page is None and per_page is None:
                url = endpoints.URLBuilder(self._base_url, endpoints.persons.list) \
                    .build()
                response = tget(url, self._private_api_key)

            else:
                url = endpoints.URLBuilder(self._base_url, endpoints.persons.list) \
                    .build()
                url_params = build_pagination_params(page, per_page)

                response = tget(url, self._private_api_key, url_params)

            return response

        def retrieve(self, person_id:str) -> MunchedResponse:
            url = endpoints.URLBuilder(self._base_url, endpoints.persons.retrieve) \
                .interpolate(endpoints.interpolations.person_id, person_id) \
                .build()
            return tget(url, self._private_api_key)

        def update(self, person_id:str, data:str) -> MunchedResponse:
            """

            :param person_id:
            :param data: JSON string of person
            :return:
            """
            url = endpoints.URLBuilder(self._base_url, endpoints.persons.update) \
                .interpolate(endpoints.interpolations.person_id, person_id) \
                .build()
            return tput(url, self._private_api_key, data)

        def partial_update(self, person_id:str, data:str) -> MunchedResponse:
            """

            :param person_id:
            :param data: JSON string of person
            :return:
            """
            url = endpoints.URLBuilder(self._base_url, endpoints.persons.partial_update) \
                .interpolate(endpoints.interpolations.person_id, person_id) \
                .build()
            return tpatch(url, self._private_api_key, data)

        def delete(self, person_id:str) -> MunchedResponse:
            url = endpoints.URLBuilder(self._base_url, endpoints.persons.delete) \
                .interpolate(endpoints.interpolations.person_id, person_id) \
                .build()
            return tdelete(url, self._private_api_key)

    class _Packets(_SubClient):
        def __init__(self, base_url, private_api_key):
            super().__init__(base_url, private_api_key)

        def update(self, packet_id:str, data:str) -> MunchedResponse:
            """

            :param packet_id:
            :param data: JSON of packet
            :return:
            """
            url = endpoints.URLBuilder(self._base_url, endpoints.packets.update) \
                .interpolate(endpoints.interpolations.packet_id, packet_id) \
                .build()
            return tpatch(url, self._private_api_key, data)

        def remind(self, packet_id:str) -> MunchedResponse:
            url = endpoints.URLBuilder(self._base_url, endpoints.packets.remind) \
                .interpolate(endpoints.interpolations.packet_id, packet_id) \
                .build()
            return tput(url, self._private_api_key)

        def retrieve_coe(self, packet_id:str) -> MunchedResponse:
            url = endpoints.URLBuilder(self._base_url, endpoints.packets.retrieve_coe) \
                .interpolate(endpoints.interpolations.packet_id, packet_id) \
                .build()
            return tget(url, self._private_api_key)

    class _Templates(_SubClient):
        def __init__(self, base_url, private_api_key):
            super().__init__(base_url, private_api_key)

        def pagedlist(self, start_page=0, per_page=50) -> PaginatedIterator:
            '''
            returns an iterable object such that you can do

            for page in client.bundles.list_iter():
                page.body -> munch of json

            :param start_page:
            :param per_page:
            :return:
            '''
            params = [start_page, per_page]
            paged_call = PaginatedIterator(self.list, params, 0)
            return paged_call

        def list(self, page=None, per_page=None) -> MunchedResponse:
            response = None
            if page is None and per_page is None:
                url = endpoints.URLBuilder(self._base_url, endpoints.templates.list) \
                    .build()
                response = tget(url, self._private_api_key)

            else:
                url = endpoints.URLBuilder(self._base_url, endpoints.templates.list) \
                    .build()
                url_params = build_pagination_params(page, per_page)

                response = tget(url, self._private_api_key, url_params)

            return response

        def retrieve(self, template_id:str) -> MunchedResponse:
            url = endpoints.URLBuilder(self._base_url, endpoints.templates.retrieve) \
                .interpolate(endpoints.interpolations.template_id, template_id) \
                .build()
            return tget(url, self._private_api_key)
