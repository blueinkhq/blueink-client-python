import requests

from munch import munchify

from .constants import BLUEINK_PAGINATION_HEADER


class Pagination:
    def __init__(self, pagination_header: str):
        """
        Pagination fields parsed out for BlueInk paged responses
        :param pagination_header: from header 'X-Blueink-Pagination'
        """
        pagination_split = pagination_header.split(",")
        self.page_number = int(pagination_split[0])
        self.total_pages = int(pagination_split[1])
        self.per_page = int(pagination_split[2])
        self.total_results = int(pagination_split[3])

    def __str__(self):
        return (
            f"page_number: {self.page_number}, per_page: {self.per_page}, "
            f"total_pages: {self.total_pages}, total_results: {self.total_results}"
        )


class NormalizedResponse:
    def __init__(self, response: requests.Response):
        """Encapsulates the response from a BlueInk REST endpoint

        The response data is available via the `data` attribute and supports
        both dictionary-style access (`data['id']`) and dot access (`data.id`).

        Status code and pagination also included.

        This will error out if JSON is not returned.
        :param response:
        """
        try:
            self.data = munchify(response.json())
        except requests.exceptions.JSONDecodeError:
            # Some responses (e.g. 500) have no content or html responses
            self.data = response.content

        self.request = response.request
        self.status = response.status_code
        self.original_response = response

        # Pagination
        self.pagination = None
        if BLUEINK_PAGINATION_HEADER in response.headers:
            self.pagination = Pagination(
                response.headers.get(BLUEINK_PAGINATION_HEADER)
            )


class RequestHelper:
    def __init__(self, private_api_key):
        self._private_api_key = private_api_key

    def delete(self, url, **kwargs):
        return self._make_request("delete", url, **kwargs)

    def get(self, url, **kwargs):
        return self._make_request("get", url, **kwargs)

    def patch(self, url, **kwargs):
        return self._make_request("patch", url, **kwargs)

    def post(self, url, **kwargs):
        return self._make_request("post", url, **kwargs)

    def put(self, url, **kwargs):
        return self._make_request("put", url, **kwargs)

    def _build_headers(self, content_type=None, more_headers=None):
        """
        Builds header with API key, optional content-type.
        :param private_api_key:
        :param content_type:
        :return:
        """
        if self._private_api_key is None:
            raise RuntimeError("Private API key must be supplied.")

        hdrs = {}
        if more_headers:
            hdrs.update(more_headers)

        hdrs["Authorization"] = f"Token {self._private_api_key}"

        if content_type is not None:
            hdrs["Content-Type"] = content_type

        return hdrs

    def _make_request(
        self, method, url, data=None, json=None, files=None, params=None, headers=None, content_type=None
    ):
        response = requests.request(
            method,
            url,
            params=params,
            data=data,
            json=json,
            headers=self._build_headers(content_type=content_type, more_headers=headers),
            files=files,
        )
        response.raise_for_status()
        return NormalizedResponse(response)
