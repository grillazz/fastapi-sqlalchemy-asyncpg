# fastapi-sqlalchemy-asyncpg
[![developer](https://img.shields.io/badge/Dev-grillazz-green?style)](https://github.com/grillazz)
![language](https://img.shields.io/badge/language-python-blue?style)
[![CI](https://img.shields.io/github/workflow/status/grillazz/fastapi-sqlalchemy-asyncpg/Unit%20Tests/main)](https://github.com/grillazz/fastapi-sqlalchemy-asyncpg/actions/workflows/build-and-test.yml?query=event%3Apush+branch%3Amain)
[![license](https://img.shields.io/github/license/grillazz/fastapi-sqlalchemy-asyncpg)](https://github.com/grillazz/fastapi-sqlalchemy-asyncpg/blob/main/LICENSE)
![visitors](https://visitor-badge.laobi.icu/badge?page_id=grillazz.fastapi-sqlalchemy-asyncpg")

![fastapi-sqlalchemy-asyncpg](/static/fsap_1.jpg)

Example of [FastAPI](https://fastapi.tiangolo.com/) integration supported by almighty [Pydantic 2.0](https://github.com/pydantic/pydantic)
with [SQLAlchemy ORM](https://www.sqlalchemy.org/) and PostgreSQL 
connected via fastest Database Client Library for python/asyncio [asyncpg](https://github.com/MagicStack/asyncpg).

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

### Rainbow logs with rich :rainbow:

To deliver better user(developer) experience when watching logs with tons of information
from few emitters (which are really needy on development stage) project is using [rich](https://github.com/Textualize/rich) library.
Event with [rich](https://github.com/Textualize/rich) superpowers reading logs is not easy.
Found [rich](https://github.com/Textualize/rich) really nice - 
but it took time to learn how to integrate it as logger object properly and keep it as singleton.

To address below needs: 
- it is hard to find what I am looking for even with glasses on.
- don’t want to hire ELK to be able to use logs. 
- want to move fast enough with debugging.

Below steps were done to integrate [rich](https://github.com/Textualize/rich) into project.
1. Configure emitters with [config.ini](https://github.com/grillazz/fastapi-sqlalchemy-asyncpg/blob/main/config.ini)
2. Eliminate duplicates i.e. sqlalchemy echo by separate handlers
3. Keep logger as singleton pattern to avoid multiple instances
4. add uvicorn parameter --log-config config.ini

![sample-logs-with-rich](/static/logz.png)

### User authentication with JWT and Redis as token storage :lock: :key:


### Local development with poetry

```shell
pyenv install 3.11 && pyenv local 3.11
```
```shell
poetry install
```


Hope you enjoy it.

### Change Log
- 4 JUN 2022 alembic migrations added to project
- 6 JUN 2022 added initial dataset for shakespeare models
- 3 OCT 2022 poetry added to project
- 12 NOV 2022 ruff implemented to project as linting tool
- 14 FEB 2023 bump project to Python 3.11
- 10 APR 2023 implement logging with rich
- 28 APR 2023 Rainbow logs with rich :rainbow:
- 7 JUL 2023 migrate to pydantic 2.0 :fast_forward:
- 25 JUL 2023 add user authentication with JWT and Redis as token storage :lock: :keyv:

