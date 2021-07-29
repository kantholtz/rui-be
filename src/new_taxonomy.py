from typing import List, Tuple, Dict

import networkx as nx

graph = nx.MultiGraph()


def add_nodes(id_data_tuples: List[Tuple[int, Dict]]) -> None:
    graph.add_nodes_from(id_data_tuples)
