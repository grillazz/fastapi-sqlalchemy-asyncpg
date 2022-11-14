# fastapi-sqlalchemy-asyncpg
[![developer](https://img.shields.io/badge/Dev-grillazz-green?style)](https://github.com/grillazz)
![language](https://img.shields.io/badge/language-python-blue?style)
[![CI](https://img.shields.io/github/workflow/status/grillazz/fastapi-sqlalchemy-asyncpg/Unit%20Tests/main)](https://github.com/grillazz/fastapi-sqlalchemy-asyncpg/actions/workflows/build-and-test.yml?query=event%3Apush+branch%3Amain)
[![license](https://img.shields.io/github/license/grillazz/fastapi-sqlalchemy-asyncpg)](https://github.com/grillazz/fastapi-sqlalchemy-asyncpg/blob/main/LICENSE)
![visitors](https://visitor-badge.laobi.icu/badge?page_id=grillazz.fastapi-sqlalchemy-asyncpg")

![fastapi-sqlalchemy-asyncpg](/static/fsap.jpg)

Example for [FastAPI](https://fastapi.tiangolo.com/) integration with [SQLAlchemy](https://www.sqlalchemy.org/) ORM with PostgreSQL via [asyncpg](https://github.com/MagicStack/asyncpg) a fast Database Client Library for python/asyncio.

Beside of using latest and greatest version of [SQLAlchemy](https://www.sqlalchemy.org/) with it robustness, powerfulness and speed
of [asyncpg](https://github.com/MagicStack/asyncpg) there is [FastAPI](https://fastapi.tiangolo.com/) (modern, fast (high-performance), 
web framework for building APIs with Python 3.8+ based on standard Python type hints.) already reviewed
on [thoughtworks](https://www.thoughtworks.com/radar/languages-and-frameworks?blipid=202104087) and noted in 
Python Developers [Survey 2021 Results](https://lp.jetbrains.com/python-developers-survey-2021/#FrameworksLibraries)
as the fifth official annual Python Developers Survey, conducted as a collaborative effort between the Python Software Foundation and JetBrains.

### How to Setup
To build , run and test and more ... use magic of make help to play with this project.
```shell
make help
```
and you receive below list:
```text
build                Build project with compose
clean                Clean Reset project containers and volumes with compose
feed_db              create database objects and insert data
format               Format project code.
help                 Show this help
lint                 Lint project code.
migrate-apply        apply alembic migrations to database/schema
migrate-create       create new alembic migration
py-upgrade           Upgrade project py files with pyupgrade library for python version 3.10
requirements         Refresh requirements.txt from pipfile.lock
safety               Check project and dependencies with safety https://github.com/pyupio/safety
slim-build           with power of docker-slim build smaller and safer images
test                 Run project tests
up                   Run project with compose
```


### How to feed database

It took me a while to find nice data set. Hope works of Shakespeare as example will be able to cover 
first part with read only declarative base configuration and all type of funny selects :)
Data set is coming form https://github.com/catherinedevlin/opensourceshakespeare
Next models were generated with https://github.com/agronholm/sqlacodegen
And after some tweaking I got desired result

Hope you enjoy it.

### Change Log
- 4 JUN 2022 alembic migrations added to project
- 6 JUN 2022 added initial dataset for shakespeare models
- 3 OCT 2022 poetry added to project
- 12 NOV 2022 ruff implemented to project as linting tool
