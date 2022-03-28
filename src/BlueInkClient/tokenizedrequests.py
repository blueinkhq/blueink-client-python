import io
import json
from munch import munchify
from requests import (Response, get, post, put, patch, delete)

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
        self.items_on_page = int(pagination_split[2])
        self.total_results = int(pagination_split[3])


class MunchedResponse:
    def __init__(self, response: Response):
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


def build_pagination_params(page_number, per_page=None):
    """
    Builds pagination URL params dict for requests' params field.
    :param page_number:
    :param per_page:
    :return:
    """
    params = {
        "page": page_number,
        "per_page": per_page
    }

    return params


def tget(url, private_api_key, params=None) -> MunchedResponse:
    """
    Wrapped requests get request with proper header
    :param url:
    :param private_api_key:
    :param params:
    :return:
    """
    response = get(url=url,
                   headers=build_header(private_api_key),
                   params=params)

    return MunchedResponse(response)


def tpost(url, private_api_key, data=None, content_type="application/json") -> MunchedResponse:
    """
    Wrapped requests post request with proper header, taking json data
    :param url:
    :param private_api_key:
    :param data: json data
    :param content_type:
    :return:
    """
    response = post(url=url,
                    data=data,
                    headers=build_header(private_api_key, content_type))
    return MunchedResponse(response)


def tpost_formdata(url, private_api_key, json_data=None, files=[io.BufferedReader], file_names=[str], content_types=[str]) -> MunchedResponse:
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

    response = post(url=url,
                    files=form_data,
                    headers=build_header(private_api_key))

    return MunchedResponse(response)


def tput(url, private_api_key, data=None, content_type=None) -> MunchedResponse:
    """
    Wrapped requests put request with proper header
    :param url:
    :param private_api_key:
    :param data:
    :param content_type:
    :return:
    """
    response = put(url=url,
                   data=data,
                   headers=build_header(private_api_key, content_type))
    return MunchedResponse(response)


def tdelete(url, private_api_key, data=None, content_type=None) -> MunchedResponse:
    """
    Wrapped requests delete request with proper header
    :param url:
    :param private_api_key:
    :param data:
    :param content_type:
    :return:
    """
    response = delete(url=url,
                      data=data,
                      headers=build_header(private_api_key, content_type))
    return MunchedResponse(response)


def tpatch(url, private_api_key, data=None, content_type=None) -> MunchedResponse:
    """
    Wrapped requests patch request with proper header
    :param url:
    :param private_api_key:
    :param data:
    :param content_type:
    :return:
    """
    response = patch(url=url,
                     data=data,
                     headers=build_header(private_api_key, content_type))
    return MunchedResponse(response)
