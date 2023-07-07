#
# Build image
#

FROM python:3.9-slim-buster AS builder

RUN pip install poetry==1.5.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /core_api
COPY pyproject.toml poetry.lock ./
RUN poetry install --with=prod --no-root && rm -rf $POETRY_CACHE_DIR


#
# Prod image
#


FROM python:3.9-slim-buster AS prod

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

ENV \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 
    
# Set the working directory to /core_api
WORKDIR /core_api

ENV VIRTUAL_ENV=/core_api/.venv \
    PATH="/core_api/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# Copy the current directory contents into the container at /core_api
COPY . /core_api

WORKDIR /core_api

# Run app.py when the container launches
ENTRYPOINT ["python", "main.py"]