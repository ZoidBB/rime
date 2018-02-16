import click, os, shutil, sys
from rime import Rime

rime = Rime(__name__)
module_root = os.path.dirname(os.path.abspath(__file__))
skeleton_path = os.path.join(module_root, "skel")

@click.group()
def main():
    pass
    
def _initialize_rime(root_path, config_file):
    if not os.path.isdir(root_path):
        click.echo("Site directory not found, aborting.")
        sys.exit(1)
    if not os.path.isfile(config_file):
        click.echo("Config file not found, aborting.")
        sys.exit(1)
    root_path = os.path.abspath(root_path)
    rime.initialize(root_path, config_file)

@main.command()
@click.option('--root-path', default='.', help='main directory')
@click.option('--config-file', default='rime.toml', help='config file')
@click.option("--host", default="localhost", help="address to bind to")
@click.option("--port", default=5000, help="port to bind to")
def run(root_path, config_file, host, port):
    """Run development server"""
    _initialize_rime(root_path, config_file)
    rime.run(host, port, debug=False, use_reloader=False)
    rime.cleanup()

@main.command()
@click.option('--root-path', default='.', help='main directory')
@click.option('--config-file', default='rime.toml', help='config file')
@click.option("--output-path", default="output/")
def build(root_path, config_file):
    """Build static main files"""
    _initialize_rime(root_path, config_file)
    rime.freezer.freeze()
    rime.cleanup()

@main.command()
@click.option('--root-path', default='.', help='main directory')
@click.option('--config-file', default='rime.toml', help='config file')
def shell(root_path, config_file):
    """Run a shell post-init"""
    _initialize_rime(root_path, config_file)
    ctx = { "rime": rime }
    try:
        import IPython
        IPython.embed(user_ns=ctx)
    except ImportError:
        import code
        code.interact(local=ctx)
    rime.cleanup()

@main.command()
@click.argument("dirname")
def create(dirname):
    if os.path.exists(dirname):
        click.echo("Directory already exists")
        system.exit(1)
    shutil.copytree(skeleton_path, dirname)
