from os import environ

from blueink.constants import (
    DEFAULT_BASE_URL,
    ENV_BLUEINK_API_URL,
    ENV_BLUEINK_PRIVATE_API_KEY,
)
from blueink.request_helper import RequestHelper
from blueink.subclients.bundle import BundleSubClient
from blueink.subclients.packet import PacketSubClient
from blueink.subclients.person import PersonSubClient
from blueink.subclients.template import TemplateSubClient
from blueink.subclients.webhook import WebhookSubClient


class Client:
    def __init__(
        self,
        private_api_key: str = None,
        base_url: str = None,
        raise_exceptions: bool = True,
    ):
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

        self._base_url = base_url

        self._request_helper = RequestHelper(private_api_key, raise_exceptions)

        self.bundles = BundleSubClient(self._base_url, self._request_helper)
        self.persons = PersonSubClient(self._base_url, self._request_helper)
        self.packets = PacketSubClient(self._base_url, self._request_helper)
        self.templates = TemplateSubClient(self._base_url, self._request_helper)
        self.webhooks = WebhookSubClient(self._base_url, self._request_helper)
