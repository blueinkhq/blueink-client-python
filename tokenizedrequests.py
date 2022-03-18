from munch import Munch
from requests import (Response, get, post, put, patch, delete)

"""
Helper functions to add header with user's token.txt
"""


def build_header(token, content_type=None):
    hdr = {'Authorization': f"Token {token}"}

    if content_type is not None:
        hdr['Content-Type'] = content_type

    return hdr


def tget(url, token) -> Response:
    response = get(url=url,
                   headers=build_header(token))


    return response


def tpost(url, token, data=None, content_type=None) -> Response:
    response = post(url=url,
                    data=data,
                    headers=build_header(token, content_type))
    return response


def tput(url, token, data=None, content_type=None) -> Response:
    response = put(url=url,
                   data=data,
                   headers=build_header(token, content_type))
    return response


def tdelete(url, token, data=None, content_type=None):
    response = delete(url=url,
                      data=data,
                      headers=build_header(token, content_type))
    return response


def tpatch(url, token, data=None, content_type=None):
    response = patch(url=url,
                     data=data,
                     headers=build_header(token, content_type))



