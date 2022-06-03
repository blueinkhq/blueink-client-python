import io
import json

import requests

from munch import munchify

"""
Helper functions to add header with user's token.txt
"""


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
        """
        Encapsulates the response from a BlueInk REST endpoint in a "Munch" of the JSON body.
        Status code and pagination also included.

        This will error out if JSON is not returned.
        :param response:
        """
        self.data = munchify(json.loads(response.content))
        self.status = response.status_code

        # Pagination
        self.pagination = None
        if "X-Blueink-Pagination" in response.headers:
            self.pagination = Pagination(response.headers.get("X-Blueink-Pagination"))


def build_header(private_api_key, content_type=None):
    """
    Builds header with API key, optional content-type.
    :param private_api_key:
    :param content_type:
    :return:
    """
    if private_api_key is None:
        raise RuntimeError("Private API key must be supplied.")

    hdr = {'Authorization': f"Token {private_api_key}"}

    if content_type is not None:
        hdr['Content-Type'] = content_type

    return hdr


class RequestHelper:
    def __init__(self, private_api_key):
        self._private_api_key = private_api_key

    def delete(self, url, **kwargs):
        return self._make_request('delete', url, **kwargs)

    def get(self, url, **kwargs):
        return self._make_request('get', url, **kwargs)

    def patch(self, url, **kwargs):
        return self._make_request('patch', url, **kwargs)

    def post(self, url, **kwargs):
        return self._make_request('post', url, **kwargs)

    def put(self, url, **kwargs):
        return self._make_request('put', url, **kwargs)

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

        hdrs['Authorization'] = f"Token {self._private_api_key}"

        if content_type is not None:
           hdrs['Content-Type'] = content_type

        return hdrs

    def _make_request(self, method, url, data=None, files=None, params=None, headers=None, content_type=None):
        response = requests.request(
            method,
            url,
            params=params,
            data=data,
            files=files,
            headers=self._build_headers(content_type=content_type, more_headers=headers)
        )
        response.raise_for_status()
        return NormalizedResponse(response)


def tget(url, private_api_key, params=None) -> NormalizedResponse:
    """
    Wrapped requests get request with proper header
    :param url:
    :param private_api_key:
    :param params:
    :return:
    """
    response = requests.get(url=url,
                   headers=build_header(private_api_key),
                   params=params)

    return NormalizedResponse(response)


def tpost(url, private_api_key, data=None, content_type="application/json") -> NormalizedResponse:
    """
    Wrapped requests post request with proper header, taking json data
    :param url:
    :param private_api_key:
    :param data: json data
    :param content_type:
    :return:
    """
    response = requests.post(url=url,
                    data=data,
                    headers=build_header(private_api_key, content_type))
    return NormalizedResponse(response)


def tpost_formdata(url, private_api_key, json_data=None, files=[io.BufferedReader], file_names=[str], content_types=[str]) -> NormalizedResponse:
    """
    Wrapped requests post request with proper header
    :param url:
    :param private_api_key:
    :param json_data:
    :param files: array of file like objects (io.BufferedReader)
    :param file_names: array of filenames
    :param content_types: array of content types (eg 'application/pdf')
    :return:
    """
    # construct form_data dict
    form_data = {
        'bundle_request': (None, json_data, "application/json") # 'None' filename is a must or server 500's out
    }
    for file_index, file in enumerate(files):
        if type(file) == io.BufferedReader:
            formdata_file = (file_names[file_index], file, content_types[file_index])
            form_data[f'files[{file_index}]'] = formdata_file
        else:
            raise RuntimeError("File is not of io.BufferedReader type!")

    response = requests.post(url=url,
                    files=form_data,
                    headers=build_header(private_api_key))

    return NormalizedResponse(response)


def tput(url, private_api_key, data=None, content_type=None) -> NormalizedResponse:
    """
    Wrapped requests put request with proper header
    :param url:
    :param private_api_key:
    :param data:
    :param content_type:
    :return:
    """
    response = requests.put(url=url,
                   data=data,
                   headers=build_header(private_api_key, content_type))
    return NormalizedResponse(response)


def tdelete(url, private_api_key, data=None, content_type=None) -> NormalizedResponse:
    """
    Wrapped requests delete request with proper header
    :param url:
    :param private_api_key:
    :param data:
    :param content_type:
    :return:
    """
    response = requests.delete(url=url,
                      data=data,
                      headers=build_header(private_api_key, content_type))
    return NormalizedResponse(response)


def tpatch(url, private_api_key, data=None, content_type=None) -> NormalizedResponse:
    """
    Wrapped requests patch request with proper header
    :param url:
    :param private_api_key:
    :param data:
    :param content_type:
    :return:
    """
    response = requests.patch(url=url,
                     data=data,
                     headers=build_header(private_api_key, content_type))
    return NormalizedResponse(response)
