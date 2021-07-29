from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class OldSymptom:
    id: int

    name: str

    parent: any  # Symptom
    children: List  # List[Symptom]


root_symptoms: List[OldSymptom] = []
lookup_symptoms: Dict[int, OldSymptom] = {}

next_id = 1


def get_symptoms() -> List[OldSymptom]:
    return root_symptoms


def add_symptom(parent: Optional[OldSymptom], name: str) -> OldSymptom:
    global next_id

    symptom = OldSymptom(next_id, name, parent, [])
    next_id = next_id + 1

    if parent:
        parent.children.append(symptom)
    else:
        root_symptoms.append(symptom)

    lookup_symptoms[symptom.id] = symptom

    return symptom


def update_symptom(symptom_id: int, new_name: str) -> OldSymptom:
    symptom = lookup_symptoms[symptom_id]

    symptom.name = new_name

    return symptom


def delete_symptom(symptom_id: int) -> OldSymptom:
    symptom = lookup_symptoms[symptom_id]

    for child in symptom.children:
        delete_symptom(child.id)

    if symptom.parent:
        symptom.parent.children.remove(symptom)
    else:
        root_symptoms.remove(symptom)

    return symptom
