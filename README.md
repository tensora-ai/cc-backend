# Tensora Count - Backend

## Prerequisites

- Python 3.13

## Remove virtual environment

```sh
rm -rf venv
```

## Create virtual environment

```sh
python3.13 -m venv venv
```

## Upgrade packaging tools

```sh
venv/bin/python -m pip install --upgrade pip wheel
```

## Install requirements

```sh
venv/bin/python -m pip install -r requirements.txt
```

## Run the server in development mode

```sh
export COSMOS_DB_ENDPOINT=? && \
    export COSMOS_DB_PRIMARY_KEY=? && \
    export COSMOS_DB_DATABASE_NAME=? && \
    export AZURE_STORAGE_CONNECTION_STRING=? && \
    export LOG_LEVEL=? && \
    export API_KEY=? && \
    PYTHONPATH=. venv/bin/uvicorn \
    app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload
```

## Check service health using CURL

```sh
curl -X GET "http://localhost:8000/api/v1/health"
```

```
{"status":"SUCCESS"}%
```

## Lint using Ruff

```sh
docker run --rm \
    --platform linux/x86_64 \
    -v $(pwd):/app \
    -w /app pipelinecomponents/ruff:latest \
    ruff check --fix .
```
