from dataclasses import dataclass

from marshmallow import fields, post_load

from src.models.camel_case_schema import CamelCaseSchema
from src.models.prediction.candidate_prediction import CandidatePrediction, CandidatePredictionSchema


@dataclass
class CandidateWithPredictions:
    candidate: str

    parent_predictions: list[CandidatePrediction]
    synonym_predictions: list[CandidatePrediction]


class CandidateWithPredictionsSchema(CamelCaseSchema):
    candidate = fields.String(required=True)

    parent_predictions = fields.List(fields.Nested(CandidatePredictionSchema), required=True)
    synonym_predictions = fields.List(fields.Nested(CandidatePredictionSchema), required=True)

    @post_load
    def make_obj(self, data, **kwargs) -> CandidateWithPredictions:
        return CandidateWithPredictions(**data)

    class Meta:
        ordered = True
