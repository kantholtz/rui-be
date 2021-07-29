from dataclasses import dataclass
from typing import List, Dict


@dataclass
class OldSymptom:
    id: int

    name: str

    parent: any  # Symptom
    children: List  # List[Symptom]


root_symptoms: List[OldSymptom] = []
lookup_symptoms: Dict[int, OldSymptom] = {}


def delete_symptom(symptom_id: int) -> OldSymptom:
    symptom = lookup_symptoms[symptom_id]

    for child in symptom.children:
        delete_symptom(child.id)

    if symptom.parent:
        symptom.parent.children.remove(symptom)
    else:
        root_symptoms.remove(symptom)

    return symptom
