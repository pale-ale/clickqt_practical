import click
import clickqt

import os


@click.command()
@click.option(
    "--verbose",
    type=bool,
    is_flag=True,
    default=True,
    required=True,
    help="Whether we want verbose output"
)
@click.argument("username", 
                default=lambda: os.environ.get("USERNAME", ""))
@click.option('-c', '--count', 
              count=True, 
              help="Repetition of the option")
@click.option('--hash-type-single', 
              type=click.Choice(['MD5', 'SHA1']))
@click.option('--hash-type-multiple', 
              type=click.Choice(['MD5', 'SHA1']), 
              multiple=True)
@click.password_option()
def main(verbose, username, count, hash_type_single, hash_type_multiple, password):
    click.echo(f"\nverbose: '{verbose}'\n" +
                f"username: '{username}'\n" +
                f"count: '{count}'\n" +
                f"hash_type_single: '{hash_type_single}'\n" +
                f"hash_type_multiple: '{hash_type_multiple}'\n" +
                f"password: '{password}'\n") #Only for testing!!!


if __name__ == "__main__":
    gui = clickqt.qtgui_from_click(main)
    gui()
