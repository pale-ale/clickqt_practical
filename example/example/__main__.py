import click
import clickqt


@click.command
@click.option(
    "--verbose",
    type=bool,
    is_flag=True,
    help="Whether we want verbose output"
)
@click.argument("filename")
def main(verbose, filename):
    if verbose:
        click.echo(f"Work on file '{filename}'")


gui = clickqt.qtgui_from_click(main)


if __name__ == "__main__":
    main()
