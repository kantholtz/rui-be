from typing import Dict

from flask.json import JSONEncoder

from src.taxonomy import OldSymptom


class JsonEncoder(JSONEncoder):
    def default(self, obj: any) -> Dict:

        if isinstance(obj, OldSymptom):
            symptom: OldSymptom = obj

            return {
                'id': symptom.id,
                'name': symptom.name,
                'parent': symptom.parent.id if symptom.parent else None,
                'children': symptom.children
            }

        else:
            return super().default(obj)
