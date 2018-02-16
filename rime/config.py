from rime.util import Box
import flask
import toml

class Config(Box, flask.Config):
    """
    Config class to use Box. Basically ignores root_path, cause we can
    """

    def __init__(self, root_path, *args, **kwargs):
        Box.__init__(self, *args, **kwargs)
        flask.Config.__init__(self, root_path)

    def load_toml(self, filename):
        """
        Loads contents from a TOML file into the Config,
        merging its contents with the existing contents
        """
        with open(filename) as file_obj:
            self.update(toml.load(file_obj))
