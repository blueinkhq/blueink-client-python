import json
from munch import munchify
from requests import (Response, get, post, put, patch, delete)

"""
Helper functions to add header with user's token.txt
"""


class Pagination:
    def __init__(self, pagination_header: str):
        pagination_split = pagination_header.split(",")
        self.page_number = int(pagination_split[0])
        self.total_pages = int(pagination_split[1])
        self.items_on_page = int(pagination_split[2])
        self.total_results = int(pagination_split[3])


class MunchedResponse:
    def __init__(self, response: Response):
        self.data = munchify(json.loads(response.content))
        self.status = response.status_code

        # Pagination
        self.pagination = None
        if "X-Blueink-Pagination" in response.headers:
            self.pagination = Pagination(response.headers.get("X-Blueink-Pagination"))


def build_header(private_api_key, content_type=None):
    hdr = {'Authorization': f"Token {private_api_key}"}

    if content_type is not None:
        hdr['Content-Type'] = content_type

    return hdr


def build_pagination_params(page_number, per_page=None):
    params = {
        "page": page_number,
        "per_page": per_page
    }

    return params


def tget(url, private_api_key, params=None) -> MunchedResponse:
    response = get(url=url,
                   headers=build_header(private_api_key),
                   params=params)

    return MunchedResponse(response)


def tpost(url, private_api_key, data=None, content_type="application/json") -> MunchedResponse:
    response = post(url=url,
                    data=data,
                    headers=build_header(private_api_key, content_type))
    return MunchedResponse(response)


def tpost_formdata(url, private_api_key, json_data=None, files=[], content_types=[]) -> MunchedResponse:

    print(json_data)
    print(type(json_data))
    form_data = {
        'bundle_request': (json_data, "application/json"),
    }

    for file_index, file in enumerate(files):
        formdata_file = (file.name, file, content_types[file_index])
        form_data[f'files[{file_index}]'] = formdata_file

    response = post(url=url,
                    data=form_data,
                    headers=build_header(private_api_key))

    print(response.content)

    return MunchedResponse(response)


def tput(url, private_api_key, data=None, content_type=None) -> MunchedResponse:
    response = put(url=url,
                   data=data,
                   headers=build_header(private_api_key, content_type))
    return MunchedResponse(response)


def tdelete(url, private_api_key, data=None, content_type=None) -> MunchedResponse:
    response = delete(url=url,
                      data=data,
                      headers=build_header(private_api_key, content_type))
    return MunchedResponse(response)


def tpatch(url, private_api_key, data=None, content_type=None) -> MunchedResponse:
    response = patch(url=url,
                     data=data,
                     headers=build_header(private_api_key, content_type))
    return MunchedResponse(response)
