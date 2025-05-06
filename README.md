![Art](https://i.postimg.cc/d0d9Bqdd/art.png)

![GitHub Created At](https://img.shields.io/github/created-at/id-andyyy/yadro-dag-service-intern?style=flat&color=1E22AA)
![Lines Of Code](https://tokei.rs/b1/github/id-andyyy/yadro-dag-service-intern?style=flat&category=code&color=DBF250&labelColor=black)
![Top Language](https://img.shields.io/github/languages/top/id-andyyy/yadro-dag-service-intern?style=flat)

# Сервис для работы с направленным ациклическим графом (DAG)

Тестовое задание на стажировку [YADRO ИМПУЛЬС&nbsp;&#127775;](https://edu.yadro.com/impulse/). Микросервис для работы с ориентированными ациклическими графами (DAG) — сохранение, чтение, получение списка смежности и так далее.&nbsp;&#128451;

## &#128268;&nbsp;API Endpoints

Реализованы следующие эндпоинты:

- &#128296;&nbsp;`POST /api/graph/` - создать граф, принимает граф в виде списка вершин и списка ребер (при несоблюдении требований возвращается клиентская ошибка)
- &#128301;&nbsp;`GET /api/graph/{graph_id}/` - получить определенный граф (возвращается ошибка, если такого графа не существует)
- &#128279;&nbsp;`GET /api/graph/{graph_id}/adjacency_list/` - получить граф в виде списка смежности 
- &#128260;&nbsp;`GET /api/graph/{graph_id}/reverse_adjacency_list/` - получить транспонированный граф в виде списка смежности
- &#128161;&nbsp;`GET /health/` - проверка работоспособности сервиса

## &#128218;&nbsp;Технологии и инструменты

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffffff)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&color=009485&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-%ff2f2e.svg?style=for-the-badge&logo=sqlalchemy&logoColor=white&color=ff2f2e)
![alembic](https://img.shields.io/badge/alembic-%230db7ed.svg?style=for-the-badge&logo=alembic&logoColor=white&color=black)
![Pytest](https://img.shields.io/badge/pytest-%23ffffff.svg?style=for-the-badge&logo=pytest&logoColor=2f9fe3)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

- REST API на FastAPI
- PostgreSQL на продакшен-стеке и в Docker Compose
- In-memory SQLite в тестах
- SQLAlchemy для работы с базой
- Alembic для миграций
- Pytest, TestClient и Monkeypatch для тестирования

## &#128161;&nbsp;Принятые технические решения

- Валидация и схема данных
    - Pydantic v2 + pydantic-settings (описание входных/выходных JSON-моделей)
- ORM и работа с бд
    - SQLAlchemy 2.0 (Declarative Base + `Mapped`/`mapped_column`)
    - При удалении вершины происходит каскадное удаление соответствующих рёбер
    - `bulk_save_objects` + `flush()` + `commit()` (оптимизированная массовая вставка вершин и рёбер, минимизация количества round-trip к базе)
- Миграции схемы
    - Alembic (предусмотрена возможность масштабирования бд без потери существующих данных)
    - В Docker при старте контейнера всегда выполняется `alembic upgrade head` для поддержки данных в актуальном состоянии
- Контейнеризация
    - Docker Compose
        - Сервис `db` (Postgres 13 + volume для персистентности)
        - Сервис `web` (Healthcheck `pg_isready`, зависимость `depends_on: condition: service_healthy`)
    - `.env` файл (стандартные переменные `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` для совместимости с Docker-образом Postgres)
- Тестирование
    - Покрытие тестами >98% кода
    - TestClient (для end-to-end API-тестов без поднятия внешнего сервера)
    - In-memory SQLite (лёгкая изолированная бд для ускорения тестов)
    - Фикстуры с откатом транзакций (каждая `db_session` откатывает изменения после теста, сохраняя чистоту состояния)
- Обработка ошибок
    - Явные проверки входных данных
    - Глобальный `exception_handler` для IntegrityError
- Разделение слоёв
    - `routers/` - HTTP + валидация
    - `crud/` - операции с бд
    - `utils/` - утилитарные функции

## &#128640;&nbsp;Как запустить сервис

1. Склонируйте репозиторий и перейдите в папку с проектом:
    ```
    git clone https://github.com/id-andyyy/yadro-dag-service-intern.git
    cd yadro-dag-service-intern 
    ```

2. Создайте файл окружения на основе `.env.example`:
    ```
    cp .env.example .env
    ```

3. Запустите Docker Compose (не забудьте предварительно запустить Docker daemon):
    ```
    docker-compose up --build
    ```

4. Проверьте работоспособность через терминал:
    ```
    curl http://0.0.0.0:8080/health
    ```
    
    Предполагаемый ответ:

    ```
    {"status":"ok"}
    ```

    Или через Swagger UI в браузере:

    ```
    http://127.0.0.1:8080/docs
    ```

## 	&#129514;&nbsp;Как запустить тесты

1. Создайте и активируйте виртуальное окружение:
    ```
    python -m venv .venv

    source .venv/bin/activate       # На macOS / Linux
    .\.venv\Scripts\Activate.ps1    # На Windows
    ```

2. Установите зависимости
    ```
    pip install -r requirements.txt
    ```

3. Запустить можно разные тесты:

    - Запуск всех тестов в проекте:

        ```
        pytest
        ```

    - Запуск всех тестов, кроме тех, которые проверяют высокую нагрузку на сервис:
        
        ```
        pytest -m "not load"
        ```

    - Запуск только тех тестов, которые проверяют высокую нагрузку:
        
        ```
        pytest -m "load"
        ```

    - Запуск тестов и сбор статистики покрытия кода:

        ```
        pytest --cov=app
        ```

    - Запуск тестов с подробным отчётом по каждому тесту:

        ```
        pytest -v
        ```

## &#128221;&nbsp;Структура проекта

```
alembic/
│   ├── versions/       # Скрипты миграций
│   └── env.py          # Конфигурация Alembic

app/
├── crud/               # Функции работы с бд
├── db/
│   ├── base.py         # Базовый класс для DeclarativeBase
│   ├── deps.py         # Получение сессий бд
│   └── session.py      # Настройка engine и SessionLocal
├── models/             # Декларативные модели
├── routers/            # Эндпоинты и их логика
├── schemas/            # Модели запросов и ответов
├── utils/              # Утилитарные функции
├── config.py           # Чтение .env
└── main.py             # Создание приложения

tests/
├── conftest.py         # Общие фикстуры
├── test_api.py         # API-тесты через TestClient
├── test_crud.py        # Unit-тесты crud-функций
└── test_utils.py       # Unit-тесты утилитарных функций

.dockerignore           # Файлы, игнорируемые Docker
.env                    # Локальные переменные окружения
.env.example            # Пример содержимого .env
.gitignore              # Файлы, игнорируемые Git
alembic.ini             # Конфигурация Alembic
docker-compose.yaml     # Описание сервисов Docker
Dockerfile              # Инструкция сборки Docker-образа
entrypoint.sh           # Скрипт запуска контейнера web
pytest.ini              # Конфигурация pytest
requirements.txt        # Список зависимостей
```

## Обратная связь

Буду признателен, если вы поставите звезду&nbsp;&#11088;. Если вы нашли баг или у вас есть предложения по улучшению, используйте раздел [Issues](https://github.com/id-andyyy/yadro-dag-service-intern/issues).