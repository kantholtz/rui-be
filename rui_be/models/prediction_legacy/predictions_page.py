from dataclasses import dataclass

from marshmallow import fields, post_load

from rui_be.models.camel_case_schema import CamelCaseSchema
from rui_be.models.prediction.prediction import PredictionSchema, Prediction


@dataclass
class PredictionsPage:
    total_predictions: int
    total_synonym_predictions: int
    total_child_predictions: int
    predictions: list[Prediction]


class PredictionsPageSchema(CamelCaseSchema):
    total_predictions = fields.Integer(required=True)
    total_synonym_predictions = fields.Integer(required=True)
    total_child_predictions = fields.Integer(required=True)
    predictions = fields.List(fields.Nested(PredictionSchema), required=True)

    @post_load
    def make_obj(self, data, **kwargs) -> PredictionsPage:
        return PredictionsPage(**data)

    class Meta:
        ordered = True
