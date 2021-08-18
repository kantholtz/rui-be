import os
import zipfile
from dataclasses import dataclass

from draug.homag.graph import Graph
from draug.homag.text import Match, Matches
from flask import Flask, request
from flask_cors import CORS
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

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
    'name': 'symptax.v6',
    'reflexive': [Graph.RELATIONS.synonym.value],
    'relmap': {m.value: m.name for m in Graph.RELATIONS}
}

graph = Graph(meta)
matches_store = Matches(graph)


#
# Dataclasses
#

@dataclass
class Entity:
    id: int
    node: int
    name: str


@dataclass
class Node:
    id: int
    parent: int
    entities: list[Entity]


@dataclass
class DeepNode:
    id: int
    parent: int
    entities: list[Entity]
    children: list


#
# Root Route
#

@app.route('/')
def get_root():
    return 'Server is up'


#
# Upload
#

@app.route('/api/1.4.0/upload', methods=['PUT'])
def put_upload() -> str:
    global graph, matches_store

    symptax_upload_zip: FileStorage = request.files['symptaxUploadZip']

    upload_filename = secure_filename(symptax_upload_zip.filename)
    upload_dir = os.getcwd()
    upload_path = os.path.join(upload_dir, upload_filename)

    symptax_upload_zip.save(upload_path)

    with zipfile.ZipFile(os.path.join(upload_dir, upload_filename), 'r') as zip_ref:
        zip_ref.extractall(upload_dir)

    extracted_dir = os.path.splitext(upload_path)[0]

    graph = Graph.from_dir(extracted_dir)

    match_txt: str = os.path.join(extracted_dir, 'match.txt')
    matches_store = Matches.from_file(match_txt, graph)

    return ''


#
# Nodes
#

@app.route('/api/1.4.0/nodes', methods=['GET'])
def get_nodes() -> dict[str, list[DeepNode]]:
    root_node_ids = graph.find_root_ents()

    #
    # Build and return list of recusively populated nodes
    #

    def deep_node_from_node_id(node_id: int) -> DeepNode:
        entity_ids = graph.node_eids(node_id)

        return DeepNode(id=node_id,
                        parent=graph.get_parent(node_id),
                        entities=[Entity(entity_id, node_id, graph.entity_name(entity_id))
                                  for entity_id in entity_ids],
                        children=[deep_node_from_node_id(child)
                                  for child in graph.get_children(node_id)])

    return {'root_nodes': [deep_node_from_node_id(root_node_id)
                           for root_node_id in root_node_ids]}


@app.route('/api/1.4.0/nodes', methods=['POST'])
def post_node() -> tuple[str, int]:
    request_data: dict = request.get_json()

    node = Node(id=request_data['id'],
                parent=request_data['parent'],
                entities=[Entity(ent['id'], ent['node'], ent['name'])
                          for ent in request_data['entities']])

    graph.add_node(names=[ent.name for ent in node.entities],
                   parent=node.parent)

    return '', 201


@app.route('/api/1.4.0/nodes/<int:node_id>', methods=['PATCH'])
def patch_node(node_id: int) -> str:
    request_data: dict = request.get_json()

    parent = request_data['parent']

    graph.set_parent(node_id, parent)

    return ''


@app.route('/api/1.4.0/nodes/<int:node_id>', methods=['DELETE'])
def delete_node(node_id: int) -> str:
    graph.delete_node(node_id)

    return ''


#
# Entities
#

@app.route('/api/1.4.0/entities', methods=['POST'])
def post_entity() -> tuple[str, int]:
    request_data: dict = request.get_json()

    entity = Entity(id=request_data['id'],
                    node=request_data['node'],
                    name=request_data['name'])

    graph.add_name(entity.id, entity.name)

    return '', 201


@app.route('/api/1.4.0/entities/<int:entity_id>', methods=['DELETE'])
def delete_entity(entity_id: int) -> str:
    graph.delete_name(entity_id)

    return ''


#
# Matches
#

@app.route('/api/1.4.0/matches', methods=['GET'])
def get_matches() -> dict[str, list[Match]]:
    global matches_store

    #
    # Parse query params
    #

    entity = request.args.get('entity')

    offset = request.args.get('offset')
    if offset:
        offset = int(offset)

    limit = request.args.get('limit')
    if limit:
        limit = int(limit)

    #
    # Get matches from draug and apply pagination
    #

    matches = list(matches_store.by_eid(entity))

    if offset and limit:
        matches = matches[offset:(offset + limit)]
    elif offset:
        matches = matches[offset:]
    elif limit:
        matches = matches[:limit]

    return {'matches': matches}


#
# Run server
#

if __name__ == '__main__':
    app.run()
