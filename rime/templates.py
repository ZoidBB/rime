from jinja2.loaders import FileSystemLoader
import os.path

class RimeLoader(FileSystemLoader):
    def __init__(self, rime):
        self.rime = rime
        self.encoding = 'utf-8'
        self.followlinks = False

    @property
    def searchpath(self):
        return self.rime.template_dirs
