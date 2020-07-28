from marshmallow import Schema, fields, validates, ValidationError
import re
import os


class TaskSchema(Schema):
    web_url = fields.Str(required=True)
    depth = fields.Int(required=True)
    id = fields.Int(required=True, dump_only=True)
    date_created = fields.DateTime(required=True, dump_only=True)
    download_url = fields.Function(lambda x: "{}/files/{}".format(
        os.getenv("PROJECT_URL"),
        x.id
    ))
    state = fields.Str()

    @validates("depth")
    def validate_depth(self, value):
        if value <= 0:
            raise ValidationError("Depth must be greater than 1")
        if value > 3:
            raise ValidationError("Depth must be lower than 3")

    @validates("web_url")
    def validate_url(self, value):
        if not re.match(r'(http(s)?:\/\/)?[\w\d\.\/]+', value, re.I).group(0):
            raise ValidationError("URL must be this type: 'https://some-site-url.domain.com/page'")