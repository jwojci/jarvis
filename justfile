# --- Settings ---
# Automatically load environment variables from the ./config/.env file
set dotenv-load := true
# Don't show the recipe name when running
set quiet 


# --- Storage Management ---
# Usage: just upload "path/to/your/file.pdf"
upload file:
    uv run scripts/data_warehouse.py upload "{{file}}"


# Usage: just list-docs
list-files:
    uv run scripts/data_warehouse.py list-files

# --- Application Commands ---
ingest file:
    jarvis ingest "{{file}}"