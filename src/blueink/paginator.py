from requests.exceptions import HTTPError

from .request_helper import NormalizedResponse


class PaginatedIterator:
    def __init__(self, paged_api_function, params, page_number_idx):
        '''

        Iterator to run client functions such as client.bundles.list() in a pythonic way
        eg.

        params = [start_page, per_page]
        paged_call = PaginatedIterator(self.list, params, 0)

        for api_call in paged_call:
            print(f"API CALL: {api_call.body}")

        :param paged_api_function: function passed by reference (eg client.bundles.list())
        :param params: params for above function
        :param page_number_idx: what index in the params list corresponds to the initial page
        '''
        self._paged_func = paged_api_function
        self._params = params
        self._page_number_idx = page_number_idx
        self._total_pages = None

    def __iter__(self):
        return self

    def __next__(self):
        page_number = self._params[self._page_number_idx]

        if self._total_pages is not None and page_number > self._total_pages:
            raise StopIteration

        try:
            api_response: NormalizedResponse = self._paged_func(*self._params)
        except HTTPError:
            raise StopIteration

        if api_response.pagination is None:
            raise StopIteration

        if self._total_pages is None:
            self._total_pages = api_response.pagination.total_pages

        self._params[self._page_number_idx] = page_number + 1

        return api_response

