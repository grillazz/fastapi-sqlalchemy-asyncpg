# fastapi-sqlalchemy-asyncpg
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

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
        <li><a href="#make-will-help-you">Make will help you</a></li>
        <li><a href="#how-to-feed-database">How to feed database</a></li>
        <li><a href="#rainbow-logs-with-rich">Rainbow logs with rich</a></li>
        <li><a href="#setup-user-auth">Setup user auth</a></li>
        <li><a href="#local-development-with-poetry">Local development with poetry</a></li>
        <li><a href="#import-xlsx-files-with-polars-and-calamine">Import xlsx files with polars and calamine</a></li>
      </ul>
    </li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

[//]: # (TODO: Usage,Roadmap, Contributing, License, Contact)

    




## About The Project

Example of [FastAPI](https://fastapi.tiangolo.com/) integration supported by almighty [Pydantic 2.0](https://github.com/pydantic/pydantic)
with [SQLAlchemy ORM](https://www.sqlalchemy.org/) and PostgreSQL16
connected via fastest Database Client Library for python/asyncio [asyncpg](https://github.com/MagicStack/asyncpg).

Beside of using latest and greatest version of [SQLAlchemy](https://www.sqlalchemy.org/) with it robustness, powerfulness and speed
of [asyncpg](https://github.com/MagicStack/asyncpg) there is [FastAPI](https://fastapi.tiangolo.com/) (modern, fast (high-performance), 
web framework for building APIs with Python 3.8+ based on standard Python type hints.) already reviewed
on [thoughtworks](https://www.thoughtworks.com/radar/languages-and-frameworks?blipid=202104087) and noted in 
Python Developers [Survey 2021 Results](https://lp.jetbrains.com/python-developers-survey-2021/#FrameworksLibraries)
as the fifth official annual Python Developers Survey, conducted as a collaborative effort between the Python Software Foundation and JetBrains.

### Built With
[![FastAPI][fastapi.tiangolo.com]][fastapi-url]
[![Pydantic][pydantic.com]][pydantic-url]
[![SQLAlchemy][sqlalchemy.org]][sqlalchemy-url]
[![Uvicorn][uvicorn.org]][uvicorn-url]
[![pytest][pytest.org]][pytest-url]
[![asyncpg][asyncpg.github.io]][asyncpg-url]
[![alembic][alembic.sqlalchemy.org]][alembic-url]
[![rich][rich.readthedocs.io]][rich-url]



<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

### Make will help you
To build , run and test and more ... use magic of make help to play with this project.
```shell
1. make docker-build
2. make docker-up
3. make docker-apply-db-migrations
4. make docker-feed-db
```


<p align="right">(<a href="#readme-top">back to top</a>)</p>

### How to feed database

It took me a while to find nice data set. Hope works of Shakespeare as example will be able to cover 
first part with read only declarative base configuration and all type of funny selects :)
Data set is coming form https://github.com/catherinedevlin/opensourceshakespeare
Next models were generated with https://github.com/agronholm/sqlacodegen

<p align="right">(<a href="#readme-top">back to top</a>)</p>

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

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Setup User Auth

Setup user authentication with JWT and Redis as token storage.

### Local development with poetry

```shell
pyenv install 3.12 && pyenv local 3.12
```
```shell
poetry install
```
Hope you enjoy it.

### Import xlsx files with polars and calamine
Power of Polars Library in data manipulation and analysis.
It uses the polars library to read the Excel data into a DataFrame by passing the bytes to the `pl.read_excel()` function -
https://docs.pola.rs/py-polars/html/reference/api/polars.read_excel.html
In `pl.read_excel()` “calamine” engine can be used for reading all major types of Excel Workbook (.xlsx, .xlsb, .xls) and is dramatically faster than the other options, using the fastexcel module to bind calamine.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Acknowledgments
Use this space to list resources you find helpful and would like to give credit to.
I've included a few of my favorites to kick things off!

* [Open Source Shakespeare Dataset](https://github.com/catherinedevlin/opensourceshakespeare)
* [SQL Code Generator](https://github.com/agronholm/sqlacodegen)
* [Passlib - password hashing library for Python](https://passlib.readthedocs.io/en/stable/)
* [Polars - fast DataFrame library for Rust and Python](https://docs.pola.rs/)

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
- **[SEP 2 2023]** add passlib and bcrypt for password hashing :lock: :key:
- **[OCT 21 2023]** refactor shakespeare models to use sqlalchemy 2.0 :fast_forward:
- **[FEB 1 2024]** bump project to Python 3.12 :fast_forward:
- **[MAR 15 2024]** add polars and calamine to project :heart_eyes_cat:
<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/grillazz/fastapi-sqlalchemy-asyncpg.svg?style=for-the-badge
[contributors-url]: https://github.com/grillazz/fastapi-sqlalchemy-asyncpg/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/grillazz/fastapi-sqlalchemy-asyncpg.svg?style=for-the-badge
[forks-url]: https://github.com/grillazz/fastapi-sqlalchemy-asyncpg/network/members
[stars-shield]: https://img.shields.io/github/stars/grillazz/fastapi-sqlalchemy-asyncpg.svg?style=for-the-badge
[stars-url]: https://github.com/grillazz/fastapi-sqlalchemy-asyncpg/stargazers
[issues-shield]: https://img.shields.io/github/issues/grillazz/fastapi-sqlalchemy-asyncpg.svg?style=for-the-badge
[issues-url]: https://github.com/grillazz/fastapi-sqlalchemy-asyncpg/issues
[license-shield]: https://img.shields.io/github/license/grillazz/fastapi-sqlalchemy-asyncpg.svg?style=for-the-badge
[license-url]: https://github.com/grillazz/fastapi-sqlalchemy-asyncpg/blob/main/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/python-has-powers/

[fastapi.tiangolo.com]: https://img.shields.io/badge/FastAPI-0.109.0-009485?style=for-the-badge&logo=fastapi&logoColor=white
[fastapi-url]: https://fastapi.tiangolo.com/
[pydantic.com]: https://img.shields.io/badge/Pydantic-2.6.0-e92063?style=for-the-badge&logo=pydantic&logoColor=white
[pydantic-url]: https://docs.pydantic.dev/latest/
[sqlalchemy.org]: https://img.shields.io/badge/SQLAlchemy-2.0.25-bb0000?color=bb0000&style=for-the-badge
[sqlalchemy-url]: https://docs.sqlalchemy.org/en/20/
[uvicorn.org]: https://img.shields.io/badge/Uvicorn-0.27.0-2094f3?style=for-the-badge&logo=uvicorn&logoColor=white
[uvicorn-url]: https://www.uvicorn.org/
[asyncpg.github.io]: https://img.shields.io/badge/asyncpg-0.29.0-2e6fce?style=for-the-badge&logo=postgresql&logoColor=white
[asyncpg-url]: https://magicstack.github.io/asyncpg/current/
[pytest.org]: https://img.shields.io/badge/pytest-7.4.4-fff?style=for-the-badge&logo=pytest&logoColor=white
[pytest-url]: https://docs.pytest.org/en/6.2.x/
[alembic.sqlalchemy.org]: https://img.shields.io/badge/alembic-1.13.1-6BA81E?style=for-the-badge&logo=alembic&logoColor=white
[alembic-url]: https://alembic.sqlalchemy.org/en/latest/

[rich.readthedocs.io]: https://img.shields.io/badge/rich-13.7.0-009485?style=for-the-badge&logo=rich&logoColor=white
[rich-url]: https://rich.readthedocs.io/en/latest/
[redis.io]: https://img.shields.io/badge/redis-3.5.3-dc382d?style=for-the-badge&logo=redis&logoColor=white
[redis-url]: https://redis.io/
