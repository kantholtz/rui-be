"""
From https://marshmallow.readthedocs.io/en/latest/examples.html
"""

from marshmallow import Schema
from marshmallow.fields import Field


class CamelCaseSchema(Schema):
    """
    Schema that uses camelCase for its external representation
    and snake_case for its internal representation
    """

    def on_bind_field(self, field_name: str, field_obj: Field):
        field_obj.data_key = camelcase(field_obj.data_key or field_name)


def camelcase(s):
    parts = iter(s.split('_'))

    return next(parts) + ''.join(i.title() for i in parts)
