import typer
from rich.console import Console

from jarvis.settings import settings

app = typer.Typer()
console = Console()


@app.callback()
def main():
    """
    This function is run before any command.
    We can leave it empty for now.
    """
    pass


if __name__ == "__main__":
    app()
