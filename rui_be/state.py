# -*- coding: utf-8 -*-

from draug.homag import sampling
from draug.homag.graph import Graph
from draug.homag.model import Predictions
from draug.homag.text import Matches

graph = Graph(meta=dict(name="unknown"))
matches_store = Matches(graph)
predictions_store = Predictions()
nlp = sampling.get_nlp()
