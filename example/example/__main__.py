import click
import clickqt

import os


@click.group()
def utilgroup():
    pass


@utilgroup.command()
@click.argument("username",
                default=lambda: os.environ.get("USERNAME", ""))
@click.option(
    "--verbose",
    count=True,
    help="Verbosity of the output"
)
@click.option('-c', '--count',
              count=True,
              help="Repetition of the option")
@click.option('--hash-type-single',
              type=click.Choice(['MD5', 'SHA1']))
@click.option('--hash-type-multiple',
              type=click.Choice(['MD5', 'SHA1']),
              multiple=True)
@click.password_option()
def passwd(verbose, username, count, hash_type_single, hash_type_multiple, password):
    click.echo(f"\nverbose: '{verbose}'\n" +
               f"username: '{username}'\n" +
               f"count: '{count}'\n" +
               f"hash_type_single: '{hash_type_single}'\n" +
               f"hash_type_multiple: '{hash_type_multiple}'\n" +
               f"password: '{password}'\n")


@utilgroup.command()
@click.option('--name', type=str, help='The name to greet.')
@click.option('--age', type=int, help='Your age in years.')
def greet(name, age):
    click.echo(f"Hello, {name}! You are {age} years old.")


gui = clickqt.qtgui_from_click(utilgroup)

if __name__ == "__main__":
    utilgroup()
