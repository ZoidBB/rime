from flask import abort, Blueprint, current_app, render_template, send_from_directory
import os.path

CoreBlueprint = Blueprint("RimeCore", __name__)

@CoreBlueprint.route("/")
def index():
    plugin = current_app.plugins.RimeCore
    frontpage_archetypes = [archetype.name
                            for archetype in plugin.archetypes.values()
                            if archetype.config.frontpage]
    items = plugin.models.content.objects(archetype__in=frontpage_archetypes)
    items = items.order_by("-date")
    return render_template(
            "index.html",
            items=items)
