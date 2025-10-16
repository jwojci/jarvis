# --- Settings ---
# Automatically load environment variables from the ./config/.env file
set dotenv-load := true
# Don't show the recipe name when running
set quiet 

# --- Project Setup ---
# Run this once after creating your virtual environment to fix all import errors.
install:
    uv pip install -e .

# --- Development Environment --- 
# Usage: just start-dev 
# Starts all required services: (Docker, MinIO) and the ZenML server.
# Run this in its own terminal window.
start-dev:
    @echo "Starting Docker Services (MinIO, Docker)..."
    docker-compose up -d
    @echo "Starting ZenML server..."
    @zenml login --local --blocking 

# Usage: just stop-dev 
# Stops all services
stop-dev:
    @echo "Stopping Docker services..."
    docker-compose down 
    @echo "Stopping ZenML server..."
    @zenml logout --local 
# --- Infrastructure ---
# Usage: just up 
up: 
    docker-compose up -d

# Usage: just down 
down:
    docker-compose down

# --- Data Management ---
# Usage: just upload "path/to/your/file.pdf"
upload file:
    uv run -m scripts.data_warehouse upload "{{file}}"


# Usage: just list-files
list-files:
    uv run -m scripts.data_warehouse list-files

# --- Pipeline Execution ---
# Usage: just ingest
ingest:
    uv run -m scripts.run 

ingest-no-cache:
    uv run -m scripts.run --no-cache