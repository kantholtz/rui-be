from dataclasses import dataclass

from marshmallow import fields, post_load

from rui_be.models.camel_case_schema import CamelCaseSchema
from rui_be.models.prediction.candidate_prediction import CandidatePrediction, CandidatePredictionSchema


@dataclass
class CandidateWithPredictions:
    candidate: str
    dismissed: bool

    total_score: float
    total_score_norm: float

    parent_predictions: list[CandidatePrediction]
    synonym_predictions: list[CandidatePrediction]


class CandidateWithPredictionsSchema(CamelCaseSchema):
    candidate = fields.String(required=True)
    dismissed = fields.Boolean(required=True)

    total_score = fields.Float(required=True)
    total_score_norm = fields.Float(required=True)

    parent_predictions = fields.List(fields.Nested(CandidatePredictionSchema), required=True)
    synonym_predictions = fields.List(fields.Nested(CandidatePredictionSchema), required=True)

    @post_load
    def make_obj(self, data, **kwargs) -> CandidateWithPredictions:
        return CandidateWithPredictions(**data)

    class Meta:
        ordered = True
