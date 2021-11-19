### Node A

entity_aa1 = {'id': 1, 'nodeId': 1, 'name': 'Aa-1', 'matchesCount': 2}
node_aa = {'id': 1, 'parentId': 0, 'entities': [entity_aa1], 'children': []}

entity_ab1 = {'id': 2, 'nodeId': 2, 'name': 'Ab-1', 'matchesCount': 2}
node_ab = {'id': 2, 'parentId': 0, 'entities': [entity_ab1], 'children': []}

entity_a1 = {'id': 0, 'nodeId': 0, 'name': 'A-1', 'matchesCount': 2}
node_a = {'id': 0, 'parentId': None, 'entities': [entity_a1], 'children': [node_aa, node_ab]}

### Node B

entity_ba1 = {'id': 4, 'nodeId': 4, 'name': 'Ba-1', 'matchesCount': 1}
entity_ba2 = {'id': 5, 'nodeId': 4, 'name': 'Ba-2', 'matchesCount': 1}
entity_ba3 = {'id': 6, 'nodeId': 4, 'name': 'Ba-3', 'matchesCount': 0}
entity_ba4 = {'id': 7, 'nodeId': 4, 'name': 'Ba-4', 'matchesCount': 1}
entity_ba5 = {'id': 8, 'nodeId': 4, 'name': 'Ba-5', 'matchesCount': 1}
node_ba = {
    'id': 4,
    'parentId': 3,
    'entities': [entity_ba1, entity_ba2, entity_ba3, entity_ba4, entity_ba5],
    'children': []
}

entity_bb1 = {'id': 9, 'nodeId': 5, 'name': 'Bb-1', 'matchesCount': 1}
entity_bb2 = {'id': 10, 'nodeId': 5, 'name': 'Bb-2', 'matchesCount': 1}
node_bb = {'id': 5, 'parentId': 3, 'entities': [entity_bb1, entity_bb2], 'children': []}

entity_b1 = {'id': 3, 'nodeId': 3, 'name': 'B-1', 'matchesCount': 1}
node_b = {'id': 3, 'parentId': None, 'entities': [entity_b1], 'children': [node_ba, node_bb]}

### Node C

entity_c1 = {'id': 11, 'nodeId': 6, 'name': 'C-1', 'matchesCount': 1}
node_c = {'id': 6, 'parentId': None, 'entities': [entity_c1], 'children': []}
