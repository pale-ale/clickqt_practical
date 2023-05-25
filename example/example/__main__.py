import click
import clickqt

import os

def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()

@click.group()
def utilgroup():
    pass


@utilgroup.command()
@click.argument("username",
                default=lambda: os.environ.get("USERNAME", ""))
@click.option(
    "--verbose",
    type=bool,
    is_flag=True,
    default=True,
    required=True,
    help="Verbosity of the output"
)
@click.option('-c', '--count',
              count=True,
              default=3,
              help="Repetition of the option")
@click.option('--hash-type-single',
              type=click.Choice(['MD5', 'SHA1']))
@click.option('--hash-type-multiple',
              type=click.Choice(['MD5', 'SHA1']),
              multiple=True)
@click.option('-r', '--range',
              type=click.FloatRange(max=20.23, clamp=True))
@click.password_option()
@click.confirmation_option(prompt='Are you sure you want to run the application with these options?')
def passwd(verbose, username, count, hash_type_single, hash_type_multiple, range, password, yes):
    click.echo(f"\nverbose: '{verbose}'\n" +
               f"username: '{username}'\n" +
               f"count: '{count}'\n" +
               f"hash_type_single: '{hash_type_single}'\n" +
               f"hash_type_multiple: '{hash_type_multiple}'\n" +
               f"range: '{range}'\n" +
               f"password: '{password}'\n" +
               f"yes: '{yes}'\n")


@utilgroup.command()
@click.option('--userinfo', type=((str, str), (int, click.types.DateTime())))
def greet(userinfo):
    (fname, lname), (no, date) = userinfo
    click.echo(f"Hello, {fname} {lname}! Int, Date: {no, date}.")
    
@utilgroup.command()
@click.option('--pos', type=int, nargs=2)
def position(pos):
    a, b = pos
    click.echo(f"{a}/{b}")
    
@click.group()
def hello():
    pass

@hello.command()
@click.option('-n', type=int)
def hello_n(n):
    for i in range(n):
        click.echo(i)
    
utilgroup.add_command(hello)

gui = clickqt.qtgui_from_click(utilgroup)

if __name__ == "__main__":
    utilgroup()
