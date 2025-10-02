import typer
from rich.console import Console

from .application.ingestion import ingest_from_storage

app = typer.Typer(help="Jarvis CLI: Your personal engineering assistant.")
console = Console()


@app.callback()
def main():
    """
    This function is run before any command.
    We can leave it empty for now.
    """
    pass


@app.command()
def ingest(
    filename: str = typer.Argument(
        ..., help="The name of the file in the MinIO bucket to ingest."
    ),
    bucket: str = typer.Option("jarvis-bucket", help="The MinIO bucket name."),
):
    """
    Ingests a document from storage, processes it, and saves it to the vector store.
    """
    console.print(
        f"Starting ingestion for [cyan]{filename}[/cyan] from bucket [yellow]{bucket}[/yellow]..."
    )
    try:
        ingest_from_storage(bucket, filename)
        console.print("[bold green]✔ Ingestion command ran successfully![/bold green]")
    except Exception as e:
        console.print(f"[bold red]✖ Error during ingestion:[/bold red] {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
