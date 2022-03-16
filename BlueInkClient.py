from requests import Response
from TokenizedRequests import (tget, tpost, tput, tpatch, tdelete)
import Endpoints


class Client:
    def __init__(self, base_url="https://api.blueink.com/api/v2", user_token=None):
        if not user_token:
            raise RuntimeError("No user token.txt supplied")

        self.bundles = self.__Bundles__(base_url, user_token)

    class __SubClient__:
        def __init__(self, base_url, user_token):
            self.__base_url__ = base_url
            self.__token__ = user_token

    class __Bundles__(__SubClient__):
        def __init__(self, base_url, user_token):
            super().__init__(base_url, user_token)

        def create(self, data) -> Response:
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.bundles.create) \
                .build()

            return tpost(url, self.__token__, data)

        def list(self) -> Response:
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.bundles.list)\
                .build()

            return tget(url, self.__token__)

        def retrieve(self, bundle_id) -> Response:
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.bundles.retrieve)\
                .interpolate(Endpoints.interpolations.bundle_id, bundle_id)\
                .build()

            return tget(url, self.__token__)

        def cancel(self, bundle_id) -> Response:
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.bundles.cancel) \
                .interpolate(Endpoints.interpolations.bundle_id, bundle_id)\
                .build()

            return tput(url, self.__token__)

        def list_events(self, bundle_id) -> Response:
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.bundles.list_events) \
                .interpolate(Endpoints.interpolations.bundle_id, bundle_id)\
                .build()

            return tget(url, self.__token__)

        def list_files(self, bundle_id) -> Response:
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.bundles.list_files) \
                .interpolate(Endpoints.interpolations.bundle_id, bundle_id)\
                .build()

            return tget(url, self.__token__)

        def list_data(self, bundle_id) -> Response:
            url = Endpoints.URLBuilder(self.__base_url__, Endpoints.bundles.list_data) \
                .interpolate(Endpoints.interpolations.bundle_id, bundle_id)\
                .build()

            return tget(url, self.__token__)


c = Client(user_token="000")

