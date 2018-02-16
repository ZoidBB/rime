from flask import current_app
from mongoengine import DynamicDocument
from mongoengine.fields import *
from rime.util import Box, slugify

models = Box()

class Content(DynamicDocument):
    abspath = StringField(required=True)
    relpath = StringField(required=True)
    archetype = StringField(required=True)
    title = StringField(required=True)
    date = DateTimeField(required=True)
    slug = StringField(required=True)
    source = StringField(required=True)
    compiled = StringField(required=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super(DynamicDocument, self).save(*args, **kwargs)

    @property
    def url(self):
        this_archetype = current_app.plugins.RimeCore.archetypes[
                self.archetype]
        return this_archetype._url_for(self)
models.content = Content

def make_model_for_data(name):
    class Data(DynamicDocument):
        pass
    Data.__name__ = name
    models[name] = Data
    return Data
