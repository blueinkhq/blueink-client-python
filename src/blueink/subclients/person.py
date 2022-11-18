from blueink import endpoints
from blueink.paginator import PaginatedIterator
from blueink.person_helper import PersonHelper
from blueink.request_helper import NormalizedResponse
from blueink.subclients.subclient import SubClient


class PersonSubClient(SubClient):
    def create(self, data: dict, **kwargs) -> NormalizedResponse:
        """Create a person (eg. signer) record.

        Args:
            data: A dictionary definition of a person

        Returns:
            NormalizedResponse object
        """
        if "name" not in data or not data["name"]:
            raise ValueError("A name is required to create a Person")

        # Merge the kwargs with the given data
        data = {**data, **kwargs}

        url = self.build_url(endpoints.PERSONS.CREATE)
        return self._requests.post(url, json=data)

    def create_from_person_helper(
        self, person_helper: PersonHelper, **kwargs
    ) -> NormalizedResponse:
        """Create a person using PersonHelper convenience object

        Args:
            person_helper: PersonHelper setup of a person

        Return:
            NormalizedResponse object
        """
        return self.create(person_helper.as_dict(**kwargs))

    def paged_list(
        self, page: int = 1, per_page: int = 50, **query_params
    ) -> PaginatedIterator:
        """Return an iterable object such that you may lazily fetch a number of
        Persons (signers)

        Typical Usage:
            for page in client.persons.paged_list():
                page.body -> munch of json

        Args:
            page: start page (default 1)
            per_page: max # of results per page (default 50)
            query_params: Additional query params to be put onto the request

        Returns:
            PaginatedIterator object
        """

        iterator = PaginatedIterator(
            paged_api_function=self.list, page=page, per_page=per_page, **query_params
        )
        return iterator

    def list(
        self, page: int = None, per_page: int = None, **query_params
    ) -> NormalizedResponse:
        """Return a list of persons (signers).

        Args:
            page:
            per_page:
            query_params: Additional query params to be put onto the request

        Returns:
            NormalizedResponse object
        """
        url = self.build_url(endpoints.PERSONS.LIST)
        return self._requests.get(
            url, params=self.build_params(page, per_page, **query_params)
        )

    def retrieve(self, person_id: str) -> NormalizedResponse:
        """Retrieve details on a singular person

        Args:
            person_id: identifying which signer to retrieve

        Returns:
            NormalizedResponse object
        """
        url = self.build_url(endpoints.PERSONS.RETRIEVE, person_id=person_id)
        return self._requests.get(url)

    def update(
        self, person_id: str, data: dict, partial: bool = False
    ) -> NormalizedResponse:
        """Update a Person (signer)'s record

        Args:
            person_id:
            data: a dictionary representation of person's data
            partial: Whether to do a partial update

        Returns:
            NormalizedResponse object
        """
        url = self.build_url(endpoints.PERSONS.UPDATE, person_id=person_id)
        if partial:
            response = self._requests.patch(url, json=data)
        else:
            response = self._requests.put(url, json=data)
        return response

    def delete(self, person_id: str) -> NormalizedResponse:
        """Delete a person (signer)

        Args:
            person_id:

        Returns:
            NormalizedResponse object
        """
        url = self.build_url(endpoints.PERSONS.DELETE, person_id=person_id)
        return self._requests.delete(url)
