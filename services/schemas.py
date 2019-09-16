from marshmallow import (
    fields,
    Schema,
)


class NLMatchWordsItemSchema(Schema):
    word = fields.String(required=True, allow_none=False)
    category = fields.Dict(required=True, allow_none=False)
    sim = fields.Float(required=True, allow_none=False)


class NLMatchWordsSchema(Schema):
    word = fields.String(required=True, allow_none=False)
    min_sim = fields.Float(required=False)
    max_count = fields.Integer(required=False)
    matches = fields.Nested(
        NLMatchWordsItemSchema, many=True, required=False)
    time_consumed = fields.Dict(required=False, allow_none=False)


class NLParseRecordSchema(Schema):
    text = fields.String(required=True, allow_none=False)
    result = fields.Dict(required=False, allow_none=False)
    time_consumed = fields.Dict(required=False, allow_none=False)
