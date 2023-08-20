# fastapi-sqlalchemy-asyncpg
[![developer](https://img.shields.io/badge/Dev-grillazz-green?style)](https://github.com/grillazz)
![language](https://img.shields.io/badge/language-python-blue?style)
[![CI](https://img.shields.io/github/workflow/status/grillazz/fastapi-sqlalchemy-asyncpg/Unit%20Tests/main)](https://github.com/grillazz/fastapi-sqlalchemy-asyncpg/actions/workflows/build-and-test.yml?query=event%3Apush+branch%3Amain)
[![license](https://img.shields.io/github/license/grillazz/fastapi-sqlalchemy-asyncpg)](https://github.com/grillazz/fastapi-sqlalchemy-asyncpg/blob/main/LICENSE)
![visitors](https://visitor-badge.laobi.icu/badge?page_id=grillazz.fastapi-sqlalchemy-asyncpg")

![fastapi-sqlalchemy-asyncpg](/static/fsap_1.jpg)

<a name="readme-top"></a>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



## About The Project

Example of [FastAPI](https://fastapi.tiangolo.com/) integration supported by almighty [Pydantic 2.0](https://github.com/pydantic/pydantic)
with [SQLAlchemy ORM](https://www.sqlalchemy.org/) and PostgreSQL 
connected via fastest Database Client Library for python/asyncio [asyncpg](https://github.com/MagicStack/asyncpg).

Beside of using latest and greatest version of [SQLAlchemy](https://www.sqlalchemy.org/) with it robustness, powerfulness and speed
of [asyncpg](https://github.com/MagicStack/asyncpg) there is [FastAPI](https://fastapi.tiangolo.com/) (modern, fast (high-performance), 
web framework for building APIs with Python 3.8+ based on standard Python type hints.) already reviewed
on [thoughtworks](https://www.thoughtworks.com/radar/languages-and-frameworks?blipid=202104087) and noted in 
Python Developers [Survey 2021 Results](https://lp.jetbrains.com/python-developers-survey-2021/#FrameworksLibraries)
as the fifth official annual Python Developers Survey, conducted as a collaborative effort between the Python Software Foundation and JetBrains.

### Built With
[![FastAPI][fastapi.tiangolo.com]][fastapi-url]
[![Pydantic][pydantic.tiangolo.com]][pydantic-url]
[![SQLAlchemy][sqlalchemy.org]][sqlalchemy-url]
[![Uvicorn][uvicorn.org]][uvicorn-url]
[![pytest][pytest.org]][pytest-url]
[![asyncpg][asyncpg.github.io]][asyncpg-url]
[![alembic][alembic.sqlalchemy.org]][alembic-url]
[![rich][rich.readthedocs.io]][rich-url]



<p align="right">(<a href="#readme-top">back to top</a>)</p>

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

#### Generate Fernet key for storing password in db
```python
In [1]: from cryptography.fernet import Fernet

In [2]: Fernet.generate_key()
Out[2]: b'Ms1HSn513x0_4WWFBQ3hYPDGAHpKH_pIseC5WwqyO7M='

```
Save the key in .secrets as FERNET_KEY


## Local development with poetry

```shell
pyenv install 3.11 && pyenv local 3.11
```
```shell
poetry install
```
Hope you enjoy it.

## Acknowledgments
Use this space to list resources you find helpful and would like to give credit to. I've included a few of my favorites to kick things off!

* [Open Source Shakespeare Dataset](https://github.com/catherinedevlin/opensourceshakespeare)
* [SQL Code Generator](https://github.com/agronholm/sqlacodegen)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Change Log
- **[long time ago...]** it was a long time ago in galaxy far far away...
- **[JUN 4 2022]** alembic migrations added to project
- **[JUN 6 2022]** initial dataset for shakespeare models
- **[OCT 3 2022]** poetry added to project
- **[NOV 12 2022]** ruff implemented to project as linting tool
- **[FEB 14 2023]** bump project to Python 3.11
- **[APR 10 2023]** implement logging with rich
- **[APR 28 2023]** Rainbow logs with rich :rainbow:
- **[JUL 7 2023]** migrate to pydantic 2.0 :fast_forward:
- **[JUL 25 2023]** add user authentication with JWT and Redis as token storage :lock: :key:

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/grillazz/fastapi-sqlalchemy-asyncpg.svg?style=for-the-badge
[fastapi.tiangolo.com]: https://img.shields.io/badge/FastAPI-0.101.1-009485?style=for-the-badge&logo=fastapi&logoColor=white
[fastapi-url]: https://fastapi.tiangolo.com/
[pydantic.tiangolo.com]: https://img.shields.io/badge/Pydantic-2.2.1-e92063?style=for-the-badge&logo=pydantic&logoColor=white
[pydantic-url]: https://docs.pydantic.dev/latest/
[sqlalchemy.org]: https://img.shields.io/badge/SQLAlchemy-2.0.20-bb0000?color=bb0000&style=for-the-badge
[sqlalchemy-url]: https://docs.sqlalchemy.org/en/20/
[uvicorn.org]: https://img.shields.io/badge/Uvicorn-0.23.2-2094f3?style=for-the-badge&logo=uvicorn&logoColor=white
[uvicorn-url]: https://www.uvicorn.org/
[asyncpg.github.io]: https://img.shields.io/badge/asyncpg-0.28.0-2e6fce?style=for-the-badge&logo=postgresql&logoColor=white
[asyncpg-url]: https://magicstack.github.io/asyncpg/current/
[pytest.org]: https://img.shields.io/badge/pytest-6.2.5-fff?style=for-the-badge&logo=pytest&logoColor=white
[pytest-url]: https://docs.pytest.org/en/6.2.x/
[alembic.sqlalchemy.org]: https://img.shields.io/badge/alembic-1.11.3-6BA81E?style=for-the-badge&logo=alembic&logoColor=white
[alembic-url]: https://alembic.sqlalchemy.org/en/latest/

[rich.readthedocs.io]: https://img.shields.io/badge/rich-10.12.0-009485?style=for-the-badge&logo=rich&logoColor=white
[rich-url]: https://rich.readthedocs.io/en/latest/
[redis.io]: https://img.shields.io/badge/redis-3.5.3-dc382d?style=for-the-badge&logo=redis&logoColor=white
[redis-url]: https://redis.io/
