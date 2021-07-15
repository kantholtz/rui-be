from typing import Dict

from flask.json import JSONEncoder

from taxonomy import Symptom


class JsonEncoder(JSONEncoder):
    def default(self, object_: any) -> Dict:

        if isinstance(object_, Symptom):
            symptom: Symptom = object_

            return {
                'id': symptom.id,
                'name': symptom.name,
                'parent': symptom.parent.id if symptom.parent else None,
                'children': symptom.children
            }

        else:
            return super(JsonEncoder, self).default(object_)
