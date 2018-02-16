import flask
import flask_assets
import os.path

class Resolver(flask_assets.FlaskResolver):
    def split_prefix(self, ctx, item):
        return (os.path.join(ctx._app._tmpdir, 'static'),
               item,
               'static')

class Environment(flask_assets.Environment):
    resolver_class = Resolver

    @property
    def load_path(self):
        return self.app.static_dirs

    @property
    def directory(self):
        return os.path.join(self.app._tmpdir, "static")

    def get_static_folder(self):
        return url_for("static")
