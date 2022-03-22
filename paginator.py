from copy import deepcopy
from tokenizedrequests import MunchedResponse


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

    def __iter__(self):
        return self

    def __next__(self):
        api_response: MunchedResponse = self._paged_func(*self._params)

        if api_response.status != 200:
            raise StopIteration

        if api_response.pagination is None:
            raise StopIteration

        next_page_number = api_response.pagination.page_number + 1
        if next_page_number > api_response.pagination.total_pages + 1:
            raise StopIteration

        self._params[self._page_number_idx] = next_page_number
        self._page_number = next_page_number
        return api_response

