from dataclasses import dataclass

from marshmallow import fields, post_load

from src.models.camel_case_schema import CamelCaseSchema
from src.models.entity.entity import EntitySchema, Entity


@dataclass
class Node:
    id: int

    parent_id: int

    entities: list[Entity]


class NodeSchema(CamelCaseSchema):
    id = fields.Integer(required=True)

    parent_id = fields.Integer(required=True)

    entities = fields.List(fields.Nested(EntitySchema), required=True)

    @post_load
    def make_obj(self, data, **kwargs) -> Node:
        return Node(**data)

    class Meta:
        ordered = True
