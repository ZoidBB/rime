from rime.core.blueprint import CoreBlueprint
from rime.core.exception import ProcessingError
from rime.core.models import models

from datetime import datetime
from flask import abort, render_template, url_for

import os.path
import re
import toml

CONTENT_REGEX = re.compile("(---+(?P<header>.+)---+)?(?P<body>.*)", re.M|re.S)


class Archetype:
    def __init__(self, plugin, name, path):
        self.plugin = plugin
        self.rime = plugin.rime
        self.logger = plugin.logger
        self.name = name
        self.path = path

    @property
    def config(self):
        return self.rime.config.archetypes.get(self.name) or \
                self.rime.config.archetypes._default

    def init(self):
        """
        Create routes
        """
        route_context = self._route_context()

        if self.config.generate_index:
            self.index.__func__.__name__ = "%s_index" % self.name
            index_route = self.config.base_url % route_context
            CoreBlueprint.route(index_route)(self.index)

        self.view.__func__.__name__ = "%s_view" % self.name
        view_route = os.path.join(
                self.config.base_url,
                self.config.route
                ) % route_context
        CoreBlueprint.route(view_route)(self.view)

        def url_generator():
            for item in models.content.objects(archetype=self.name):
                yield self._url_data_for(item)
        url_generator.__name__ = "RimeCore.%s_view" % self.name
        self.rime.freezer.register_generator(url_generator)

    def load(self):
        self._load_from_directory(self.path)

    def index(self):
        return "index test"

    def view(self, slug, **_):
        item = models.content.objects(
                archetype=self.name,
                slug=slug).first()
        if not item: abort(404)
        return render_template("content/_default_view.html", item=item)

    def _load_from_directory(self, directory):
        for entry in os.scandir(directory):
            if entry.is_dir():
                self._load_from_directory(entry.path)
                continue

            relpath = entry.path[len(self.rime.root_path)+1:]

            with open(entry.path) as entry_fd:
                try:
                    data, body = self._process_source(entry_fd.read())
                except ProcessingError as exception:
                    self.logger.warning(
                            "Error processing `%s`: %s",
                            relpath,
                            exception)
                    continue

            content_obj = models.content(
                    abspath = entry.path,
                    relpath = relpath,
                    archetype = self.name,
                    **data
                    )
            content_obj.source = body
            content_obj.compiled = self._compile_body(
                    body,
                    os.path.splitext(entry.path)[1]
                    )
            content_obj.save()

    def _process_source(self, source):
        regex_match = CONTENT_REGEX.match(source)
        if not regex_match:
            raise ProcessingError('Content file invalid, no header?')

        match_dict = regex_match.groupdict()
        header = self._process_header(match_dict['header'])
        body = self._process_body(match_dict['body'])

        return header, body

    def _process_header(self, header):
        if not header or not header.strip():
            raise ProcessingError('Header missing')

        try:
            header = toml.loads(header)
        except toml.TomlDecodeError as exception:
            raise ProcessingError('Header invalid: %s' % exception)

        if 'title' not in header or not header.get('title', '').strip():
            raise ProcessingError('Header missing title')
        if 'date' not in header:
            raise ProcessingError('Header missing date')
        if not isinstance(header['date'], datetime):
            raise ProcessingError('Header date invalid')

        return header

    def _process_body(self, body):
        if not body or not body.strip():
            raise ProcessingError('Body empty')

        return body.strip()

    def _compile_body(self, body, ext):
        processor = self.plugin.content_processors.get(ext)
        if not processor: return body
        return processor(body)

    def _route_context(self):
        return { "archetype": self.name }

    def _url_data_for(self, item):
        route_context = self._route_context()
        base_route = os.path.join(
                self.rime.config.site.base_url,
                self.config.base_url,
                self.config.route) % route_context
        route_fields = [x.group(1) for x in re.finditer(
            "<([^>]+)>",
            base_route)]
        field_data = {}
        for field in route_fields:
            attr = field.split(":", 1)[-1]
            field_data[attr] = self._resolve_route_field(item, attr)
        return field_data

    def _url_for(self, item):
        return url_for('.%s_view' % self.name, **self._url_data_for(item))

    def _resolve_route_field(self, item, field):
        special = {
                "year": lambda x: x.strftime("%Y"),
                "month": lambda x: x.strftime("%m"),
                "day": lambda x: x.strftime("%d")
                }

        value = item
        for x in field.split("__"):
            if x in special:
                value = special[x](value)
            else:
                value = getattr(value, x)
        return value
