from dataclasses import dataclass

from marshmallow import fields, post_load

from rui_be.models.camel_case_schema import CamelCaseSchema


@dataclass
class PredictionPatch:
    dismissed: bool


class PredictionPatchSchema(CamelCaseSchema):
    dismissed = fields.Boolean(required=True)

    @post_load
    def make_obj(self, data, **kwargs) -> PredictionPatch:
        return PredictionPatch(**data)

    class Meta:
        ordered = True
