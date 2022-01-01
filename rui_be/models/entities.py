from dataclasses import dataclass

from marshmallow import fields, post_load

from rui_be.models.camel_case_schema import CamelCaseSchema


@dataclass
class Entity:

    # --

    class Schema(CamelCaseSchema):

        eid = fields.Integer(required=True)
        nid = fields.Integer(required=True)

        name = fields.String(required=True)
        matches_count = fields.Integer(required=True)

        @post_load
        def make_obj(self, data, **kwargs) -> "Entity":
            return Entity(**data)

        class Meta:
            ordered = True

    eid: int
    nid: int

    name: str
    matches_count: int


@dataclass
class PostEntity:

    # --

    class Schema(CamelCaseSchema):
        nid = fields.Integer(required=True)

        name = fields.String(required=True)

        @post_load
        def make_obj(self, data, **kwargs) -> "PostEntity":
            return PostEntity(**data)

        class Meta:
            ordered = True

    nid: int
    name: str


@dataclass
class PostNodeEntity:
    class Schema(CamelCaseSchema):
        name = fields.String(required=True)

        @post_load
        def make_obj(self, data, **kwargs) -> "PostNodeEntity":
            return PostNodeEntity(**data)

        class Meta:
            ordered = True

    name: str
