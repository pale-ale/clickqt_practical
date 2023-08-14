import click
from click_option_group import optgroup

@click.command()
@optgroup.group(
    "Server configuration", help="The configuration of some server connection"
)
@optgroup.option("-h", "--host", default="localhost", help="Server host name")
@optgroup.option("-p", "--port", type=int, default=8888, help="Server port")
@click.option("--debug/--no-debug", default=False, help="Debug flag")
@optgroup.group("Test configuration", help="The configuration of some test suite.")
@optgroup.option("--n", default=5, help="Number of test rounds")
def cli(host, port, debug, n):
    pass