from rime import Plugin
from rime.core.archetype import Archetype
from rime.core.blueprint import CoreBlueprint
from rime.core.models import models
from rime.util import Box
from mongoengine import connect

import os.path
import rime.util

class RimeCore(Plugin):
    content_processors = {}

    def __init__(self):
        Plugin.__init__(self)
        self.content_dir = None
        self.data_dir = None
        self.base_url = None
        self.archetypes = Box()
        self.models = models

    @classmethod
    def register_processor(cls, extension):
        def decorator(function):
            cls.content_processors[extension] = function
            return function
        return decorator

    def preinit(self):
        """
         - 'connect' mongomock
         - anything else that doesn't make major modifications
        """
        connect('rime', host='mongomock://localhost')

        self.content_dir = self.rime.get_relative_dir("content/")
        self.data_dir = self.rime.get_relative_dir("data/")
        self.base_url = self.config.get('base_url', '/')

    def init(self):
        """
        Heavy lifting
         - Detect content types and generate routes
         - Load content into mongomock
        """

        # This is weird, but since they need to import this class
        # we gotta import them here.. plus it makes sense? kinda?
        import rime.core.processors

        self._init_archetypes()
        self._init_data()

    def postinit(self):
        """
        Register the blueprint after all else has been completed
        """
        self.rime.register_blueprint(CoreBlueprint, url_prefix=self.base_url)

        self._load_archetypes()
        self._load_data()

        @self.rime.context_processor
        def inject_models():
            return { "models": models }

    def _init_archetypes(self):
        for archetype_name in os.listdir(self.content_dir):
            abspath = os.path.join(self.content_dir, archetype_name)
            if not os.path.isdir(abspath): continue

            archetype = Archetype(
                    self,
                    archetype_name,
                    abspath
                    )
            archetype.init()
            self.archetypes[archetype_name] = archetype

    def _init_data(self):
        pass

    def _load_archetypes(self):
        for archetype_name, archetype in self.archetypes.items():
            archetype.load()

    def _load_data(self):
        pass
