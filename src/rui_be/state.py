from draug.homag.graph import Graph
from draug.homag.model import Predictions
from draug.homag.text import Matches

meta = {
    'name': 'symptax.v6',
    'reflexive': [Graph.RELATIONS.synonym.value],
    'relmap': {m.value: m.name for m in Graph.RELATIONS}
}

graph = Graph(meta)

matches_store = Matches(graph)
predictions_store = Predictions()
