from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class Symptom:
    id: int

    name: str

    parent: any  # Symptom
    children: List  # List[Symptom]


root_symptoms: List[Symptom] = []
lookup_symptoms: Dict[int, Symptom] = {}

next_id = 0


def add_symptom(parent: Optional[Symptom], name: str) -> Symptom:
    global next_id

    symptom = Symptom(next_id, name, parent, [])
    next_id = next_id + 1

    if parent:
        parent.children.append(symptom)
    else:
        root_symptoms.append(symptom)

    lookup_symptoms[symptom.id] = symptom

    return symptom


cat_a = add_symptom(None, 'Cat A')
cat_a_1 = add_symptom(cat_a, 'Cat A.1')
cat_a_2 = add_symptom(cat_a, 'Cat A.2')
cat_b = add_symptom(None, 'Cat B')
