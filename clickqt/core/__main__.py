import click
import sys
from clickqt.core.core import qtgui_from_click
from importlib import util


@click.command('clickqtfy')
@click.argument('epfile', type=click.Path(exists=True))
@click.argument('epname')
def clickqtfy(epfile, epname):
	''' Generate a GUI for an entry point inside EPFILE named EPNAME. '''
	modulename = f"clickqtfy.imported_module"
	spec = util.spec_from_file_location(modulename, epfile)
	if spec is None:
		raise ImportError(f"Cannot get spec from path '{epfile}'.")
	module = util.module_from_spec(spec)
	sys.modules[modulename] = module
	spec.loader.exec_module(module)
	entrypoint = getattr(module, epname, None)
	if entrypoint is None:
		raise ImportError(f"Python file at '{epfile}' does not contain the entry point named '{epname}'.")
	if not isinstance(entrypoint, click.Command):
		raise ImportError(f"Entry point '{epname}' is not a 'click.Command'.")
	qtgui_from_click(entrypoint)()
