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
