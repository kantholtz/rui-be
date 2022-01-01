from dataclasses import dataclass
from typing import Optional

from marshmallow import fields, post_load

from rui_be.models.camel_case_schema import CamelCaseSchema
from rui_be.models.entity.post_node_entity import PostNodeEntitySchema, PostNodeEntity


@dataclass
class PostNode:
    pid: Optional[int]

    entities: list[PostNodeEntity]


class PostNodeSchema(CamelCaseSchema):
    pid = fields.Integer(required=True, allow_none=True)

    entities = fields.List(fields.Nested(PostNodeEntitySchema), required=True)

    @post_load
    def make_obj(self, data, **kwargs) -> PostNode:
        return PostNode(**data)

    class Meta:
        ordered = True
