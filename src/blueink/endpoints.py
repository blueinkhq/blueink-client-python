from urllib import parse
from munch import Munch

bundles = Munch(
    create="/bundles/",
    list="/bundles/",
    retrieve="/bundles/{bundle_id}/",
    cancel="/bundles/{bundle_id}/cancel/",
    list_events="/bundles/{bundle_id}/events/",
    list_files="/bundles/{bundle_id}/files/",
    list_data="/bundles/{bundle_id}/data/",
)

persons = Munch(
    create="/persons/",
    list="/persons/",
    retrieve="/persons/{person_id}/",
    full_update="/persons/{person_id}/",
    partial_update="/persons/{person_id}/",
    delete="/persons/{person_id}/",
)

packets = Munch(
    full_update="/packets/{packet_id}/", remind="/packets/{packet_id}/remind/", retrieve_coe="/packets/{packet_id}/coe/"
)

templates = Munch(list="/templates/", retrieve="/templates/{template_id}/")

interpolations = Munch(
    bundle_id="{bundle_id}", person_id="{person_id}", packet_id="{packet_id}", template_id="{template_id}"
)


class URLBuilder:
    def __init__(self, base_url, endpoint: str):
        self._base_url = base_url
        self._endpoint = endpoint

    def interpolate(self, variable: str, value):
        self._endpoint = self._endpoint.replace(variable, str(value))
        return self

    def build(self):
        return self._base_url + self._endpoint
