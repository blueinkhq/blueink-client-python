from blueink import endpoints
from blueink.paginator import PaginatedIterator
from blueink.request_helper import NormalizedResponse
from blueink.subclients.subclient import SubClient


class TemplateSubClient(SubClient):
    def __init__(self, base_url, private_api_key):
        super().__init__(base_url, private_api_key)

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
