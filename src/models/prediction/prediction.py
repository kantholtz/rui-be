from dataclasses import dataclass

from marshmallow import fields, post_load

from src.models.camel_case_schema import CamelCaseSchema
from src.models.node.node import Node, NodeSchema


@dataclass
class Prediction:
    score: float
    node: Node


class PredictionSchema(CamelCaseSchema):
    score = fields.Float(required=True)
    node = fields.Nested(NodeSchema, required=True)

    @post_load
    def make_obj(self, data, **kwargs) -> Prediction:
        return Prediction(**data)

    class Meta:
        ordered = True
