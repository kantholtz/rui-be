from dataclasses import dataclass
from typing import Optional

from marshmallow import fields, post_load

from src.models.camel_case_schema import CamelCaseSchema
from src.models.entity.post_node_entity import PostNodeEntitySchema, PostNodeEntity


@dataclass
class PostNode:
    parent_id: Optional[int]

    entities: list[PostNodeEntity]


class PostNodeSchema(CamelCaseSchema):
    parent_id = fields.Integer(required=True, allow_none=True)

    entities = fields.List(fields.Nested(PostNodeEntitySchema), required=True)

    @post_load
    def make_obj(self, data, **kwargs) -> PostNode:
        return PostNode(**data)

    class Meta:
        ordered = True
