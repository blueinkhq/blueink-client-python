from string import Template

# Note, this module abuses Classes to achieve a namespace, where SimpleNameSpace
# or something similar might be more appropriate. However, afaik none of those
# solutions have good auto-completion support in IDEs.
# So we do it this way. ¯\_(ツ)_/¯


class BUNDLES:
    CREATE = "/bundles/"
    LIST = "/bundles/"
    RETRIEVE = "/bundles/${bundle_id}/"
    CANCEL = "/bundles/${bundle_id}/cancel/"
    LIST_EVENTS = "/bundles/${bundle_id}/events/"
    LIST_FILES = "/bundles/${bundle_id}/files/"
    LIST_DATA = "/bundles/${bundle_id}/data/"


class PERSONS:
    CREATE = "/persons/"
    LIST = "/persons/"
    RETRIEVE = "/persons/${person_id}/"
    UPDATE = "/persons/${person_id}/"
    DELETE = "/persons/${person_id}/"


class PACKETS:
    EMBED_URL = "/packets/${packet_id}/embed_url/"
    UPDATE = "/packets/${packet_id}/"
    REMIND = "/packets/${packet_id}/remind/"
    RETRIEVE_COE = "/packets/${packet_id}/coe/"


class TEMPLATES:
    LIST = "/templates/"
    RETRIEVE = "/templates/${template_id}/"


class URLBuilder:
    def __init__(self, base_url, endpoint: str):
        self._base_url = base_url
        self._endpoint = endpoint

    def build(self, **kwargs):
        return self._base_url + Template(self._endpoint).substitute(**kwargs)
