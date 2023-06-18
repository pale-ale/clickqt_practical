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
              confirmation_prompt=True,
              type=click.Choice(['MD5', 'SHA1']))
@click.option('--hash-type-multiple',
              required=True,
              type=click.Choice(['MD5', 'SHA1']),
              multiple=True)
@click.option('-r', '--range',
              confirmation_prompt=True,
              type=click.FloatRange(max=20.23, clamp=True))
@click.password_option()
@click.confirmation_option(expose_value=False, prompt='Are you sure you want to run the application with these options?')
@click.argument('filename', type=click.Path(exists=True))
@click.argument('input', type=click.File('rb'))
@click.argument('output', type=click.File('wb'))
def test(verbose, username, count, hash_type_single, hash_type_multiple, range, password, filename, input, output):
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
@click.option('--userinfo', type=(str, (int, click.types.DateTime())), default=["test", (1, "2023-06-14 15:20:25")])
def greet(userinfo):
    fname, (no, date) = userinfo
    click.echo(f"Hello, {fname}! Int, Date: {no, date}.")
    
@utilgroup.command()
@click.option('--pos', type=int, nargs=2, default=[1, 2])
def position(pos):
    a, b = pos
    click.echo(f"{a}/{b}")
    
@click.group()
def hello():
    print("Hello group")

@hello.command()
@click.option('-n', type=int, default=3)
def test(n):
    for i in range(n):
        click.echo(i)

def test_callback(ctx, param, value):
    if value=="2":
        return "123"
    else:
        raise click.BadParameter(f"Wrong value")

@hello.command()
@click.option('-t', type=str, callback=test_callback)
def test_with_callback(t):
    click.echo(t)

@hello.command()
@click.option('-ns', type=(int, str), multiple=True, required=True, default=[(1, "a"), (2, "b")])
def hello_ns(ns):
    for i,s in ns:
        for _ in range(i):
            click.echo(f"{s}{i}")

@hello.command()
@click.option('paths', '--path', multiple=True, envvar="PATH", default=[".", "tests"],
              type=click.Path(exists=True))
def hellp_path(paths):
    for path in paths:
        click.echo(path)

@click.group()
def hello2():
    print("Hello2 group")

@hello2.command()
@click.option('-ns', type=(int, str), multiple=True)
def hello_ns2(ns):
    for i,s in ns:
        for _ in range(i):
            click.echo(f"{s}{i}")
    
utilgroup.add_command(hello)
hello.add_command(hello2)
import sys
@click.command()
@click.option('--upper', 'transformation', flag_value='upper',
              default=True)
@click.option('--lower', 'transformation', flag_value='lower')
def info(transformation):
    click.echo(getattr(sys.platform, transformation)())

gui = clickqt.qtgui_from_click(info)

if __name__ == "__main__":
    #mine_set()
    gui()
