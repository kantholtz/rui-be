from dataclasses import dataclass
from typing import Optional

from marshmallow import fields, post_load

from rui_be.models.camel_case_schema import CamelCaseSchema


@dataclass
class NodePatch:
    pid: Optional[int]


class NodePatchSchema(CamelCaseSchema):
    pid = fields.Integer(required=True, allow_none=True)

    @post_load
    def make_obj(self, data, **kwargs) -> NodePatch:
        return NodePatch(**data)

    class Meta:
        ordered = True
