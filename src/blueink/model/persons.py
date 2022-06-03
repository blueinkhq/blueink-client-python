import io
import json
from copy import deepcopy
from marshmallow import Schema, post_dump
from marshmallow import fields as mmf

"""
Developer Note:

Schema classes are for the Marshmallow serializer. 
Validation is being done through these as well.
"""


class ValidationError(RuntimeError):
    def __init__(self, error_text: str):
        super(ValidationError, self).__init__(error_text)


class HiddenEmptyFieldsSchemaMixin:
    @post_dump
    def remove_empties(self, data, many):
        new_data = deepcopy(data)
        for key, value in data.items():
            if value is None:
                new_data.pop(key)

        return new_data


class ContactChannelSchema(Schema, HiddenEmptyFieldsSchemaMixin):
    email = mmf.Email()
    phone = mmf.Str()
    kind = mmf.Str()

    class Meta:
        ordered = True


class PersonSchema(Schema):
    name = mmf.Str()
    metadata = mmf.Dict()
    channels = mmf.List(mmf.Nested(ContactChannelSchema))

    class Meta:
        ordered = True


class ContactChannel:
    KIND_PHONE = "mp"
    KIND_EMAIL = "em"

    def __init__(self, kind: str, email: str = None, phone: str = None):
        self.email = email
        self.phone = phone
        self.kind = kind


class Person:
    def __init__(
        self,
        name: str,
        metadata: dict,
        channels: [ContactChannel],
    ):

        self.name = name
        self.metadata = metadata
        self.channels = channels


class PersonHelper:
    def __init__(
        self,
        name: str = None,
        metadata: dict = None,
        phones: list = [],
        emails: list = [],
    ):
        self._name = name
        self._metadata = metadata
        self._phones = phones
        self._emails = emails

    def add_phone(self, phone: str) -> list:
        self._phones.append(phone)
        return self._phones

    def set_phones(self, phones: list) -> list:
        self._phones = phones
        return self._phones

    def get_phones(self) -> list:
        return self._phones

    def add_email(self, email: str) -> list:
        self._emails.append(email)
        return self._emails

    def set_emails(self, emails: list) -> list:
        self._emails = emails
        return self._emails

    def get_emails(self) -> list:
        return self._emails

    def set_metadata(self, metadata: dict) -> dict:
        self._metadata = metadata
        return self._metadata

    def set_name(self, name: str) -> str:
        self._name = name
        return self._name

    def as_dict(self):

        channels = []

        for email in self._emails:
            channels.append(ContactChannel(email=email, kind=ContactChannel.KIND_EMAIL))
        for phone in self._phones:
            channels.append(ContactChannel(phone=phone, kind=ContactChannel.KIND_PHONE))

        person_out = Person(
            self._name,
            self._metadata,
            channels,
        )

        schema = PersonSchema()

        return schema.dump(person_out)
