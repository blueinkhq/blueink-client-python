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


class WEBHOOKS:
    CREATE = "/webhooks/"
    LIST = "/webhooks/"
    RETRIEVE = "/webhooks/${webhook_id}/"
    UPDATE = "/webhooks/${webhook_id}/"
    DELETE = "/webhooks/${webhook_id}/"

    CREATE_HEADER = "/webhooks/headers/"
    LIST_HEADERS = "/webhooks/headers/"
    RETRIEVE_HEADER = "/webhooks/headers/${webhook_header_id}/"
    UPDATE_HEADER = "/webhooks/headers/${webhook_header_id}/"
    DELETE_HEADER = "/webhooks/headers/${webhook_header_id}/"

    LIST_EVENTS = "/webhooks/events/"
    RETRIEVE_EVENT = "/webhooks/events/${webhook_event_id}/"

    LIST_DELIVERIES = "/webhooks/deliveries/"
    RETRIEVE_DELIVERY = "/webhooks/deliveries/${webhook_delivery_id}/"

    RETRIEVE_SECRET = "/webhooks/secret/"
    REGENERATE_SECRET = "/webhooks/secret/regenerate/"


class URLBuilder:
    def __init__(self, base_url, endpoint: str):
        self._base_url = base_url
        self._endpoint = endpoint

    def build(self, **kwargs):
        return self._base_url + Template(self._endpoint).substitute(**kwargs)
