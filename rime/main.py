#!/usr/bin/env python
"""
Rime
"""


import coloredlogs
import flask
import flask_frozen
import importlib
import mongoengine
import os.path
import shutil
import tempfile
import toml
import hashlib

from rime.assets import Environment as AssetEnvironment
from rime.config import Config
from rime.templates import RimeLoader
from rime.util import Box

class Rime(flask.Flask):
    """
    Where all the magic happens
    """
    config_class = Config

    def __init__(self, *args, **kwargs):
        flask.Flask.__init__(self, *args, static_folder=None, **kwargs)

        # Should probably figure out a better way to deal with this
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)
        coloredlogs.install(logger=self.logger, level="WARNING")

        self.root_path = ""

        self.plugins = Box()
        self.plugin_load_order = []

        self.freezer = None
        self.assets = None

    @property
    def plugins_ordered(self):
        return [self.plugins[x] for x in self.plugin_load_order]

    @property
    def static_dirs(self):
        yield os.path.join(self._tmpdir, 'static')
        for plugin in self.plugins_ordered:
            if plugin.static_dir:
                yield plugin.static_dir

    @property
    def template_dirs(self):
        yield os.path.join(self._tmpdir, 'templates')
        for plugin in self.plugins_ordered:
            if plugin.template_dir:
                yield plugin.template_dir

    def initialize(self, root_path, config_file):
        """
         - Prepares Flask, Freezer, Assets, and in-memory DB
         - Finds and loads all plugins
         - Runs plugin init phases
        """
        self._init_core(root_path, config_file)
        self._plugins_load()
        self._plugins_phase('preinit')
        self._plugins_phase('init')
        self._plugins_phase('postinit')

    def get_relative_dir(self, dirname):
        return os.path.join(self.root_path, dirname)

    def cleanup(self):
        self._plugins_phase('precleanup')
        self._plugins_phase('cleanup')
        shutil.rmtree(self._tmpdir)
        self._plugins_phase('postcleanup')

    def _init_core(self, root_path, config_file):
        self.root_path = root_path

        self._tmpdir = tempfile.mkdtemp()
        os.mkdir(os.path.join(self._tmpdir, "templates"))
        os.mkdir(os.path.join(self._tmpdir, "static"))

        self.config.load_toml(config_file)

        self.freezer = flask_frozen.Freezer(self)

        self.assets = AssetEnvironment(self)

        self.jinja_env.loader = RimeLoader(self)
        self.jinja_env.globals['string_as_template'] = self._string_as_template

        @self.route("/static/<path:filename>")
        def static(filename):
            """
            Handle layered static files
            """
            if not filename: flask.abort(404)
            for static_dir in self.static_dirs:
                file_path = os.path.join(static_dir, filename)
                if os.path.isfile(file_path):
                    return flask.send_from_directory(static_dir, filename)
            flask.abort(404)

    def _plugins_load(self):
        """
        Imports plugins and gets them ready for init
        """
        for plugin in self.config.site.plugins:
            plugin_module_name, plugin_module_attribute = plugin.rsplit(".", 1)

            try:
                plugin_module = importlib.import_module(plugin_module_name)
            except ImportError as exception:
                self.logger.error("Unable to load plugin `%s`: %s", plugin,
                        exception)
                continue

            try:
                plugin_class = getattr(plugin_module, plugin_module_attribute)
            except AttributeError:
                self.logger.error(
                        "Unable to find plugin class in module `%s`, is it a valid Rime plugin?",
                        plugin)
                continue

            try:
                self.plugins[plugin_module_attribute] = plugin_class()
                self.plugins[plugin_module_attribute].load(self)
            except Exception as exception:
                self.logger.critical(
                        "Unable to instantiate plugin `%s`, Rime in unknown state: %s",
                        plugin, exception)
                continue

            self.plugin_load_order.append(plugin_module_attribute)

    def _plugins_phase(self, phase):
        for plugin_name, plugin_obj in self.plugins.items():
            getattr(plugin_obj, phase)()

    def _string_as_template(self, s):
        hasher = hashlib.sha512()
        hasher.update(s.encode())
        template_id = hasher.hexdigest()
        template_path = os.path.join(
                self._tmpdir,
                "templates",
                template_id)
        if os.path.exists(template_path):
            return template_id
        with open(template_path, 'w') as template_fd:
            template_fd.write(s)
        return template_id
