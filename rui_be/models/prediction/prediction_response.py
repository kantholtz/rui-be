from dataclasses import dataclass

from marshmallow import fields, post_load

from rui_be.models.camel_case_schema import CamelCaseSchema
from rui_be.models.prediction.candidate_with_predictions import CandidateWithPredictionsSchema, CandidateWithPredictions


@dataclass
class PredictionResponse:
    total_predictions: int
    predictions: list[CandidateWithPredictions]


class PredictionResponseSchema(CamelCaseSchema):
    total_predictions = fields.Integer(required=True)
    predictions = fields.List(fields.Nested(CandidateWithPredictionsSchema), required=True)

    @post_load
    def make_obj(self, data, **kwargs) -> PredictionResponse:
        return PredictionResponse(**data)

    class Meta:
        ordered = True
