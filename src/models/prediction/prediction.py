from dataclasses import dataclass
from enum import Enum

from marshmallow import fields, post_load
from marshmallow_enum import EnumField

from src.models.camel_case_schema import CamelCaseSchema


class Relation(Enum):
    PARENT = 1
    SYNONYM = 2


@dataclass
class Prediction:
    score: float
    relation: Relation
    candidate: str


class PredictionSchema(CamelCaseSchema):
    score = fields.Float(required=True)
    relation = EnumField(Relation, required=True)
    candidate = fields.String(required=True)

    @post_load
    def make_obj(self, data, **kwargs) -> Prediction:
        return Prediction(**data)

    class Meta:
        ordered = True
