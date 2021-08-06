from dataclasses import dataclass
from typing import Dict, Tuple, List

import yaml
from draug.homag.graph import RELATIONS, Graph
from flask import Flask, request
from flask_cors import CORS
from werkzeug.datastructures import FileStorage

#
# Set up app object
#

app = Flask(__name__)

CORS(app)

app.config['JSON_SORT_KEYS'] = False  # Simplify debugging in frontend

#
# Create initial taxonomy
#

meta = {
    'name': 'symptax.v5',
    'reflexive': (RELATIONS['synonym'],),
    'relmap': {rid: name for name, rid in RELATIONS.items()}
}

graph = Graph(meta)


#
# Set up routes
#

@app.route('/')
def get_root():
    return 'Server is up'


@dataclass
class Entity:
    id: int
    parent: int
    names: List[str]


@dataclass
class DeepEntity:
    id: int
    parent: int
    names: List[str]
    children: List


@app.route('/api/1.1.0/taxonomy', methods=['GET'])
def get_taxonomy() -> Dict[str, List[DeepEntity]]:
    root_entity_ids = graph.find_root_ents()

    #
    # Build and return list of recusively populated entities
    #

    def id_to_entity(entity_id: int) -> DeepEntity:
        return DeepEntity(id=entity_id,
                           parent=graph.get_parent(entity_id),
                           names=graph.nxg.nodes[entity_id]['names'],
                           children=[id_to_entity(child) for child in graph.get_children(entity_id)])

    return {'taxonomy': [id_to_entity(root_node) for root_node in root_entity_ids]}


@app.route('/api/1.1.0/taxonomy', methods=['PUT'])
def put_taxonomy() -> str:
    global graph

    meta_yml: FileStorage = request.files['metaYml']
    nodes_txt: FileStorage = request.files['nodesTxt']
    edges_txt: FileStorage = request.files['edgesTxt']

    meta_dict = yaml.load(meta_yml.stream, Loader=yaml.FullLoader)

    str_nodes = (line.split(b' ', maxsplit=1) for line in nodes_txt.stream)
    nodes = ((int(node_id), eval(data)) for node_id, data in str_nodes)

    str_triples = (line.split() for line in edges_txt.stream)
    triples = ((int(str_triple[0]), int(str_triple[1]), int(str_triple[2])) for str_triple in str_triples)

    graph = Graph.load_from_streams(meta_dict, nodes, triples)

    return ''


@app.route('/api/1.1.0/entity', methods=['POST'])
def post_entity() -> Tuple[str, int]:
    request_data: Dict = request.get_json()

    entity = Entity(id=request_data['id'],
                      parent=request_data['parent'],
                      names=request_data['names'])

    graph.add_ent(entity.parent, entity.names)

    return '', 201


@app.route('/api/1.1.0/entity', methods=['PUT'])
def put_entity() -> str:
    request_data: Dict = request.get_json()

    entity = Entity(id=request_data['id'],
                      parent=request_data['parent'],
                      names=request_data['names'])

    graph.update_ent(entity.id, entity.parent, entity.names)

    return ''


@app.route('/api/1.1.0/entity/<int:entity_id>', methods=['DELETE'])
def delete_entity(entity_id: int) -> str:
    graph.delete_ent(entity_id)

    return ''


#
# Run server
#

if __name__ == '__main__':
    app.run()
