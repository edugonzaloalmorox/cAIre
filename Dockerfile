FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends cuda-drivers cuda-nvcc cuda-runtime-dev

RUN pip install poetry


ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /caire-app

COPY pyproject.toml poetry.lock ./

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

COPY src ./src

RUN poetry install --without dev

WORKDIR /caire-app/src

EXPOSE 5000

CMD ["poetry", "run", "uvicorn", "test:app", "--host",  "0.0.0.0", "--port", "5000"]


