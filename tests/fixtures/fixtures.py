from rui_be.models.entity.entity import Entity
from rui_be.models.match.match import Match
from rui_be.models.node.deep_node import DeepNode

### Node A

entity_aa1 = Entity(id=1, node_id=1, name='Aa-1', matches_count=2)
deep_node_aa = DeepNode(id=1, parent_id=0, entities=[entity_aa1], children=[])

entity_ab1 = Entity(id=2, node_id=2, name='Ab-1', matches_count=2)
deep_node_ab = DeepNode(id=2, parent_id=0, entities=[entity_ab1], children=[])

entity_a1 = Entity(id=0, node_id=0, name='A-1', matches_count=2)
deep_node_a = DeepNode(id=0, parent_id=None, entities=[entity_a1], children=[deep_node_aa, deep_node_ab])

### Node B

entity_ba1 = Entity(id=4, node_id=4, name='Ba-1', matches_count=1)
entity_ba2 = Entity(id=5, node_id=4, name='Ba-2', matches_count=1)
entity_ba3 = Entity(id=6, node_id=4, name='Ba-3', matches_count=0)
entity_ba4 = Entity(id=7, node_id=4, name='Ba-4', matches_count=1)
entity_ba5 = Entity(id=8, node_id=4, name='Ba-5', matches_count=1)
deep_node_ba = DeepNode(id=4,
                        parent_id=3,
                        entities=[entity_ba1, entity_ba2, entity_ba3, entity_ba4, entity_ba5],
                        children=[])

entity_bb1 = Entity(id=9, node_id=5, name='Bb-1', matches_count=1)
entity_bb2 = Entity(id=10, node_id=5, name='Bb-2', matches_count=1)
deep_node_bb = DeepNode(id=5, parent_id=3, entities=[entity_bb1, entity_bb2], children=[])

entity_b1 = Entity(id=3, node_id=3, name='B-1', matches_count=1)
deep_node_b = DeepNode(id=3, parent_id=None, entities=[entity_b1], children=[deep_node_ba, deep_node_bb])

### Node C

entity_c1 = Entity(id=11, node_id=6, name='C-1', matches_count=1)
deep_node_c = DeepNode(id=6, parent_id=None, entities=[entity_c1], children=[])

### New Node & New Entity

next_node_id = 7
next_entity_id = 12

### Matches

match_a11 = Match(entity_id=entity_a1.id,
                  ticket=1000,
                  context='Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt '
                          'ut labore et dolore magna aliqua .',
                  mention='dolor',
                  mention_indexes=[2, 3])

match_a12 = Match(entity_id=entity_a1.id,
                  ticket=1011,
                  context='Viverra tellus in hac habitasse platea dictumst .',
                  mention='habitasse platea',
                  mention_indexes=[4, 6])
