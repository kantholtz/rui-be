from dataclasses import dataclass
from typing import Optional

from marshmallow import fields, post_load

from rui_be.models.camel_case_schema import CamelCaseSchema
from rui_be.models.entity.entity import EntitySchema, Entity


@dataclass
class Node:

    nid: int  # node id
    pid: Optional[int]  # parent id

    entities: list[Entity]


class NodeSchema(CamelCaseSchema):

    nid = fields.Integer(required=True)
    pid = fields.Integer(required=True, allow_none=True)

    entities = fields.List(fields.Nested(EntitySchema), required=True)

    @post_load
    def make_obj(self, data, **kwargs) -> Node:
        return Node(**data)

    class Meta:
        ordered = True
