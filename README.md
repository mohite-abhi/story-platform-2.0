# Story Publishing Platform

A backend application built while learning Django and backend engineering concepts.

## Tech Stack

- Python
- Django
- PostgreSQL

## Current Features

- Custom User model
- Story model

## Roadmap

- Django Admin
- Authentication
- Django REST Framework
- Testing
- Docker
- Redis
- Celery
- CI/CD
- Deployment

## Create .env file with following keys for configuration

```
SECRET_KEY
DEBUG
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
```
## Running with Docker Compose

### Prerequisites

* Docker
* Docker Compose

### Start the application

From the project root:

```bash
docker compose up --build
```

The Django application will be available at:

```text
http://localhost:8000
```

### Apply migrations

In another terminal:

```bash
docker compose exec django python manage.py migrate
```

### Create a superuser

```bash
docker compose exec django python manage.py createsuperuser
```

### Run tests

```bash
docker compose exec django python manage.py test
```

### Stop the application

```bash
docker compose down
```

This removes the containers but preserves the PostgreSQL data stored in the `postgres_data` Docker volume.

> Do not use `docker compose down -v` unless you intentionally want to delete the PostgreSQL volume and its data.
