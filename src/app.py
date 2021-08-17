import os
import zipfile
from dataclasses import dataclass

import yaml
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
class Entity:
    id: int
    parent: int
    names: list[str]


@dataclass
class DeepEntity:
    id: int
    parent: int
    names: list[str]
    children: list


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

    meta_yml: str = os.path.join(extracted_dir, 'meta.yml')
    nodes_txt: str = os.path.join(extracted_dir, 'nodes.txt')
    edges_txt: str = os.path.join(extracted_dir, 'edges.txt')
    match_txt: str = os.path.join(extracted_dir, 'match.txt')

    with open(meta_yml) as f:
        meta = yaml.load(f, Loader=yaml.FullLoader)

    nodes = parse_nodes_txt(nodes_txt)
    edges = parse_edges_txt(edges_txt)
    matches = parse_match_txt(match_txt)

    graph = Graph.load_from_memory(meta, nodes, edges)
    matches_store = Matches.from_matches(matches)

    return ''


def parse_nodes_txt(nodes_txt: str) -> list[tuple[int, dict]]:
    """
    Parse Nodes TXT whose lines have the following format:

    node {data} ...
    """

    def parse_line(line: str) -> tuple[int, dict]:
        chunks = line.split(' ', maxsplit=1)

        node_id = int(chunks[0])
        data = eval(chunks[1])

        return node_id, data

    with open(nodes_txt, encoding='utf-8') as f:
        nodes = [parse_line(line) for line in f.readlines()]

    return nodes


def parse_edges_txt(edges_txt: str) -> list[tuple[int, int, int]]:
    """
    Parse Edges TXT whose lines have the following format:

    head tail rel
    """

    def parse_line(line: str) -> tuple[int, int, int]:
        chunks = line.split(' ')

        head = int(chunks[0])
        tail = int(chunks[1])
        rel = int(chunks[2])

        return head, tail, rel

    with open(edges_txt, encoding='utf-8') as f:
        edges = [parse_line(line) for line in f.readlines()]

    return edges


def parse_match_txt(match_txt: str) -> list[Match]:
    """
    Parse Nodes TXT whose lines have the following format:

    entity_label|mention|ticket.phrase_id|phrase_text
    """

    def parse_line(line: str) -> Match:
        chunks = line.split('|')

        entity = str(chunks[0])
        mention = str(chunks[1])

        ticket_chunk, phrase_id_chunk = chunks[2].split('.')
        ticket = int(ticket_chunk)
        phrase_id = int(phrase_id_chunk)

        phrase_text = str(chunks[3])

        return Match(entity, mention, ticket, phrase_id, phrase_text)

    with open(match_txt, encoding='utf-8') as f:
        matches = [parse_line(line) for line in f.readlines()]

    return matches


@app.route('/api/1.3.0/entities', methods=['GET'])
def get_entities() -> dict[str, list[DeepEntity]]:
    root_entity_ids = graph.find_root_ents()

    #
    # Build and return list of recusively populated entities
    #

    def id_to_entity(entity_id: int) -> DeepEntity:
        return DeepEntity(id=entity_id,
                          parent=graph.get_parent(entity_id),
                          names=graph.nxg.nodes[entity_id]['names'],
                          children=[id_to_entity(child) for child in graph.get_children(entity_id)])

    return {'entities': [id_to_entity(root_node) for root_node in root_entity_ids]}


@app.route('/api/1.3.0/entity', methods=['POST'])
def post_entity() -> tuple[str, int]:
    request_data: dict = request.get_json()

    entity = Entity(id=request_data['id'],
                    parent=request_data['parent'],
                    names=request_data['names'])

    graph.add_ent(entity.parent, entity.names)

    return '', 201


@app.route('/api/1.3.0/entity', methods=['PUT'])
def put_entity() -> str:
    request_data: dict = request.get_json()

    entity = Entity(id=request_data['id'],
                    parent=request_data['parent'],
                    names=request_data['names'])

    graph.update_ent(entity.id, entity.parent, entity.names)

    return ''


@app.route('/api/1.3.0/entity/<int:entity_id>', methods=['DELETE'])
def delete_entity(entity_id: int) -> str:
    graph.delete_ent(entity_id)

    return ''


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
