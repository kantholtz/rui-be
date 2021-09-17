from dataclasses import dataclass

from marshmallow import fields, post_load

from src.rui_be.models.camel_case_schema import CamelCaseSchema


@dataclass
class Match:
    entity_id: int

    ticket: int
    context: str
    mention: str
    mention_indexes: list[int]


class MatchSchema(CamelCaseSchema):
    entity_id = fields.Integer(required=True)

    ticket = fields.Integer(required=True)
    context = fields.String(required=True)
    mention = fields.String(required=True)
    mention_indexes = fields.List(fields.Integer(), required=True)

    @post_load
    def make_obj(self, data, **kwargs) -> Match:
        return Match(**data)

    class Meta:
        ordered = True
