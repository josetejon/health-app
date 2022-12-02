from mongoengine import Document, fields


class Component(Document):
    observation_name = fields.StringField(max_length=200, required=True)
    value = fields.StringField(max_length=20, required=True)
    value_type = fields.StringField(max_length=20, required=True)
    value_unit = fields.StringField(max_length=20, required=True)
    observation_parent = fields.ObjectIdField(required=True)


class Observation(Document):
    monitored_id = fields.IntField()
    observation_name = fields.StringField(max_length=200)
    issued = fields.DateTimeField()
    value = fields.StringField(max_length=20, required=False)
    value_type = fields.StringField(max_length=20, required=False)
    value_unit = fields.StringField(max_length=20, required=False)
    _id = fields.ObjectIdField(required=True)
