from dataclasses import dataclass
from typing import Optional

from marshmallow import fields, post_load

from rui_be.models.camel_case_schema import CamelCaseSchema

from rui_be.models.entities import Entity
from rui_be.models.entities import PostNodeEntity


@dataclass
class Node:

    # --

    class Schema(CamelCaseSchema):

        nid = fields.Integer(required=True)
        pid = fields.Integer(required=True, allow_none=True)

        entities = fields.List(fields.Nested(Entity.Schema), required=True)

        @post_load
        def make_obj(self, data, **kwargs) -> "Node":
            return Node(**data)

        class Meta:
            ordered = True

    nid: int  # node id
    pid: Optional[int]  # parent id

    entities: list[Entity]


@dataclass(order=True)  # order=True to faciliate comparing lists in test's diff view
class DeepNode:

    # --

    class Schema(CamelCaseSchema):

        nid = fields.Integer(required=True)
        pid = fields.Integer(required=True, allow_none=True)

        entities = fields.List(fields.Nested(Entity.Schema), required=True)
        children = fields.List(fields.Nested(lambda: DeepNode.Schema()), required=True)

        @post_load
        def make_obj(self, data, **kwargs) -> "DeepNode":
            return DeepNode(**data)

        class Meta:
            ordered = True

    nid: int
    pid: Optional[int]

    entities: list[Entity]
    children: list["DeepNode"]


@dataclass
class NodePatch:

    # --

    class Schema(CamelCaseSchema):
        pid = fields.Integer(required=True, allow_none=True)

        @post_load
        def make_obj(self, data, **kwargs) -> "NodePatch":
            return NodePatch(**data)

        class Meta:
            ordered = True

    pid: Optional[int]


@dataclass
class PostNode:

    # --

    class Schema(CamelCaseSchema):

        pid = fields.Integer(required=True, allow_none=True)
        entities = fields.List(fields.Nested(PostNodeEntity.Schema), required=True)

        @post_load
        def make_obj(self, data, **kwargs) -> "PostNode":
            return PostNode(**data)

        class Meta:
            ordered = True

    pid: Optional[int]
    entities: list[PostNodeEntity]
