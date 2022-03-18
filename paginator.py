from copy import deepcopy
from tokenizedrequests import MunchedResult

"""
Unfinished
"""

class PagedAPICall:
    def __init__(self, paged_api_function, params, page_number_idx):
        self._paged_func = paged_api_function
        self._params = deepcopy(params)
        self._page_number_idx = page_number_idx

        self._current_page_number = params[page_number_idx]
        self._previous_page_number = None if self._current_page_number <= 0 else self._current_page_number - 1
        self._next_page_number = self._current_page_number + 1

        self._params[self._page_number_idx] = self._current_page_number
        self.api_response: MunchedResult = self._paged_func(*self._params)

        # set next page
        if self.api_response.success:
            pagination = self.api_response.http_response_headers.get("X-Blueink-Pagination").split(",")
            self._current_page_number = pagination[0]
            self._previous_page_number = None if self._current_page_number <= 0 else self._current_page_number - 1
            self._next_page_number = self._current_page_number + 1
            self.page = self.api_response

    def __iter__(self):
        return self

    def __next__(self):
        new_params = deepcopy(self._params)
        new_params[self._page_number_idx] = new_params[self._page_number_idx] + 1

        return PagedAPICall(paged_api_function=self._paged_func,
                            params=self._params,
                            page_number_idx=self._page_number_idx)
