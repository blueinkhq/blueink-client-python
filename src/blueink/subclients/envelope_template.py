from blueink import endpoints
from blueink.paginator import PaginatedIterator
from blueink.request_helper import NormalizedResponse
from blueink.subclients.subclient import SubClient


class EnvelopeTemplateSubClient(SubClient):
    def paged_list(
        self, page: int = 1, per_page: int = 50, **query_params
    ) -> PaginatedIterator:
        """Return an iterable object containing a list of envelope templates

        Typical Usage:
            for page in client.envelope_templates.paged_list():
                page.body -> munch of json

        Args:
            page: start page (default 1)
            per_page: max # of results per page (default 50)
            query_params: Additional query params to be put onto the request

        Returns:
            PaginatedIterator object
        """
        iterator = PaginatedIterator(
            paged_api_function=self.list, page=page, per_page=per_page, **query_params
        )
        return iterator

    def list(
        self, page: int = None, per_page: int = None, **query_params
    ) -> NormalizedResponse:
        """Return a list of Envelope Templates.

        Envelope Templates are reusable document workflows that contain predefined
        documents, field layouts, signer roles, and configuration settings.

        Args:
            page: which page to fetch
            per_page: how many templates to fetch
            query_params: Additional query params to be put onto the request

        Returns:
            NormalizedResponse object
        """
        url = self.build_url(endpoints.ENVELOPE_TEMPLATES.LIST)
        return self._requests.get(
            url, params=self.build_params(page, per_page, **query_params)
        )

    def retrieve(self, envelope_template_id: str) -> NormalizedResponse:
        """Return a singular Envelope Template by id.

        Args:
            envelope_template_id: The ID that uniquely identifies the Envelope Template

        Returns:
            NormalizedResponse object
        """
        url = self.build_url(
            endpoints.ENVELOPE_TEMPLATES.RETRIEVE,
            envelope_template_id=envelope_template_id,
        )
        return self._requests.get(url)
