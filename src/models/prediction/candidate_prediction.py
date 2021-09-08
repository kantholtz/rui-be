from dataclasses import dataclass

from marshmallow import fields, post_load

from src.models.camel_case_schema import CamelCaseSchema
from src.models.prediction.prediction import Prediction, PredictionSchema


@dataclass
class CandidatePrediction:
    candidate: str

    parent_predictions: list[Prediction]
    synonym_predictions: list[Prediction]


class CandidatePredictionSchema(CamelCaseSchema):
    candidate = fields.String(required=True)

    parent_predictions = fields.List(fields.Nested(PredictionSchema), required=True)
    synonym_predictions = fields.List(fields.Nested(PredictionSchema), required=True)

    @post_load
    def make_obj(self, data, **kwargs) -> CandidatePrediction:
        return CandidatePrediction(**data)

    class Meta:
        ordered = True
