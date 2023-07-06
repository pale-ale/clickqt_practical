import click
import sys
from clickqt.core.core import qtgui_from_click
from importlib import util, metadata

@click.group('clickqtfy')
def clickqtfy():
	''' Generate a GUI for an entry point inside EPFILE named EPNAME. '''

@clickqtfy.command('ep')
@click.argument('epname')
def package(epname):
	qtgui_from_click(get_command_from_entrypoint(epname), True, epname)()

@clickqtfy.command('file')
@click.argument('epfile', type=click.Path(exists=True))
@click.argument('epname')
def withep(epfile, epname):
	qtgui_from_click(get_command_from_path(epfile, epname), False, str(epfile))()

def get_command_from_entrypoint(epname:str) -> click.Command:
	eps = get_entrypoints_from_name(epname)
	if len(eps) == 0:
		raise ImportError(f"No entry point named '{epname}' found.")
	if len(eps) > 1:
		concateps = "\n".join([ep.name for ep in eps])
		raise ImportError(f"No entry point named '{epname}' found. Did you mean one of the following:\n{concateps}")
	return validate_entrypoint(eps[0].load())

def get_entrypoints_from_name(epname:str) -> list[metadata.EntryPoint]:	
		grouped_eps = metadata.entry_points()
		candidates:list[metadata.EntryPoint] = []
		for group in grouped_eps.groups:
			for ep in grouped_eps.select(group=group):
				if ep.name == epname:
					return [ep]
				if epname in ep.name or epname in ep.value:
					candidates.append(ep)
		return candidates

def get_command_from_path(eppath:str, epname:str) -> click.Command:	
	modulename = f"clickqtfy.imported_module"
	spec = util.spec_from_file_location(modulename, eppath)
	module = util.module_from_spec(spec)
	sys.modules[modulename] = module
	spec.loader.exec_module(module)
	entrypoint = getattr(module, epname, None)
	if entrypoint is None:
		raise ImportError(f"Module '{spec.origin}' does not contain the entry point '{epname}'.")
	return validate_entrypoint(entrypoint)
	
def validate_entrypoint(ep):
	if not isinstance(ep, click.Command):
		raise TypeError(f"Entry point '{ep}' is not a 'click.Command'.")
	return ep