from dataclasses import dataclass

from marshmallow import fields, post_load

from src.models.camel_case_schema import CamelCaseSchema


@dataclass
class PostEntity:
    node_id: int

    name: str


class PostEntitySchema(CamelCaseSchema):
    node_id = fields.Integer(required=True)

    name = fields.String(required=True)

    @post_load
    def make_obj(self, data, **kwargs) -> PostEntity:
        return PostEntity(**data)

    class Meta:
        ordered = True
