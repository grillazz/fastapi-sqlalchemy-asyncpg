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
        <li><a href="#setup-local-env-with-uv">Setup local development with uv</a></li>
        <li><a href="#import-xlsx-files-with-polars-and-calamine">Import xlsx files with polars and calamine</a></li>
        <li><a href="#worker-aware-async-scheduler">Schedule jobs</a></li>
        <li><a href="#smtp-setup">Email Configuration</a></li>
        <li><a href="#uv-knowledge-and-inspirations">UV knowledge and inspirations</a></li> 
        <li><a href="#large-language-model">Integration with local LLM</a></li>  
      </ul>
    </li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

[//]: # (TODO: Usage,Roadmap, Contributing, License, Contact)

    
## About The Project

This example demonstrates the seamless integration of [FastAPI](https://fastapi.tiangolo.com/), a modern, high-performance web framework,
with [Pydantic 2.0](https://github.com/pydantic/pydantic), a robust and powerful data validation library.
The integration is further enhanced by the use of [SQLAlchemy ORM](https://www.sqlalchemy.org/), a popular and feature-rich Object-Relational Mapping tool,
and [PostgreSQL17](https://www.postgresql.org/docs/17/release.html) relational database.

The entire stack is connected using the [asyncpg](https://github.com/MagicStack/asyncpg) Database Client Library,
which provides a robust and efficient way to interact with PostgreSQL databases in Python,
leveraging the power of asyncio and event loops.

Notably, this example showcases the latest and greatest versions of SQLAlchemy and psycopg,
which are renowned for their robustness, power, and speed. The inclusion of FastAPI adds a modern, fast, and high-performance web framework to the mix
allowing for the rapid development of APIs with Python 3.8+.

FastAPI has received significant recognition in the industry, including a review on thoughtworks Technology Radar in April 2021,
where it was classified as a Trial technology, with comments praising its performance, ease of use,
and features such as API documentation using OpenAPI. Additionally, FastAPI was recognized in the Python Developers Survey 2023 Results,
conducted by the Python Software Foundation and JetBrains, where it was reported that 1 in 4 Python developers use FastAPI,
with a 4 percentage point increase from the previous year.


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
2. make docker-up > alternatively > make docker-up-granian
3. make docker-apply-db-migrations
4. make docker-feed-database
```

### Adjust make with just
[//]: # (TODO: switch form make to just)
<p align="right">(<a href="#readme-top">back to top</a>)</p>

### How to feed database

It took me a while to find nice data set. Hope works of Shakespeare as example will be able to cover 
first part with read only declarative base configuration and all type of funny selects :)
Data set is coming form https://github.com/catherinedevlin/opensourceshakespeare
Next models were generated with https://github.com/agronholm/sqlacodegen

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Rainbow logs with rich :rainbow:

To enhance the developer experience when viewing logs with extensive information from multiple emitters 
(which are particularly useful during development), this project uses the [rich](https://github.com/Textualize/rich) library.
Event with the superpowers of [rich](https://github.com/Textualize/rich), reading logs can be challenging.
The [rich](https://github.com/Textualize/rich) library is highly beneficial, but integrating it properly as a logger object
and maintaining it as a singleton took some effort.

To address the following needs:
- Difficulty in finding specific information in logs.
- Avoiding the complexity of setting up an ELK stack for log management.
- Speeding up the debugging process.

he following steps were taken to integrate [rich](https://github.com/Textualize/rich) into the project:
1. Configure emitters using the [logging-uvicorn.json](https://github.com/grillazz/fastapi-sqlalchemy-asyncpg/blob/main/logging-uvicorn.json)
   or use [logging-granian.json](https://github.com/grillazz/fastapi-sqlalchemy-asyncpg/blob/main/logging-granian.json) for granian
2. Eliminate duplicates, such as SQLAlchemy echo, by using separate handlers.
3. Maintain the logger as a singleton to prevent multiple instances.
4. Add the --log-config ./logging-uvicorn.json parameter to Uvicorn or --log-config ./logging-granian.json to Granian.

![sample-logs-with-rich](/static/logz.png)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Setup User Auth

Setup user authentication with JWT and Redis as token storage.

### Setup local env with uv
```shell
uv sync
source .venv/bin/activate
```

### Import xlsx files with polars and calamine
Power of Polars Library in data manipulation and analysis.
It uses the polars library to read the Excel data into a DataFrame by passing the bytes to the `pl.read_excel()` function -
https://docs.pola.rs/py-polars/html/reference/api/polars.read_excel.html
In `pl.read_excel()` “calamine” engine can be used for reading all major types of Excel Workbook (.xlsx, .xlsb, .xls) and is dramatically faster than the other options, using the fastexcel module to bind calamine.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Worker aware async scheduler
The project uses the APScheduler library to schedule tasks in the background.
The APScheduler library is a powerful and flexible in-process task scheduler with Cron-like capabilities.
It allows you to schedule jobs to run at specific times or intervals, and it supports multiple job stores, triggers, and executors.
The library is designed to be easy to use and highly configurable, making it suitable for a wide range of use cases.
It was added to project in version 4.0.0a5 with Redis as event broker and SQLAlchemy as data store.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### SMTP setup
The project uses the `smtplib` library to send emails.
The `smtplib` library is a built-in Python library that provides a simple interface for sending emails using the Simple Mail Transfer Protocol (SMTP).
It allows you to connect to an SMTP server, send an email message, and disconnect from the server.
The library is easy to use and provides a flexible and powerful way to send emails from your Python applications.

SMTPEmailService provides a reusable interface to send emails via an SMTP server.
This service supports plaintext and HTML emails, and also allows sending template-based emails using the Jinja2 template engine.
It is implemented as a singleton to ensure that only one SMTP connection is maintained
throughout the application lifecycle, optimizing resource usage.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Large Language Model
The `/v1/ml/chat/` endpoint is designed to handle chat-based interactions with the LLM model.
It accepts a user prompt and streams responses back in real-time.
The endpoint leverages FastAPI's asynchronous capabilities to efficiently manage multiple simultaneous requests,
ensuring low latency and high throughput.

FastAPI's async support is particularly beneficial for reducing I/O bottlenecks when connecting to the LLM model.
By using asynchronous HTTP clients like `httpx`,
the application can handle multiple I/O-bound tasks concurrently,
such as sending requests to the LLM server and streaming responses back to the client.
This approach minimizes idle time and optimizes resource utilization, making it ideal for high-performance applications.

Install ollama and run the server
```shell
ollama run llama3.2
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### UV knowledge and inspirations
- https://docs.astral.sh/uv/
- https://hynek.me/articles/docker-uv/
- https://thedataquarry.com/posts/towards-a-unified-python-toolchain/
- https://www.youtube.com/watch?v=ifj-izwXKRA&t=760s > UV and Ruff: Next-gen Python Tooling
- https://www.youtube.com/watch?v=8UuW8o4bHbw&t=1s > uv IS the Future of Python Packaging! 🐍📦


<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Acknowledgments
Use this space to list resources you find helpful and would like to give credit to.
I've included a few of my favorites to kick things off!

* [Open Source Shakespeare Dataset](https://github.com/catherinedevlin/opensourceshakespeare)
* [SQL Code Generator](https://github.com/agronholm/sqlacodegen)
* [Passlib - password hashing library for Python](https://passlib.readthedocs.io/en/stable/)
* [Polars - fast DataFrame library for Rust and Python](https://docs.pola.rs/)
* [Rich - Traceback and logging, made easy](https://rich.readthedocs.io/en/stable/traceback.html)
* [Calamine - Excel reader in Rust](https://github.com/tafia/calamine)
* [Inline Snapshots - pytest plugin for inline snapshots]()
* [Connection pool for asyncpg](https://magicstack.github.io/asyncpg/current/usage.html#connection-pools)
* [Granian - A Rust HTTP server for Python applications](https://github.com/emmett-framework/granian)
* [APScheduler - In-process task scheduler with Cron-like capabilities](https://apscheduler.readthedocs.io/en/master/)
* [Valkey - A simple and fast key-value store](https://github.com/valkey-io/valkey)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Change Log
<details>
  <summary>2025 (3 changes)</summary>
      <ul>
         <li>[MAY 3 2025] add large language model integration :robot:</li>
         <li>[MAR 8 2025] switch from poetry to uv :fast_forward:</li>
         <li>[JAN 28 2025] add SMTP setup :email:</li>
      </ul>
</details>
<details>
  <summary>2024 (6 changes)</summary>
      <ul>
         <li>[DEC 16 2024] bump project to Python 3.13 :fast_forward:</li>
         <li>[OCT 16 2024] apscheduler added to project :clock1:</li>
         <li>[AUG 17 2024] granian use case implemented with docker compose and rich logger :fast_forward:</li>
         <li>[JUN 8 2024] implement asyncpg connection pool :fast_forward:</li>
         <li>[MAR 15 2024] add polars and calamine to project :heart_eyes_cat:</li>
         <li>[FEB 1 2024] bump project to Python 3.12 :fast_forward:</li>
      </ul>
</details>
<details>
  <summary>2023 (7 changes)</summary>
      <ul>
         <li>[OCT 21 2023] refactor shakespeare models to use sqlalchemy 2.0 :fast_forward:</li>
         <li>[SEP 2 2023] add passlib and bcrypt for password hashing :lock: :key:</li>
         <li>[JUL 25 2023] add user authentication with JWT and Redis as token storage :lock: :key:</li>
         <li>[JUL 7 2023] migrate to pydantic 2.0 :fast_forward:</li>
         <li>[APR 28 2023] Rainbow logs with rich :rainbow:</li>
         <li>[APR 10 2023] implement logging with rich</li>
         <li>[FEB 14 2023] bump project to Python 3.11</li>
      </ul>
</details>
<details>
  <summary>2022 (5 changes)</summary>
      <ul>
         <li>[NOV 12 2022] ruff implemented to project as linting tool</li>
         <li>[OCT 3 2022] poetry added to project</li>
         <li>[JUN 6 2022] initial dataset for shakespeare models</li>
         <li>[JUN 4 2022] alembic migrations added to project</li>
         <li>[long time ago...] it was a long time ago in galaxy far far away...</li>
      </ul>
</details>

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

[fastapi.tiangolo.com]: https://img.shields.io/badge/FastAPI-0.115.11-009485?style=for-the-badge&logo=fastapi&logoColor=white
[fastapi-url]: https://fastapi.tiangolo.com/
[pydantic.com]: https://img.shields.io/badge/Pydantic-2.10.6-e92063?style=for-the-badge&logo=pydantic&logoColor=white
[pydantic-url]: https://docs.pydantic.dev/latest/
[sqlalchemy.org]: https://img.shields.io/badge/SQLAlchemy-2.0.38-bb0000?color=bb0000&style=for-the-badge
[sqlalchemy-url]: https://docs.sqlalchemy.org/en/20/
[uvicorn.org]: https://img.shields.io/badge/Uvicorn-0.34.0-2094f3?style=for-the-badge&logo=uvicorn&logoColor=white
[uvicorn-url]: https://www.uvicorn.org/
[asyncpg.github.io]: https://img.shields.io/badge/asyncpg-0.30.0-2e6fce?style=for-the-badge&logo=postgresql&logoColor=white
[asyncpg-url]: https://magicstack.github.io/asyncpg/current/
[pytest.org]: https://img.shields.io/badge/pytest-8.3.5-fff?style=for-the-badge&logo=pytest&logoColor=white
[pytest-url]: https://docs.pytest.org/en/6.2.x/
[alembic.sqlalchemy.org]: https://img.shields.io/badge/alembic-1.15.1-6BA81E?style=for-the-badge&logo=alembic&logoColor=white
[alembic-url]: https://alembic.sqlalchemy.org/en/latest/
[rich.readthedocs.io]: https://img.shields.io/badge/rich-13.9.4-009485?style=for-the-badge&logo=rich&logoColor=white
[rich-url]: https://rich.readthedocs.io/en/latest/
[redis.io]: https://img.shields.io/badge/redis-5.2.1-dc382d?style=for-the-badge&logo=redis&logoColor=white
[redis-url]: https://redis.io/
