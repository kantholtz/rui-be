# -*- coding: utf-8 -*-

from dataclasses import dataclass

from marshmallow import fields, post_load

from rui_be.models.node.node import Node, NodeSchema
from rui_be.models.camel_case_schema import CamelCaseSchema

from draug.homag import model as draug


@dataclass
class Prediction:

    # --
    class Schema(CamelCaseSchema):

        score = fields.Float(required=True)
        score_norm = fields.Float(required=True)

        context = fields.String(required=True)
        node = fields.Nested(NodeSchema, required=True)

        @post_load
        def make_obj(self, data, **kwargs) -> "Prediction":
            return Prediction(**data)

    # --

    score: float
    score_norm: float

    context: str
    node: Node

    # --

    @classmethod
    def from_draug(Self, pred: draug.Prediction, node: Node):
        return Self(
            score_norm=pred.score_norm,
            score=pred.score,
            context=pred.context,
            node=node,
        )


@dataclass
class Predictions:

    # --

    class Schema(CamelCaseSchema):

        total = fields.Integer(required=True)

        synonyms = fields.List(fields.Nested(Prediction.Schema), required=True)
        children = fields.List(fields.Nested(Prediction.Schema), required=True)

        @post_load
        def make_obj(self, data, **kwargs) -> "Predictions":
            return Predictions(**data)

        class Meta:
            ordered = True

    # --

    total_synonyms: int
    total_children: int

    synonyms: list[Prediction]
    children: list[Prediction]
