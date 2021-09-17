from dataclasses import dataclass
from typing import Optional

from marshmallow import fields, post_load

from rui_be.models.camel_case_schema import CamelCaseSchema
from rui_be.models.entity.entity import EntitySchema, Entity


@dataclass
class DeepNode:
    id: int

    parent_id: Optional[int]

    entities: list[Entity]
    children: list  # list[DeepNode]


class DeepNodeSchema(CamelCaseSchema):
    id = fields.Integer(required=True)

    parent_id = fields.Integer(required=True, allow_none=True)

    entities = fields.List(fields.Nested(EntitySchema), required=True)
    children = fields.List(fields.Nested(lambda: DeepNodeSchema()), required=True)

    @post_load
    def make_obj(self, data, **kwargs) -> DeepNode:
        return DeepNode(**data)

    class Meta:
        ordered = True
