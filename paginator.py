from copy import deepcopy
from tokenizedrequests import MunchedResult


class PagedAPICall:
    def __init__(self, paged_api_function, params, page_number_idx):
        '''

        Iterator to run client functions such as client.bundles.list() in a pythonic way
        eg.

        for api_call in client.bundles.list_iter(start_page=1, per_page=2):
            print(f"API CALL: {api_call.body}")

        :param paged_api_function: function passed by reference (eg client.bundles.list())
        :param params: params for above function
        :param page_number_idx: what index in the params list corresponds to the initial page
        '''
        self._paged_func = paged_api_function
        self._params = params
        self._page_number_idx = page_number_idx

        self._page_number = params[page_number_idx]
        self._total_pages = None

    def __iter__(self):
        return self

    def __next__(self):
        api_response: MunchedResult = self._paged_func(*self._params)

        # set fields based on API call
        if api_response.success:
            self._total_pages = api_response.total_pages

        if not api_response.success:
            raise StopIteration

        next_page_number = self._page_number + 1

        if next_page_number > api_response.total_pages + 1:
            raise StopIteration

        self._params[self._page_number_idx] = next_page_number
        self._page_number = next_page_number
        return api_response

