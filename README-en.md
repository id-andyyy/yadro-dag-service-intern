![Art](https://i.postimg.cc/ZKqg75d9/art.png)

![GitHub Created At](https://img.shields.io/github/created-at/id-andyyy/dag-service-api?style=flat&color=1E22AA)
![](https://tokei.rs/b1/github/id-andyyy/dag-service-api?style=flat&category=code&color=A3B43A)
![Top Language](https://img.shields.io/github/languages/top/id-andyyy/dag-service-api?style=flat)
![Pet Project](https://img.shields.io/badge/pet-project-8400FF)

# Service for working with a directed acyclic graph (DAG)

A microservice for working with directed acyclic graphs (DAGs) - saving, reading, getting an adjacency list, and so on&nbsp;&#128451;.

## &#128268;&nbsp;API Endpoints

The following endpoints are implemented:

- &#128296;&nbsp;`POST /api/graph/` - create a graph, accepts a graph as a list of vertices and a list of edges (a client error is returned if the requirements are not met)
- &#128301;&nbsp;`GET /api/graph/{graph_id}/` - get a specific graph (an error is returned if such a graph does not exist)
- &#128279;&nbsp;`GET /api/graph/{graph_id}/adjacency_list/` - get a graph as an adjacency list
- &#128260;&nbsp;`GET /api/graph/{graph_id}/reverse_adjacency_list/` - get a transposed graph as an adjacency list
- &#128161;&nbsp;`GET /health/` - service health check

## &#128218;&nbsp;Technologies and Tools

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffffff)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&color=009485&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-%ff2f2e.svg?style=for-the-badge&logo=sqlalchemy&logoColor=white&color=ff2f2e)
![alembic](https://img.shields.io/badge/alembic-%230db7ed.svg?style=for-the-badge&logo=alembic&logoColor=white&color=black)
![Pytest](https://img.shields.io/badge/pytest-%23ffffff.svg?style=for-the-badge&logo=pytest&logoColor=2f9fe3)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

- Python 3.11
- REST API on FastAPI
- PostgreSQL 13 on the production stack and in Docker Compose
- In-memory SQLite in tests
- SQLAlchemy for working with the database
- Alembic for migrations
- Pytest, TestClient, and Monkeypatch for testing
- Docker and Docker Compose

## &#128161;&nbsp;Technical Decisions Made

- Validation and data schema
    - Pydantic v2 + pydantic-settings (description of input/output JSON models)
- ORM and database work
    - SQLAlchemy (Declarative Base + `Mapped`/`mapped_column`)
    - When a vertex is deleted, the corresponding edges are cascaded
    - `bulk_save_objects` + `flush()` + `commit()` (optimized bulk insertion of vertices and edges, minimizing the number of round-trips to the database)
- Schema migrations
    - Alembic (provides the ability to scale the database without losing existing data)
    - In Docker, `alembic upgrade head` is always executed at container startup to keep the data up to date
- Containerization
    - Docker Compose
        - `db` service (Postgres 13 + volume for persistence)
        - `web` service (Healthcheck `pg_isready`, dependency `depends_on: condition: service_healthy`)
    - `.env` file (standard variables `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` for compatibility with the Postgres Docker image)
- Testing
    - >98% code coverage with tests
    - TestClient (for end-to-end API tests without starting an external server)
    - In-memory SQLite (lightweight isolated database to speed up tests)
    - Fixtures with transaction rollback (each `db_session` rolls back changes after the test, maintaining a clean state)
- Error handling
    - Explicit input data checks
    - Global `exception_handler` for IntegrityError
- Layer separation
    - `routers/` - HTTP + validation
    - `crud/` - database operations
    - `utils/` - utility functions

## &#128640;&nbsp;How to run the service

1. Clone the repository and go to the project folder:
    ```
    git clone https://github.com/id-andyyy/dag-service-api.git
    cd dag-service-api 
    ```

2. Create an environment file based on `.env.example`:
    ```
    cp .env.example .env
    ```

3. Start Docker Compose (don't forget to start the Docker daemon beforehand):
    ```
    docker-compose up --build
    ```

4. Check the service's health through the terminal:
    ```
    curl http://0.0.0.0:8080/health
    ```
    
    Expected response:

    ```
    {"status":"ok"}
    ```

    Or through the Swagger UI in your browser:

    ```
    http://127.0.0.1:8080/docs
    ```

## &#129514;&nbsp;How to run tests

1. Create and activate a virtual environment:
    ```
    python -m venv .venv

    source .venv/bin/activate       # On macOS / Linux
    .\.venv\Scripts\Activate.ps1    # On Windows
    ```

2. Install the dependencies:
    ```
    pip install -r requirements.txt
    ```

3. Note that there are tests that check the service's performance under high load. Usually, the execution time of such tests does not exceed 12 seconds. You can run different tests.

    - Run all tests in the project:

        ```
        pytest
        ```

    - Run all tests except those that check high load on the service:
        
        ```
        pytest -m "not load"
        ```

    - Run only the tests that check for high load:
        
        ```
        pytest -m "load"
        ```

    - Run tests and collect code coverage statistics:

        ```
        pytest --cov=app
        ```

    - Run tests with a detailed report for each test:

        ```
        pytest -v
        ```

## &#128221;&nbsp;Project Structure

```
alembic/
│   ├── versions/       # Migration scripts
│   └── env.py          # Alembic configuration

app/
├── crud/               # Database operation functions
├── db/
│   ├── base.py         # Base class for DeclarativeBase
│   ├── deps.py         # Getting db sessions
│   └── session.py      # Engine and SessionLocal setup
├── models/             # Declarative models
├── routers/            # Endpoints and their logic
├── schemas/            # Request and response models
├── utils/              # Utility functions
├── config.py           # Reading .env
└── main.py             # Creating the application

tests/
├── conftest.py         # Common fixtures
├── test_api.py         # API tests via TestClient
├── test_crud.py        # Unit tests for crud functions
└── test_utils.py       # Unit tests for utility functions

.dockerignore           # Files ignored by Docker
.env                    # Local environment variables
.env.example            # Example of .env contents
.gitignore              # Files ignored by Git
alembic.ini             # Alembic configuration
docker-compose.yaml     # Description of Docker services
Dockerfile              # Docker image build instructions
entrypoint.sh           # Script to start the web container
pytest.ini              # Pytest configuration
requirements.txt        # List of dependencies
```

## Feedback

I would be grateful if you would give a star&nbsp;&#11088;. If you find a bug or have suggestions for improvement, use the [Issues](https://github.com/id-andyyy/dag-service-api/issues) section.

Читать на [русском&nbsp;&#127479;&#127482;](README.md)