from marshmallow import Schema, fields, validate

class BlogSchema(Schema):
    _id = fields.Str(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    content = fields.Str(required=True)
    image = fields.Str(required=False)
    imageKey = fields.Str(required=False)
    author = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    status = fields.Str(validate=validate.OneOf(['draft', 'published']), default='draft')

blog_schema = BlogSchema()
blogs_schema = BlogSchema(many=True) 