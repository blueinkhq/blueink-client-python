import json
from munch import munchify
from requests import (Response, get, post, put, patch, delete)

"""
Helper functions to add header with user's token.txt
"""


class MunchedResult:
    def __init__(self, response: Response):
        self.success = True if response.status_code == 200 else False
        self.content_size = len(response.content)
        self.body = munchify(json.loads(response.content))
        self.http_response_code = response.status_code

        # Pagination
        self.paginated = False
        self.page_number = None
        self.total_pages = None
        self.items_on_page = None
        self.total_results = None

        if "X-Blueink-Pagination" in response.headers:
            self.paginated = True
            pagination = response.headers.get("X-Blueink-Pagination").split(",")
            self.page_number = int(pagination[0])
            self.total_pages = int(pagination[1])
            self.items_on_page = int(pagination[2])
            self.total_results = int(pagination[3])


def build_header(token, content_type=None):
    hdr = {'Authorization': f"Token {token}"}

    if content_type is not None:
        hdr['Content-Type'] = content_type

    return hdr


def build_pagination_params(page_number, per_page=None):
    params = {
        "page": page_number,
        "per_page":per_page
    }

    return params


def tget(url, token, params=None) -> MunchedResult:
    response = get(url=url,
                   headers=build_header(token),
                   params=params)

    return MunchedResult(response)


def tpost(url, token, data=None, content_type=None) -> MunchedResult:
    response = post(url=url,
                    data=data,
                    headers=build_header(token, content_type))
    return MunchedResult(response)


def tput(url, token, data=None, content_type=None) -> MunchedResult:
    response = put(url=url,
                   data=data,
                   headers=build_header(token, content_type))
    return MunchedResult(response)


def tdelete(url, token, data=None, content_type=None) -> MunchedResult:
    response = delete(url=url,
                      data=data,
                      headers=build_header(token, content_type))
    return MunchedResult(response)


def tpatch(url, token, data=None, content_type=None) -> MunchedResult:
    response = patch(url=url,
                     data=data,
                     headers=build_header(token, content_type))
    return MunchedResult(response)



