from dataclasses import dataclass

from marshmallow import fields, post_load

from rui_be.models.camel_case_schema import CamelCaseSchema
from rui_be.models.node.node import Node, NodeSchema


@dataclass
class CandidatePrediction:
    score: float
    score_norm: float
    node: Node


class CandidatePredictionSchema(CamelCaseSchema):
    score = fields.Float(required=True)
    score_norm = fields.Float(require=True)
    node = fields.Nested(NodeSchema, required=True)

    @post_load
    def make_obj(self, data, **kwargs) -> CandidatePrediction:
        return CandidatePrediction(**data)

    class Meta:
        ordered = True
