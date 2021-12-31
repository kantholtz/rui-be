from dataclasses import dataclass

from marshmallow import fields, post_load

from rui_be.models.camel_case_schema import CamelCaseSchema
from rui_be.models.node.node import Node, NodeSchema


@dataclass
class PredictionItem:
    score: float
    score_norm: float
    node: Node


class PredictionItemSchema(CamelCaseSchema):
    score = fields.Float(required=True)
    score_norm = fields.Float(require=True)
    node = fields.Nested(NodeSchema, required=True)

    @post_load
    def make_obj(self, data, **kwargs) -> PredictionItem:
        return PredictionItem(**data)

    class Meta:
        ordered = True
