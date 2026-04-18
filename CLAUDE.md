# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the full stack (API + PostgreSQL + pgAdmin)
docker compose up --build

# Run tests (uses SQLite, no .env needed)
.venv/bin/pytest tests/

# Run a single test
.venv/bin/pytest tests/test_listings.py::test_create_listing -v

# Run alembic migrations
alembic upgrade head

# Start dev server manually (requires DATABASE_URL)
uvicorn app.main:app --reload
```

## Architecture

FastAPI application for real estate listings, backed by PostgreSQL via SQLAlchemy ORM.

**Request flow:** Router endpoints (`app/routers/`) → Pydantic schemas (`app/schemas.py`) for validation → SQLAlchemy models (`app/models.py`) → PostgreSQL via `get_db()` session dependency (`app/database.py`).

**Models:** `User` has many `Listing` (via `owner_id` FK). Auth endpoints are not yet implemented.

**Schemas** use Pydantic v2 syntax (`ConfigDict(from_attributes=True)`, not `class Config`).

**Database dependency:** `app.database.get_db` is the FastAPI dependency that yields a SQLAlchemy session. Tests override this with `app.dependency_overrides[get_db]` to use a separate SQLite database.

**Alembic migrations** are in `alembic/versions/` but the initial migration is a stub — tables are currently created by SQLAlchemy directly.

## Testing

Tests use an isolated SQLite database (`test.db`), created/dropped per test via the `setup_db` autouse fixture. `tests/conftest.py` sets a dummy `DATABASE_URL` so `app.database` can be imported without a `.env` file. The real database is never touched.

## Docker Services

- **api** — FastAPI on port 8000 (mounts `./app` and `./alembic` for live reload)
- **db** — PostgreSQL 16 on port 5432
- **pgadmin** — pgAdmin on port 5050

Environment variables are defined in `.env` (see `.env.example`).
