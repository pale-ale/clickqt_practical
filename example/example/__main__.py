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


gui = clickqt.qtgui_from_click(main)

if __name__ == "__main__":
    gui()
