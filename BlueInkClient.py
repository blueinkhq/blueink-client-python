from requests import Response
from os import environ
from TokenizedRequests import (tget, tpost, tput, tpatch, tdelete)
import Endpoints


class Client:
    def __init__(self, override_base_url=None, override_api_key=None):
        base_url = override_base_url if override_base_url is not None else environ['BLUEINK_API_URI']
        api_key = override_api_key if override_api_key is not None else environ['BLUEINK_API_KEY']

        self.bundles = self.__Bundles__(base_url, api_key)
        self.persons = self.__Persons__(base_url, api_key)
        self.packets = self.__Packets__(base_url, api_key)
        self.templates = self.__Templates__(base_url, api_key)

    class __SubClient__:
        def __init__(self, base_url, api_key):
            self.__base_url__ = base_url
            self.__api_key__ = api_key

    class __Bundles__(__SubClient__):
        def __init__(self, base_url, api_key):
            super().__init__(base_url, api_key)

        def create(self, data) -> Response:
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.bundles.create) \
                .build()

            return tpost(url, self.__api_key__, data, "application/json")

        def list(self) -> Response:
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.bundles.list)\
                .build()

            return tget(url, self.__api_key__)

        def retrieve(self, bundle_id) -> Response:
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.bundles.retrieve)\
                .interpolate(Endpoints.interpolations.bundle_id, bundle_id)\
                .build()

            return tget(url, self.__api_key__)

        def cancel(self, bundle_id) -> Response:
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.bundles.cancel) \
                .interpolate(Endpoints.interpolations.bundle_id, bundle_id)\
                .build()

            return tput(url, self.__api_key__)

        def list_events(self, bundle_id) -> Response:
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.bundles.list_events) \
                .interpolate(Endpoints.interpolations.bundle_id, bundle_id)\
                .build()

            return tget(url, self.__api_key__)

        def list_files(self, bundle_id) -> Response:
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.bundles.list_files) \
                .interpolate(Endpoints.interpolations.bundle_id, bundle_id)\
                .build()

            return tget(url, self.__api_key__)

        def list_data(self, bundle_id) -> Response:
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.bundles.list_data) \
                .interpolate(Endpoints.interpolations.bundle_id, bundle_id)\
                .build()

            return tget(url, self.__api_key__)

    class __Persons__(__SubClient__):
        def __init__(self, base_url, api_key):
            super().__init__(base_url, api_key)

        def create(self, data):
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.persons.create)\
                .build()
            return tpost(url, self.__api_key__, data, "application/json")

        def list(self):
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.persons.list) \
                .build()
            return tget(url, self.__api_key__)

        def retrieve(self, person_id):
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.persons.retrieve) \
                .interpolate(Endpoints.interpolations.person_id, person_id) \
                .build()
            return tget(url, self.__api_key__)

        def update(self, person_id, data):
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.persons.update) \
                .interpolate(Endpoints.interpolations.person_id, person_id) \
                .build()
            return tput(url, self.__api_key__, data, "application/json")

        def partial_update(self, person_id, data):
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.persons.partial_update) \
                .interpolate(Endpoints.interpolations.person_id, person_id) \
                .build()
            return tpatch(url, self.__api_key__, data, "application/json")

        def delete(self, person_id):
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.persons.delete) \
                .interpolate(Endpoints.interpolations.person_id, person_id) \
                .build()
            return tdelete(url, self.__api_key__)

    class __Packets__(__SubClient__):
        def __init__(self, base_url, api_key):
            super().__init__(base_url, api_key)

        def update(self, packet_id, data):
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.packets.update) \
                .interpolate(Endpoints.interpolations.packet_id, packet_id) \
                .build()
            return tpatch(url, self.__api_key__, data, "application/json")

        def remind(self, packet_id):
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.packets.remind) \
                .interpolate(Endpoints.interpolations.packet_id, packet_id) \
                .build()
            return tput(url, self.__api_key__)

        def retrieve_coe(self, packet_id):
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.packets.retrieve_coe) \
                .interpolate(Endpoints.interpolations.packet_id, packet_id) \
                .build()
            return tget(url, self.__api_key__)

    class __Templates__(__SubClient__):
        def __init__(self, base_url, api_key):
            super().__init__(base_url, api_key)

        def list(self):
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.templates.list) \
                .build()
            return tget(url, self.__api_key__)

        def retrieve(self, template_id):
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.templates.retrieve) \
                .interpolate(Endpoints.interpolations.template_id, template_id) \
                .build()
            return tget(url, self.__api_key__)

