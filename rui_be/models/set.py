from marshmallow import fields


class Set(fields.List):
    def _deserialize(self, *args, **kwargs):
        return set(super()._deserialize(*args, **kwargs))
