from dataclasses import dataclass

from marshmallow import fields, post_load

from rui_be.models.camel_case_schema import CamelCaseSchema
from rui_be.models.prediction.prediction_item import (
    PredictionItem,
    PredictionItemSchema,
)


@dataclass
class Prediction:
    candidate: str
    dismissed: bool

    total_score: float
    total_score_norm: float

    parent_predictions: list[PredictionItem]
    synonym_predictions: list[PredictionItem]


class PredictionSchema(CamelCaseSchema):
    candidate = fields.String(required=True)
    dismissed = fields.Boolean(required=True)

    total_score = fields.Float(required=True)
    total_score_norm = fields.Float(required=True)

    parent_predictions = fields.List(fields.Nested(PredictionItemSchema), required=True)
    synonym_predictions = fields.List(
        fields.Nested(PredictionItemSchema), required=True
    )

    @post_load
    def make_obj(self, data, **kwargs) -> Prediction:
        return Prediction(**data)

    class Meta:
        ordered = True
