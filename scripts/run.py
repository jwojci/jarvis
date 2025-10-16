import typer
from loguru import logger
from rich.console import Console
from datetime import datetime as dt

from pipelines.ingestion_pipeline import ingestion_pipeline

app = typer.Typer()
console = Console()


@app.command()
def main(
    no_cache: bool = typer.Option(
        False, "--no-cache", help="Disable caching for the pipeline run."
    )
):
    """Main entry point for running pipelines."""
    console.print("[bold cyan] Starting Jarvis Ingestion Pipeline...[/bold cyan]")

    pipeline_args = {"enable_cache": not no_cache}

    run_name = f"ingestion_run_{dt.now().strftime("%Y_%m_%d_%H_%M_%S")}"
    ingestion_pipeline.with_options(run_name=run_name, **pipeline_args)()

    console.print("[bold green] Pipeline run finished. [/bold green]")


if __name__ == "__main__":
    app()
