from dataclasses import dataclass

from rui_be.models.prediction.partial_prediction_item import PartialPredictionItem


@dataclass
class PartialPrediction:
    candidate: str
    dismissed: bool

    total_score: float
    total_score_norm: float

    parent_predictions: list[PartialPredictionItem]
    synonym_predictions: list[PartialPredictionItem]
