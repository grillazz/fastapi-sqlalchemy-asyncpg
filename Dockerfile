FROM python:3.14-slim AS base

RUN apt-get update -qy \
    && apt-get install -qyy \
    -o APT::Install-Recommends=false \
    -o APT::Install-Suggests=false \
    build-essential \
    ca-certificates

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON=python3.14 \
    UV_PROJECT_ENVIRONMENT=/panettone

COPY pyproject.toml /_lock/
COPY uv.lock /_lock/

RUN cd /_lock && uv sync --locked --no-install-project
##########################################################################
FROM python:3.14-slim

ENV PATH=/panettone/bin:$PATH

RUN groupadd -r panettone
RUN useradd -r -d /panettone -g panettone -N panettone

COPY --from=base --chown=panettone:panettone /panettone /panettone

USER panettone
WORKDIR /panettone
COPY /app/ app/
COPY /tests/ tests/
COPY /templates/ templates/
COPY .env app/
COPY alembic.ini /panettone/alembic.ini
COPY /alembic/ /panettone/alembic/
COPY pyproject.toml /panettone/pyproject.toml