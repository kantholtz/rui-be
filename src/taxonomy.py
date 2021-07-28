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

next_id = 1


def get_symptoms() -> List[Symptom]:
    return root_symptoms


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


def update_symptom(symptom_id: int, new_name: str) -> Symptom:
    symptom = lookup_symptoms[symptom_id]

    symptom.name = new_name

    return symptom


def delete_symptom(symptom_id: int) -> Symptom:
    symptom = lookup_symptoms[symptom_id]

    for child in symptom.children:
        delete_symptom(child.id)

    if symptom.parent:
        symptom.parent.children.remove(symptom)
    else:
        root_symptoms.remove(symptom)

    return symptom
