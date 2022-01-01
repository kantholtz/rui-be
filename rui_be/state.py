import logging

from draug.homag.graph import Graph
from draug.homag.model import Predictions
from draug.homag.text import Matches

graph = Graph(meta=dict(name="unknown"))
matches_store = Matches(graph)
predictions_store = Predictions()
