from requests.exceptions import HTTPError

from .request_helper import NormalizedResponse


class PaginatedIterator:
    def __init__(self, paged_api_function, page=1, per_page=50, **kwargs):
        """

        Iterator to run client functions such as client.bundles.list() in a pythonic way
        eg.
        paged_call = PaginatedIterator(self.list, page=1, per_page=50, related_data=False)

        for api_call in paged_call:
            print(f"API CALL: {api_call.body}")

        :param paged_api_function: function passed by reference (eg client.bundles.list())
        :param page: starting page (default 1); BlueInk pagination starts at 1
        :param per_page: items per page (default 50)
        :param kwargs: Query params to be passed to the paged_api_function
        """
        self._paged_func = paged_api_function
        self._starting_page = page
        self._items_per_page = per_page
        self._paged_func_args = kwargs

        self._total_pages = None
        self.next_page = self._starting_page

    def __iter__(self):
        return self

    def __next__(self):
        if self._total_pages is not None and self.next_page > self._total_pages:
            raise StopIteration

        try:
            api_response: NormalizedResponse = self._paged_func(page=self.next_page,
                                                                per_page=self._items_per_page,
                                                                **self._paged_func_args)
        except HTTPError:
            raise StopIteration

        if api_response.pagination is None:
            raise StopIteration

        if self._total_pages is None:
            self._total_pages = api_response.pagination.total_pages

        self.next_page = self.next_page + 1
        return api_response

