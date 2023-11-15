from blueink import endpoints
from blueink.request_helper import RequestHelper


class SubClient:
    def __init__(self, base_url: str, requests_helper: RequestHelper):
        self._base_url = base_url
        self._requests = requests_helper

    def build_url(self, endpoint: str, **kwargs):
        """Shortcut to build a URL using endpoints.URLBuilder

        Args:
            endpoint: one of the API endpoints, e.g. endpoints.BUNDLES.create
            **kwargs: the arg name should be one of the keys in endpoints.
            interpolations, and the arg value will be substituted for the named
            placeholder in the endpoint str

        Returns:
            The URL as a str

        Raises:
            ValueError if one of the kwargs is not a valid endpoint
            interpolation key
        """
        # All of our current endpoints take 1 parameter, max
        if len(kwargs) > 1:
            raise ValueError("Only one interpolation parameter is allowed")

        try:
            url = endpoints.URLBuilder(self._base_url, endpoint).build(**kwargs)
        except KeyError:
            arg_name = list(kwargs.keys())[0]
            raise ValueError(
                f'Invalid substitution argument "{arg_name}"'
                f' provided for endpoint "{endpoint}"'
            )

        return url

    @staticmethod
    def build_params(page: int = None, per_page: int = None, **query_params):
        params = dict(**query_params)

        # page could be zero, although Blueink pagination is 1-indexed
        if page is not None:
            params["page"] = page

        if per_page:
            params["per_page"] = per_page

        return params
