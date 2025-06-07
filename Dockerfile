FROM ubuntu:oracular AS build

RUN apt-get update -qy && apt-get install -qyy \
    -o APT::Install-Recommends=false \
    -o APT::Install-Suggests=false \
    build-essential \
    ca-certificates \
    python3-setuptools \
    python3.13-dev \
    git

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.13 \
    UV_PROJECT_ENVIRONMENT=/panettone

COPY pyproject.toml /_lock/
COPY uv.lock /_lock/

RUN --mount=type=cache,target=/root/.cache
RUN cd /_lock  && uv sync \
    --locked \
    --no-dev \
    --no-install-project
##########################################################################
FROM ubuntu:oracular

ENV PATH=/panettone/bin:$PATH

RUN groupadd -r panettone
RUN useradd -r -d /panettone -g panettone -N panettone

STOPSIGNAL SIGINT

RUN apt-get update -qy && apt-get install -qyy \
    -o APT::Install-Recommends=false \
    -o APT::Install-Suggests=false \
    python3.13 \
    libpython3.13 \
    libpcre3 \
    libxml2

RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY --from=build --chown=panettone:panettone /panettone /panettone

USER panettone
WORKDIR /panettone
COPY /app/ app/
COPY /tests/ tests/
COPY /templates/ templates/
COPY .env app/
COPY alembic.ini app/
COPY alembic/ app/alembic/
COPY logging-uvicorn.json /panettone/logging-uvicorn.json
COPY pyproject.toml /panettone/pyproject.toml

RUN python -V
RUN python -Im site
RUN python -Ic 'import uvicorn'
