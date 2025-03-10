from marshmallow import Schema, fields, validate, ValidationError

class ProductSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1))
    images = fields.List(fields.Str(), required=True, validate=validate.Length(min=1))
    imageKeys = fields.List(fields.Str(), required=True, validate=validate.Length(min=1))
    description = fields.Str(required=True, validate=validate.Length(min=1))
    price = fields.Float(required=False, allow_none=True)
    currency = fields.Str(required=False, allow_none=True)
    content = fields.Str(required=False, allow_none=True)
    categoryId = fields.Str(required=False)
    createdAt = fields.DateTime(required=False)
    updatedAt = fields.DateTime(required=False)
product_schema = ProductSchema() 