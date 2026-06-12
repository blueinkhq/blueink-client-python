from blueink import endpoints
from blueink.paginator import PaginatedIterator
from blueink.request_helper import NormalizedResponse
from blueink.subclients.subclient import SubClient


class TemplateSubClient(SubClient):
    def paged_list(
        self, page: int = 1, per_page: int = 50, **query_params
    ) -> PaginatedIterator:
        """return an iterable object containing a list of templates

        Typical Usage:
            for page in client.templates.paged_list():
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
        """Return a list of Templates.

        Args:
            page:
            per_page:
            query_params: Additional query params to be put onto the request

        Returns:
            NormalizedResponse object
        """
        url = self.build_url(endpoints.TEMPLATES.LIST)
        return self._requests.get(
            url, params=self.build_params(page, per_page, **query_params)
        )

    def retrieve(self, template_id: str) -> NormalizedResponse:
        """Return a singular Template by id.

        Args:
            template_id:

        Returns:
            NormalizedResponse object
        """
        url = self.build_url(endpoints.TEMPLATES.RETRIEVE, template_id=template_id)
        return self._requests.get(url)

    def update(self, template_id: str, data: dict) -> NormalizedResponse:
        """Partially update a Template.

        Typically used to write template metadata, e.g.
        ``{"metadata": {"key": "value"}}``.

        Args:
            template_id:
            data: dict of fields to update on the template

        Returns:
            NormalizedResponse object
        """
        if not data:
            raise ValueError("data is required")

        url = self.build_url(endpoints.TEMPLATES.UPDATE, template_id=template_id)
        return self._requests.patch(url, json=data)

    def create_preparation_session(self, data: dict) -> NormalizedResponse:
        """Create an embedded template preparation session.

        Creates a secure, time-limited URL that can be embedded in an iframe to allow
        end users to prepare a template through your application.

        Args:
            data: configuration for the preparation session. Supported keys:
                - template_id (str, optional): slug of an existing template to edit
                - redirect_url (str, optional): URL to redirect to after preparation

        Returns:
            NormalizedResponse object with keys:
                - url: the preparation session URL to embed in an iframe
                - expires: ISO 8601 timestamp when the session URL expires
        """
        if not data:
            raise ValueError("data is required")

        url = self.build_url(endpoints.TEMPLATES.CREATE_PREPARATION_SESSION)
        return self._requests.post(url, json=data)
