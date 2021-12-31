from dataclasses import dataclass


@dataclass
class PartialPredictionItem:
    score: float
    score_norm: float
    node_id: int
