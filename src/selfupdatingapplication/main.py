import typer
from rich import print
import os

from selfupdatingapplication.update_check import check_for_updates

__version__ = "1.1.0"

app = typer.Typer()

def version_callback(value: bool):
    if value:
        print(f"Version: {__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the application's version and exit.",
    )
):
    """
    A simple self-updating application.
    """
    check_for_updates()

@app.command()
def hello():
    """
    Says hello to the current user.
    """
    username = os.getlogin()
    print(f"Hello {username}")

if __name__ == "__main__":
    app()
