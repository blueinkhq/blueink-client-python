import io
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


class ContactChannelSchema(Schema):
    email = mmf.Email()
    phone = mmf.Int()
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

    def __init__(self, email: str, phone: str, kind: str):
        self.email = email
        self.phone = phone
        self.kind = kind


class ContactChannelEmail(ContactChannel):
    def __init__(self, email: str):
        self.email = email
        self.phone = None
        self.kind = "em"


class ContactChannelPhone(ContactChannel):
    def __init__(self, phone: str):
        self.email = None
        self.phone = phone
        self.kind = "mp"


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
        channels: list = [],
    ):
        self._name = name
        self._metadata = metadata
        self._channels = channels
        self._id = None

    def add_channel(self, channel: ContactChannel):
        self._channels.append(channel)
        return self

    def set_metadata(self, metadata: dict):
        self._metadata = metadata
        return self

    def set_name(self, name: str):
        self._name = name
        return self

    def as_data(self):
        person_out = Person(
            self._name,
            self._metadata,
            self._channels,
        )

        schema = PersonSchema()

        return schema.dumps(person_out)
