from typing import Dict

from flask.json import JSONEncoder

from src.taxonomy import Symptom


class JsonEncoder(JSONEncoder):
    def default(self, obj: any) -> Dict:

        if isinstance(obj, Symptom):
            symptom: Symptom = obj

            return {
                'id': symptom.id,
                'name': symptom.name,
                'parent': symptom.parent.id if symptom.parent else None,
                'children': symptom.children
            }

        else:
            return super(JsonEncoder, self).default(obj)
