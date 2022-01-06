# -*- coding: utf-8 -*-

from dataclasses import dataclass

from marshmallow import fields, post_load

from rui_be.models.nodes import Node
from rui_be.models.camel_case_schema import CamelCaseSchema

from draug.homag.graph import NID
from draug.homag.model import PID
from draug.homag import model as draug


@dataclass
class Prediction:

    # --
    class Schema(CamelCaseSchema):

        pid = fields.Integer(required=True)

        score = fields.Float(required=True)
        score_norm = fields.Float(required=True)

        context = fields.String(required=True)
        node = fields.Nested(Node.Schema, required=True)

        @post_load
        def make_obj(self, data, **kwargs) -> "Prediction":
            return Prediction(**data)

    # --

    pid: PID

    score: float
    score_norm: float

    context: str
    node: Node

    @classmethod
    def from_draug(Self, pred: draug.Prediction, node: Node):
        return Self(
            pid=pred.pid,
            score_norm=pred.score_norm,
            score=pred.score,
            context=pred.context,
            node=node,
        )


@dataclass
class Predictions:

    # --

    class Schema(CamelCaseSchema):

        total_synonyms = fields.Integer(required=True)
        total_children = fields.Integer(required=True)

        synonyms = fields.List(fields.Nested(Prediction.Schema), required=True)
        children = fields.List(fields.Nested(Prediction.Schema), required=True)

        @post_load
        def make_obj(self, data, **kwargs) -> "Predictions":
            return Predictions(**data)

        class Meta:
            ordered = True

    total_synonyms: int
    total_children: int

    synonyms: list[Prediction]
    children: list[Prediction]


@dataclass
class Annotation:

    # --

    class Schema(CamelCaseSchema):

        nid = fields.Integer(required=True)
        relation = fields.String(required=True)
        phrase = fields.String(required=True)

        predicted_nid = fields.Integer(required=True)
        predicted_relation = fields.String(required=True)

        specific = fields.Boolean(required=True)

        @post_load
        def make_obj(self, data, **kwargs) -> "Annotation":
            return Annotation(**data)

    nid: int
    relation: str
    phrase: str

    predicted_nid: int
    predicted_relation: str

    specific: bool


@dataclass
class FilterRequest:

    # --

    class Schema(CamelCaseSchema):

        nid = fields.Integer(required=True)
        relation = fields.String(required=True)
        phrase = fields.String(required=True)

        @post_load
        def make_obj(self, data, **kwargs) -> "FilterRequest":
            return FilterRequest(**data)

    nid: NID
    relation: str
    phrase: str
