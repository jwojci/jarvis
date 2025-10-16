import os

import typer
from boto3.session import Session
from rich.console import Console
from rich.prompt import Prompt

from jarvis.settings import settings, DATA_SOURCES_CONFIG

app = typer.Typer()
console = Console()

# check if config is set
if not all([settings.MINIO_ACCESS_KEY, settings.MINIO_SECRET_KEY]):
    console.print(
        "[bold red]Error:[/bold red] Missing MinIO configuration. Please set MINIO_ACCESS_KEY and MINIO_SECRET_KEY environment variables."
    )
    raise typer.Exit(code=1)

s3_client = Session(
    aws_access_key_id=settings.MINIO_ACCESS_KEY,
    aws_secret_access_key=settings.MINIO_SECRET_KEY,
).client("s3", endpoint_url=f"http://{settings.MINIO_ENDPOINT}")


@app.command()
def upload(
    file_path: str = typer.Argument(..., help="Path to the local file to upload"),
    bucket_name: str = typer.Option(
        settings.MINIO_BUCKET_NAME, help="Name of the bucket"
    ),
):
    """Uploads a file to the specified MinIO bucket, creating one if it doesn't exist."""
    existing_categories = [config["prefix"] for config in DATA_SOURCES_CONFIG.values()]
    new_category_option = "Create a new category"
    choices = existing_categories + [new_category_option]

    chosen_category = Prompt.ask(
        "Select a category", choices=choices, default=existing_categories[0]
    )

    if chosen_category == new_category_option:
        category = Prompt.ask("Enter the name for the new category's directory")
        console.print(
            f"[bold yellow]⚠️  Warning:[/bold yellow] You've uploaded to a new category '{category}'."
        )
        console.print(
            f"For the pipeline to process it, you must manually update 'DATA_SOURCES_CONFIG' in 'settings.py' and create the necessary handlers."
        )
    else:
        category = chosen_category

    local_filename = os.path.basename(file_path)
    object_name = f"{category}/{local_filename}"

    try:
        # Check if bucket exists
        try:
            s3_client.head_bucket(Bucket=bucket_name)
        except s3_client.exceptions.ClientError:
            console.print(f"Bucket '{bucket_name}' not found. Creating it...")
            s3_client.create_bucket(Bucket=bucket_name)

        console.print(
            f"Uploading [cyan]{file_path}[/cyan] to bucket [yellow]{bucket_name}[/yellow]..."
        )
        s3_client.upload_file(file_path, bucket_name, object_name)
        console.print("[bold green]✔ Success![/bold green]")

    except Exception as e:
        console.print(f"[bold red]✖ Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def list_files(
    bucket_name: str = typer.Argument(
        settings.MINIO_BUCKET_NAME, help="Name of the bucket"
    )
):
    """Lists all of the objects in the specified bucket"""
    try:
        console.print(f"Listing files in bucket [yellow]{bucket_name}[/yellow]:")

        response = s3_client.list_objects_v2(Bucket=bucket_name)

        if "Contents" in response:
            for obj in response["Contents"]:
                console.print(f"- [cyan]{obj['Key']}[/cyan]")
        else:
            console.print("Bucket is empty or does not exist.")

    except Exception as e:
        console.print(
            f"[bold red]✖ Error while trying to list the files:[/bold red] {e}"
        )
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
