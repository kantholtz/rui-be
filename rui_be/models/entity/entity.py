from dataclasses import dataclass

from marshmallow import fields, post_load

from rui_be.models.camel_case_schema import CamelCaseSchema


@dataclass
class Entity:
    id: int

    node_id: int

    name: str
    matches_count: int


class EntitySchema(CamelCaseSchema):
    id = fields.Integer(required=True)

    node_id = fields.Integer(required=True)

    name = fields.String(required=True)
    matches_count = fields.Integer(required=True)

    @post_load
    def make_obj(self, data, **kwargs) -> Entity:
        return Entity(**data)

    class Meta:
        ordered = True
