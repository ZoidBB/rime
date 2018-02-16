import os, sys

class Plugin:
    """
    Rime Plugin Base Class
    """

    has_static = False
    has_templates = False

    def __init__(self):
        self.rime = None
        self.logger = None
        self.module_dir = os.path.dirname(
                os.path.abspath(
                    sys.modules[self.__module__].__file__
                )
            )

    @property
    def config(self):
        if self.__class__.__name__ not in self.rime.config.plugins:
            self.rime.config.plugins[self.__class__.__name__] = {}
        return self.rime.config.plugins[self.__class__.__name__]

    @property
    def template_dir(self):
        if not self.has_templates: return
        template_dir = os.path.join(self.module_dir, "templates")
        if os.path.isdir(template_dir):
            return template_dir

    @property
    def static_dir(self):
        if not self.has_static: return
        static_dir = os.path.join(self.module_dir, "static")
        if os.path.isdir(static_dir):
            return static_dir

    def load(self, rime):
        self.rime = rime
        self.logger = rime.logger

    def preinit(self):
        pass

    def init(self):
        pass

    def postinit(self):
        pass

    def precleanup(self):
        pass

    def cleanup(self):
        pass

    def postcleanup(self):
        pass
