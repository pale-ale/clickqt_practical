import click
import clickqt


@click.command()
@click.option(
    "--verbose",
    count=True,
    help="Verbosity of the output"
)
@click.option(
    "--suppress",
    is_flag=True,
    help="Mute output"
)
@click.argument("filename")
def main(verbose, suppress, filename):
    if suppress:
        return
    match verbose:
        case 0:
            click.echo("<<Secrets you know nothing about>>")
        case 1:
            click.echo("Working...")
        case _:
            click.echo(f"Working on file '{filename}'...")
            
@click.group()
def cli():
    pass

@cli.command()
@click.option('--name', type=str, help='The name to greet.')
@click.option('--age', type=float, help='Your age in years.')
def greet(name, age):
    click.echo(f"Hello, {name}! You are {age} years old.")

@cli.command()
@click.option('--coordinates', nargs=2, type=float, help='The x and y coordinates')
def plot(coordinates):
    x, y = coordinates
    click.echo(f"Plotting point ({x}, {y})")


gui = clickqt.qtgui_from_click(cli)

if __name__ == "__main__":
    gui()
