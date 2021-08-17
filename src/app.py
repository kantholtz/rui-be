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
matches_store = Matches()


#
# Set up routes
#

@app.route('/')
def get_root():
    return 'Server is up'


@dataclass
class Node:
    id: int
    parent: int
    names: list[str]


@dataclass
class DeepNode:
    id: int
    parent: int
    names: list[str]
    children: list


#
# Upload
#

@app.route('/api/1.3.0/upload', methods=['PUT'])
def put_upload() -> str:
    global graph, matches_store

    symptax_core_zip: FileStorage = request.files['symptaxCoreZip']

    upload_filename = secure_filename(symptax_core_zip.filename)
    upload_dir = os.getcwd()
    upload_path = os.path.join(upload_dir, upload_filename)

    symptax_core_zip.save(upload_path)

    with zipfile.ZipFile(os.path.join(upload_dir, upload_filename), 'r') as zip_ref:
        zip_ref.extractall(upload_dir)

    extracted_dir = os.path.splitext(upload_path)[0]

    graph = Graph.load(extracted_dir)

    match_txt: str = os.path.join(extracted_dir, 'match.txt')
    matches = _parse_match_txt(match_txt)
    matches_store = Matches.from_matches(matches)

    return ''


def _parse_match_txt(match_txt: str) -> list[Match]:
    """
    Parse Match TXT whose lines have the following format:

    ticket|node_name|node_id|mention|mention_indexes|context
    """

    def parse_line(line: str) -> Match:
        chunks = line.split('|')

        ticket: int = int(chunks[0])
        node_name: str = chunks[1]
        node_id: int = int(chunks[2])
        mention: str = chunks[3]
        mention_indexes: tuple[int] = tuple(map(int, chunks[4].split()))
        context: str = chunks[5]

        return Match(ticket, node_id, node_name, mention, context, mention_indexes)

    with open(match_txt, encoding='utf-8') as f:
        matches = [parse_line(line) for line in f.readlines()]

    return matches


#
# Nodes
#

@app.route('/api/1.3.0/nodes', methods=['GET'])
def get_nodes() -> dict[str, list[DeepNode]]:
    root_node_ids = graph.find_root_ents()

    #
    # Build and return list of recusively populated nodes
    #

    def deep_node_from_node_id(node_id: int) -> DeepNode:
        return DeepNode(id=node_id,
                        parent=graph.get_parent(node_id),
                        names=graph.nxg.nodes[node_id]['names'],
                        children=[deep_node_from_node_id(child)
                                  for child in graph.get_children(node_id)])

    return {'root_nodes': [deep_node_from_node_id(root_node)
                           for root_node in root_node_ids]}


@app.route('/api/1.3.0/nodes', methods=['POST'])
def post_node() -> tuple[str, int]:
    request_data: dict = request.get_json()

    node = Node(id=request_data['id'],
                parent=request_data['parent'],
                names=request_data['names'])

    graph.add_ent(node.parent, node.names)

    return '', 201


@app.route('/api/1.3.0/nodes', methods=['PUT'])
def put_node() -> str:
    request_data: dict = request.get_json()

    node = Node(id=request_data['id'],
                parent=request_data['parent'],
                names=request_data['names'])

    graph.update_ent(node.id, node.parent, node.names)

    return ''


@app.route('/api/1.3.0/nodes/<int:node_id>', methods=['DELETE'])
def delete_node(node_id: int) -> str:
    graph.delete_ent(node_id)

    return ''


#
# Matches
#

@app.route('/api/1.3.0/matches', methods=['GET'])
def get_matches() -> dict[str, list[Match]]:
    global matches_store

    #
    # Parse query params
    #

    name = request.args.get('name')

    offset = request.args.get('offset')
    if offset:
        offset = int(offset)

    limit = request.args.get('limit')
    if limit:
        limit = int(limit)

    #
    # Get matches from draug and apply pagination
    #

    matches = list(matches_store.get_entity_matches(name))

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
