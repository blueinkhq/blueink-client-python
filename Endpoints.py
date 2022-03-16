from munch import Munch

bundles = Munch(
    create="/bundles/",
    list="/bundles/",
    retrieve="/bundles/{bundle_id}/",
    cancel="/bundles/{bundle_id}/cancel/",
    list_events="/bundles/{bundle_id}/events/",
    list_files="/bundles/{bundle_id}/files/",
    list_data="/bundles/{bundle_id}/data/"
)

interpolations = Munch(
    bundle_id="{bundle_id}"
)


class URLBuilder:
    def __init__(self, base_url, endpoint: str):
        self.base_url = base_url
        self.endpoint = endpoint

    def interpolate(self, variable: str, value):
        self.endpoint = self.endpoint.replace(variable, str(value))
        return self

    def build(self):
        return self.base_url + self.endpoint