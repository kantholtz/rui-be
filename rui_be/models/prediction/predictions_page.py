from dataclasses import dataclass

from marshmallow import fields, post_load

from rui_be.models.camel_case_schema import CamelCaseSchema
from rui_be.models.prediction.candidate_with_predictions import CandidateWithPredictionsSchema, CandidateWithPredictions


@dataclass
class PredictionsPage:
    total_predictions: int
    predictions: list[CandidateWithPredictions]


class PredictionsPageSchema(CamelCaseSchema):
    total_predictions = fields.Integer(required=True)
    predictions = fields.List(fields.Nested(CandidateWithPredictionsSchema), required=True)

    @post_load
    def make_obj(self, data, **kwargs) -> PredictionsPage:
        return PredictionsPage(**data)

    class Meta:
        ordered = True
