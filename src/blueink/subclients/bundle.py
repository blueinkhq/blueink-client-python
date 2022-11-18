import io
import json
from typing import List

from munch import Munch

from blueink import endpoints
from blueink.bundle_helper import BundleHelper
from blueink.constants import BUNDLE_STATUS
from blueink.paginator import PaginatedIterator
from blueink.request_helper import NormalizedResponse
from blueink.subclients.subclient import SubClient


class BundleSubClient(SubClient):
    def _prepare_files(self, file_list: [io.BufferedReader]):
        if isinstance(file_list, dict):
            file_list = [file_list]

        files_data = []
        if file_list:
            for idx, file_dict in enumerate(file_list):
                if "file" in file_dict:
                    fh = file_dict["file"]
                    if not isinstance(fh, io.BufferedReader):
                        raise ValueError(
                            f"Bad type for file {idx}. Expected an io.BufferedReader"
                            f" (e.g. an open file handle)"
                        )
                    field_name = f"files[{idx}]"
                    files_data.append(
                        (
                            field_name,
                            (
                                file_dict.get("filename"),
                                fh,
                                file_dict.get("content_type"),
                            ),
                        )
                    )
                elif "file_b64" in file_dict:
                    b64 = file_dict["file_b64"]
                    field_name = f"files[{idx}]"
                    files_data.append(
                        (
                            field_name,
                            (
                                file_dict.get("filename"),
                                b64,
                                file_dict.get("content_type"),
                            ),
                        )
                    )

        return files_data

    def create(
        self, data: dict, files: List[io.BufferedReader] = []
    ) -> NormalizedResponse:
        """Post a Bundle to the BlueInk application.

        Args:
            data: raw data for Bundle, expressed as a python dict
            files: list of file-like objects

        Returns:
            NormalizedResponse object
        """
        if not data:
            raise ValueError("data is required")

        url = self.build_url(endpoints.BUNDLES.CREATE)

        if not files:
            response = self._requests.post(url, json=data)
        else:
            files_data = self._prepare_files(files)
            if not files_data:
                raise ValueError("No valid file data provided")

            bundle_request_data = {"bundle_request": json.dumps(data)}

            response = self._requests.post(
                url, data=bundle_request_data, files=files_data
            )

        return response

    def create_from_bundle_helper(self, bdl_helper: BundleHelper) -> NormalizedResponse:
        """Post a Bundle to the BlueInk application.

        Provided as a convenience to simplify posting of a Bundle. This is the
        recommended way to create a Bundle.

        Args:
            bdl_helper: BundleHelper that has been configured as desired.

        Returns:
            NormalizedResponse object

        """
        data = bdl_helper.as_data()
        files = bdl_helper.files
        return self.create(data=data, files=files)

    def paged_list(
        self,
        page: int = 1,
        per_page: int = 50,
        related_data: bool = False,
        **query_params,
    ) -> PaginatedIterator:
        """Returns an iterable object such that you may lazily fetch a number of
        Bundles

        Typical Usage:
            for page in client.bundles.paged_list():
                page.body -> munch of json

        Args:
            page: what page to start iterator at
            per_page: max number of bundles per page
            related_data: toggles whether or not to provide metadata along with
            bundles (events, files, data)

        Returns:
            PaginatedIterator object, compliant with python iterables
        """
        iterator = PaginatedIterator(
            paged_api_function=self.list,
            page=page,
            per_page=per_page,
            related_data=related_data,
            **query_params,
        )
        return iterator

    def list(
        self,
        page: int = None,
        per_page: int = None,
        related_data: bool = False,
        **query_params,
    ) -> NormalizedResponse:
        """Returns a list of bundles

        Args:
            page: which page to fetch
            per_page: how many bundles to fetch
            related_data: (default false), returns events, files, data if true
            query_params: Additional query params to be put onto the request

        Returns:
            NormalizedResponse object
        """
        url = self.build_url(endpoints.BUNDLES.LIST)
        response = self._requests.get(
            url, params=self.build_params(page, per_page, **query_params)
        )

        if related_data:
            for bundle in response.data:
                self._attach_additional_data(bundle)

        return response

    def _attach_additional_data(self, bundle):
        if type(bundle) == Munch and bundle.id is not None:
            bundle_id = bundle.id

            events_response = self.list_events(bundle_id)
            if events_response.status == 200:
                bundle.events = events_response.data

            if bundle.status == BUNDLE_STATUS.COMPLETE:
                files_response = self.list_files(bundle_id)
                bundle.files = files_response.data

                data_response = self.list_data(bundle_id)
                bundle.data = data_response.data

    def retrieve(
        self, bundle_id: str, related_data: bool = False
    ) -> NormalizedResponse:
        """Request a single bundle

        Args:
            bundle_id: bundle slug
            related_data: (default false), returns events, files, data if true

        Returns:
            NormalizedResponse object
        """
        url = self.build_url(endpoints.BUNDLES.RETRIEVE, bundle_id=bundle_id)
        response = self._requests.get(url)

        if related_data:
            bundle = response.data
            self._attach_additional_data(bundle)

        return response

    def cancel(self, bundle_id: str) -> NormalizedResponse:
        """Cancel a bundle given bundle slug

        Args:
            bundle_id: denotes which bundle to cancel

        Returns:
            NormalizedResponse object

        """
        url = self.build_url(endpoints.BUNDLES.CANCEL, bundle_id=bundle_id)
        return self._request.put(url)

    def list_events(self, bundle_id: str) -> NormalizedResponse:
        """Return a list of events for the supplied bundle corresponding to the id

        Args:
            bundle_id: which bundle to return events for

        Returns:
            NormalizedResponse object
        """
        url = self.build_url(endpoints.BUNDLES.LIST_EVENTS, bundle_id=bundle_id)
        return self._requests.get(url)

    def list_files(self, bundle_id: str) -> NormalizedResponse:
        """Return a list of files for the supplied bundle corresponding to the id

        Args:
            bundle_id: which bundle to return files for

        Returns:
            NormalizedResponse object
        """
        url = self.build_url(endpoints.BUNDLES.LIST_FILES, bundle_id=bundle_id)
        return self._requests.get(url)

    def list_data(self, bundle_id: str) -> NormalizedResponse:
        """Return a data for the supplied bundle corresponding to the id

        Args:
            bundle_id: which bundle to return data for

        Returns:
            NormalizedResponse object
        """
        url = self.build_url(endpoints.BUNDLES.LIST_DATA, bundle_id=bundle_id)
        return self._requests.get(url)
