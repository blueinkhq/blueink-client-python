from typing import List

from blueink.model.persons import ContactChannelSchema, PersonSchema


class PersonHelper:
    def __init__(
        self,
        name: str = None,
        metadata: dict = {},
        phones: List[str] = [],
        emails: List[str] = [],
    ):
        """Helper class to aid building a Person.

        Once Person is ready, use as_dict() to compile python dictionary for the Person.
        Args:
            name:
            metadata:
            phones:
            emails:
        """
        self._name = name
        self._metadata = metadata
        self._phones = phones
        self._emails = emails

    def add_phone(self, phone: str) -> List[str]:
        """
        Add a phone number to the current list of phone numbers

        Args:
            phone: The phone number being added to the list

        Returns:
            A copy of all of the phone numbers currently in the list
        """
        self._phones.append(phone)
        return self._phones

    def set_phones(self, phones: List[str]) -> List[str]:
        """
        Replace the current list of phone numbers with this list

        Args:
            phones: The phone numbers replacing the existing list of numbers

        Returns:
            A copy of all of the phone numbers currently in the list
        """
        self._phones = phones
        return self._phones

    def get_phones(self) -> List[str]:
        """
        Returns all of the phone numbers currently stored

        Returns:
            A copy of all of the phone numbers currently in the list
        """
        return self._phones

    def add_email(self, email: str) -> List[str]:
        """
        Add an email to the current list of emails

        Args:
            email: The email being add to the existing list
        Returns:
            A copy of all of the emails currently in the list
        """
        self._emails.append(email)
        return self._emails

    def set_emails(self, emails: List[str]) -> List[str]:
        """
        Replace the current list of emails with this list

        Args:
            phones: The emails replacing the existing list of emails

        Returns:
            A copy of all of the emails currently in the list
        """
        self._emails = emails
        return self._emails

    def get_emails(self) -> List[str]:
        """
        Returns all of the emails currently stored

        Returns:
            A copy of all of the emails currently in the list
        """
        return self._emails

    def set_metadata(self, metadata: dict) -> dict:
        """
        Replace the existing metadata dict with this dict

        Args:
            metadata: The new metadata for the person

        Returns:
            A copy of the current metadata
        """
        self._metadata = metadata
        return self._metadata

    def set_name(self, name: str) -> str:
        """
        Set the name for the person

        Args:
            name: The new name for the person

        Returns:
            The current name of the person
        """
        self._name = name
        return self._name

    def as_dict(self, **kwargs):
        """
        Return a person as a dictionary

        Returns:
            Returns a person as a dictionary
        """
        channels = []

        for email in self._emails:
            channels.append(ContactChannelSchema(email=email, kind="em"))
        for phone in self._phones:
            channels.append(ContactChannelSchema(phone=phone, kind="mp"))

        person_out = PersonSchema(
            name=self._name,
            metadata=self._metadata,
            channels=channels,
        )
        out_dict = person_out.dict(
            exclude_unset=True,
        )

        # Merge in the additional data
        out_dict = {**out_dict, **kwargs}

        return out_dict
