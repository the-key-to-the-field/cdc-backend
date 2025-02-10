from marshmallow import Schema, fields, validate, ValidationError

class ProductSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1))
    image = fields.Str(required=True, validate=validate.Length(min=1))
    imageKey = fields.Str(required=True, validate=validate.Length(min=1))
    description = fields.Str(required=True, validate=validate.Length(min=1))
    price = fields.Float(required=False, allow_none=True)
    currency = fields.Str(required=False, allow_none=True)
    content = fields.Str(required=False, allow_none=True)
    categoryId = fields.Str(required=False)
    createdAt = fields.DateTime(required=False)
    updatedAt = fields.DateTime(required=False)
product_schema = ProductSchema() 