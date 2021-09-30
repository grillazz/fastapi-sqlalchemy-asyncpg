# Pull base image
FROM python:3.9-slim-buster as builder

# Set environment variables
WORKDIR /pipfiles
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

# Install pipenv
RUN set -ex && pip install pipenv --upgrade

# Install dependencies
RUN set -ex && pipenv lock -r > req.txt && pip install -r req.txt

FROM builder as final
WORKDIR /app
COPY ./the_app/ /app/
COPY ./tests/ /app/
COPY .env /app/

RUN set -ex && bash -c "eval $(grep 'PYTHONDONTWRITEBYTECODE' .env)"
RUN set -ex && bash -c "eval $(grep 'PYTHONUNBUFFERED' .env)"
