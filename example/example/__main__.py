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
@click.confirmation_option(expose_value=False, prompt='Are you sure you want to run the application with these options?')
@click.argument('filename', type=click.Path(exists=True))
@click.argument('input', type=click.File('rb'))
@click.argument('output', type=click.File('wb'))
def passwd(username, verbose, count, hash_type_single, hash_type_multiple, range, password, filename, input, output):
    click.echo(f"verbose: '{verbose}'\n" +
               f"username: '{username}'\n" +
               f"count: '{count}'\n" +
               f"hash_type_single: '{hash_type_single}'\n" +
               f"hash_type_multiple: '{hash_type_multiple}'\n" +
               f"range: '{range}'\n" +
               f"password: '{password}'\n" +
               f"filename: '{filename}'")
    click.echo("input: ", nl=False)
    while True:
        chunk = input.read(1024)
        if not chunk:
            break
        output.write(chunk)
    click.echo() # New line


@utilgroup.command()
@click.option('--userinfo', type=(str, int, click.types.DateTime()))
def greet(userinfo):
    fname, no, date = userinfo
    date = date.strftime("%Y-%m-%d")
    click.echo(f"Hello, {fname}! Int, Date: {no, date}.")
    
@utilgroup.command()
@click.option('--pos', type=int, nargs=2)
def position(pos):
    a, b = pos
    click.echo(f"{a}/{b}")
    
@click.group()
def hello():
    pass

@hello.command()
@click.option('--n', type=int)
def hello_n(n):
    for i in range(n):
        click.echo(i)

@hello.command()
@click.option('--ns', type=(int, str), multiple=True)
def hello_ns(ns):
    for i,s in ns:
        for _ in range(i):
            click.echo(f"{s}{i}")
    
utilgroup.add_command(hello)

gui = clickqt.qtgui_from_click(utilgroup)

if __name__ == "__main__":
    utilgroup()
