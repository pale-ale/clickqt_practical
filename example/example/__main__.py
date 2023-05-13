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
@click.option('--userinfo', type=(str, click.types.DateTime()))
def greet(userinfo):
    name, date = userinfo
    click.echo(f"Hello, {name}! You are {0} years old. Today is {date}.")
    
@utilgroup.command()
@click.option('--pos', nargs=2, type=float)
def findme(pos):
    a, b = pos
    click.echo(f"{a}, {b}")

@click.command()
def hello():
    click.echo("Hello World")

gui = clickqt.qtgui_from_click(hello)

if __name__ == "__main__":
    hello()
