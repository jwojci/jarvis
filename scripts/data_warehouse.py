import os

import typer
from boto3.session import Session
from rich.console import Console
from dotenv import load_dotenv

load_dotenv()

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")


app = typer.Typer()
console = Console()

# check if config is set
if not all([MINIO_ACCESS_KEY, MINIO_SECRET_KEY]):
    console.print(
        "[bold red]Error:[/bold red] Missing MinIO configuration. Please set MINIO_ACCESS_KEY and MINIO_SECRET_KEY environment variables."
    )
    raise typer.Exit(code=1)

s3_client = Session(
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
).client("s3", endpoint_url=f"http://{MINIO_ENDPOINT}")


@app.command()
def upload(
    file_path: str = typer.Argument(..., help="Path to the local file to upload"),
    bucket_name: str = typer.Argument("jarvis-bucket", help="Name of the bucket"),
):
    """Uploads a file to the specified MinIO bucket, creating one if it doesn't exist."""
    object_name = os.path.basename(file_path)

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
    bucket_name: str = typer.Argument("jarvis-bucket", help="Name of the bucket")
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
