from blueink import endpoints
from blueink.request_helper import NormalizedResponse
from blueink.subclients.subclient import SubClient


class VerifySubClient(SubClient):
    def create(self, data: dict) -> NormalizedResponse:
        """Verify a signed PDF against the Blueink application (POST /verify/).

        Args:
            data: dict containing the ``hash`` (sha256) of the document to verify

        Returns:
            NormalizedResponse object, with verification details as `data`
        """
        if not data:
            raise ValueError("data is required")

        url = self.build_url(endpoints.VERIFY.CREATE)
        return self._requests.post(url, json=data)
