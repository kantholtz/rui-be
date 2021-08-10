from dataclasses import dataclass
from typing import Iterator

import yaml
from draug.homag.graph import RELATIONS, Graph
from draug.homag.text import Match, Matches
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
matches = Matches()


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


@app.route('/api/1.2.0/upload', methods=['PUT'])
def put_data() -> str:
    global graph, matches

    meta_yml: FileStorage = request.files['metaYml']
    nodes_txt: FileStorage = request.files['nodesTxt']
    edges_txt: FileStorage = request.files['edgesTxt']
    match_txt: FileStorage = request.files['matchTxt']

    meta = yaml.load(meta_yml.stream, Loader=yaml.FullLoader)
    nodes = parse_nodes_txt(nodes_txt)
    edges = parse_edges_txt(edges_txt)

    graph = Graph.load_from_memory(meta, nodes, edges)

    matches = parse_match_txt(match_txt)
    matches = Matches.from_matches(matches)

    return ''


def parse_nodes_txt(nodes_txt: FileStorage) -> Iterator[tuple[int, dict]]:
    """
    Parse Nodes TXT whose lines have the following format:

    node {data} ...
    """

    def parse_line(line: str) -> tuple[int, dict]:
        chunks = line.split(' ', maxsplit=1)

        node_id = int(chunks[0])
        data = eval(chunks[1])

        return node_id, data

    return (parse_line(str(line)) for line in nodes_txt.stream)


def parse_edges_txt(edges_txt: FileStorage) -> Iterator[tuple[int, int, int]]:
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

    return (parse_line(str(line)) for line in edges_txt.stream)


def parse_match_txt(match_txt: FileStorage) -> Iterator[Match]:
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

    return (parse_line(str(line)) for line in match_txt.stream)


@app.route('/api/1.2.0/taxonomy', methods=['GET'])
def get_taxonomy() -> dict[str, list[DeepEntity]]:
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


@app.route('/api/1.2.0/entity', methods=['POST'])
def post_entity() -> tuple[str, int]:
    request_data: dict = request.get_json()

    entity = Entity(id=request_data['id'],
                    parent=request_data['parent'],
                    names=request_data['names'])

    graph.add_ent(entity.parent, entity.names)

    return '', 201


@app.route('/api/1.2.0/entity', methods=['PUT'])
def put_entity() -> str:
    request_data: dict = request.get_json()

    entity = Entity(id=request_data['id'],
                    parent=request_data['parent'],
                    names=request_data['names'])

    graph.update_ent(entity.id, entity.parent, entity.names)

    return ''


@app.route('/api/1.2.0/entity/<int:entity_id>', methods=['DELETE'])
def delete_entity(entity_id: int) -> str:
    graph.delete_ent(entity_id)

    return ''


#
# Run server
#

if __name__ == '__main__':
    app.run()
