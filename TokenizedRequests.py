from requests import (Response, get, post, put, patch, delete)

"""
Helper functions to add header with user's token.txt
"""

def build_header(token):
    return {'Authorization': token}


def tget(url, token) -> Response:
    response = get(url=url,
                   headers=build_header(token))
    return response


def tpost(url, token, data) -> Response:
    response = post(url=url,
                    data=data,
                    headers=build_header(token))
    return response


def tput(url, token, data) -> Response:
    response = put(url=url,
                   data=data,
                   headers=build_header(token))
    return response


def tdelete(url, token, data):
    response = delete(url=url,
                      data=data,
                      headers=build_header(token))
    return response


def tpatch(url, token, data):
    response = patch(url=url,
                     data=data,
                     headers=build_header(token))



