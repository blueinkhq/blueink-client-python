from requests import Response
from os import environ
from TokenizedRequests import (tget, tpost, tput, tpatch, tdelete)
import Endpoints


class Client:
    def __init__(self, override_base_url=None, override_api_key=None):
        base_url = override_base_url if override_base_url is not None else environ['BLUEINK_API_URI']
        api_key = override_api_key if override_api_key is not None else environ['BLUEINK_API_KEY']

        self.bundles = self._Bundles(base_url, api_key)
        self.persons = self._Persons(base_url, api_key)
        self.packets = self._Packets(base_url, api_key)
        self.templates = self._Templates(base_url, api_key)

    class _SubClient:
        def __init__(self, base_url, api_key):
            self._base_url = base_url
            self._api_key = api_key

    class _Bundles(_SubClient):
        def __init__(self, base_url, api_key):
            super().__init__(base_url, api_key)

        def create(self, data) -> Response:
            url = Endpoints.URLBuilder(self._base_url, Endpoints.bundles.create) \
                .build()

            return tpost(url, self._api_key, data, "application/json")

        def list(self) -> Response:
            url = Endpoints.URLBuilder(self._base_url, Endpoints.bundles.list)\
                .build()

            return tget(url, self._api_key)

        def retrieve(self, bundle_id) -> Response:
            url = Endpoints.URLBuilder(self._base_url, Endpoints.bundles.retrieve)\
                .interpolate(Endpoints.interpolations.bundle_id, bundle_id)\
                .build()

            return tget(url, self._api_key)

        def cancel(self, bundle_id) -> Response:
            url = Endpoints.URLBuilder(self._base_url, Endpoints.bundles.cancel) \
                .interpolate(Endpoints.interpolations.bundle_id, bundle_id)\
                .build()

            return tput(url, self._api_key)

        def list_events(self, bundle_id) -> Response:
            url = Endpoints.URLBuilder(self._base_url, Endpoints.bundles.list_events) \
                .interpolate(Endpoints.interpolations.bundle_id, bundle_id)\
                .build()

            return tget(url, self._api_key)

        def list_files(self, bundle_id) -> Response:
            url = Endpoints.URLBuilder(self._base_url, Endpoints.bundles.list_files) \
                .interpolate(Endpoints.interpolations.bundle_id, bundle_id)\
                .build()

            return tget(url, self._api_key)

        def list_data(self, bundle_id) -> Response:
            url = Endpoints.URLBuilder(self._base_url, Endpoints.bundles.list_data) \
                .interpolate(Endpoints.interpolations.bundle_id, bundle_id)\
                .build()

            return tget(url, self._api_key)

    class _Persons(_SubClient):
        def __init__(self, base_url, api_key):
            super().__init__(base_url, api_key)

        def create(self, data):
            url = Endpoints.URLBuilder(self._base_url, Endpoints.persons.create)\
                .build()
            return tpost(url, self._api_key, data, "application/json")

        def list(self):
            url = Endpoints.URLBuilder(self._base_url, Endpoints.persons.list) \
                .build()
            return tget(url, self._api_key)

        def retrieve(self, person_id):
            url = Endpoints.URLBuilder(self._base_url, Endpoints.persons.retrieve) \
                .interpolate(Endpoints.interpolations.person_id, person_id) \
                .build()
            return tget(url, self._api_key)

        def update(self, person_id, data):
            url = Endpoints.URLBuilder(self._base_url, Endpoints.persons.update) \
                .interpolate(Endpoints.interpolations.person_id, person_id) \
                .build()
            return tput(url, self._api_key, data, "application/json")

        def partial_update(self, person_id, data):
            url = Endpoints.URLBuilder(self._base_url, Endpoints.persons.partial_update) \
                .interpolate(Endpoints.interpolations.person_id, person_id) \
                .build()
            return tpatch(url, self._api_key, data, "application/json")

        def delete(self, person_id):
            url = Endpoints.URLBuilder(self._base_url, Endpoints.persons.delete) \
                .interpolate(Endpoints.interpolations.person_id, person_id) \
                .build()
            return tdelete(url, self._api_key)

    class _Packets(_SubClient):
        def __init__(self, base_url, api_key):
            super().__init__(base_url, api_key)

        def update(self, packet_id, data):
            url = Endpoints.URLBuilder(self._base_url, Endpoints.packets.update) \
                .interpolate(Endpoints.interpolations.packet_id, packet_id) \
                .build()
            return tpatch(url, self._api_key, data, "application/json")

        def remind(self, packet_id):
            url = Endpoints.URLBuilder(self._base_url, Endpoints.packets.remind) \
                .interpolate(Endpoints.interpolations.packet_id, packet_id) \
                .build()
            return tput(url, self._api_key)

        def retrieve_coe(self, packet_id):
            url = Endpoints.URLBuilder(self._base_url, Endpoints.packets.retrieve_coe) \
                .interpolate(Endpoints.interpolations.packet_id, packet_id) \
                .build()
            return tget(url, self._api_key)

    class _Templates(_SubClient):
        def __init__(self, base_url, api_key):
            super().__init__(base_url, api_key)

        def list(self):
            url = Endpoints.URLBuilder(self._base_url, Endpoints.templates.list) \
                .build()
            return tget(url, self._api_key)

        def retrieve(self, template_id):
            url = Endpoints.URLBuilder(self._base_url, Endpoints.templates.retrieve) \
                .interpolate(Endpoints.interpolations.template_id, template_id) \
                .build()
            return tget(url, self._api_key)

