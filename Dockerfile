FROM ubuntu:25.10 AS base

RUN apt-get update -qy \
    && apt-get install -qyy \
    -o APT::Install-Recommends=false \
    -o APT::Install-Suggests=false \
    build-essential \
    ca-certificates \
    python3-setuptools \
    python3.14-dev


COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON=python3.14 \
    UV_PROJECT_ENVIRONMENT=/panettone

COPY pyproject.toml /_lock/
COPY uv.lock /_lock/

RUN cd /_lock && uv sync --locked --no-install-project
##########################################################################
FROM ubuntu:25.10

ENV PATH=/panettone/bin:$PATH

RUN groupadd -r panettone
RUN useradd -r -d /panettone -g panettone -N panettone

STOPSIGNAL SIGINT

RUN apt-get update -qy && apt-get install -qyy \
    -o APT::Install-Recommends=false \
    -o APT::Install-Suggests=false \
    python3.14 \
    libpython3.14 \
    libpcre3

RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

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