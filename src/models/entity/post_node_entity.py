from dataclasses import dataclass

from marshmallow import fields, post_load

from src.models.camel_case_schema import CamelCaseSchema


@dataclass
class PostNodeEntity:
    name: str


class PostNodeEntitySchema(CamelCaseSchema):
    name = fields.String(required=True)

    @post_load
    def make_obj(self, data, **kwargs) -> PostNodeEntity:
        return PostNodeEntity(**data)

    class Meta:
        ordered = True
