# PropAI Listings API

A property listings REST API built with FastAPI, PostgreSQL, and Docker Compose.

## Tech Stack

- FastAPI
- PostgreSQL 16
- SQLAlchemy + Alembic
- Docker Compose
- Python 3.12

## Getting Started

### Prerequisites
- Docker
- Docker Compose

### Run locally

```bash
git clone https://github.com/anatota/propai-listings
cd propai-listings
cp .env.example .env
# fill in .env values
docker compose up --build
```

API: http://localhost:8000  
Docs: http://localhost:8000/docs  
pgAdmin: http://localhost:5050

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | ❌ | Health check |
| POST | `/auth/register` | ❌ | Register user |
| POST | `/auth/token` | ❌ | Login |
| GET | `/listings` | ❌ | List all listings |
| POST | `/listings` | ✅ | Create listing |
| GET | `/listings/{id}` | ❌ | Get listing |
| PATCH | `/listings/{id}` | ✅ | Partial update |
| DELETE | `/listings/{id}` | ✅ | Delete listing |

## Built with AI

---

### Day 1 — Foundation
**Tools: Claude (web), GitHub Copilot, Codex**

**How I worked:**

I used AI as a mentor throughout — not just to generate code, but to explain every decision as it was made. Before writing a single line, I asked Claude to help design the data model and project structure so I understood what I was building and why. The boilerplate prompt came from that conversation and was run via Codex. I then asked the Codex agent to check for errors and fix them. Whenever I didn't understand an error or a terminal command, I used inline chat in order to explain the underlying concepts.

Every unfamiliar concept got questioned in real time — how Docker networking works inside Compose, why `DATABASE_URL` uses the service name `db` instead of `localhost`, what the correct build order is and why. This wasn't passive generation — it was deliberate use of AI to compress the feedback loop on concepts that would otherwise take days to encounter organically.

One concrete example of this thinking: when setting up Docker, I asked specifically about running commands without `sudo` — a Linux permissions question that most tutorials skip. That led to understanding how Docker group membership works on Ubuntu, which is the kind of systems-level detail that matters in a real environment.

**Engineering decisions:**

- Chose to run everything in Docker (API + Postgres + pgAdmin) rather than running FastAPI locally — consistent environment from day one, no "works on my machine" problems
- Included pgAdmin for DB visibility during development — being able to inspect the actual tables while building the API layer made debugging faster
- Database-first build order: models → migrations → API. The API imports models at startup; building it in the wrong order means you can't run anything

**Where AI went wrong / what I corrected:**

- Alembic was set up correctly by the agent but not explained. I noticed I didn't understand what had been done and asked for a breakdown before moving on — migration tools, why they exist, what `--autogenerate` actually does

**What I learned:**

- `depends_on` with a healthcheck prevents the API container from starting before Postgres is actually ready — without it, you get connection errors on startup because Docker starts containers in parallel
- `DATABASE_URL` inside Docker uses the Compose service name as the hostname, not `localhost` — `localhost` inside a container refers to the container itself
- Alembic tracks schema changes the same way Git tracks code changes. `--autogenerate` compares your models to the actual DB state and generates a migration file. You still review and run it manually
- Migration tools exist because in production you can't just `DROP TABLE` and recreate — you need to evolve the schema safely without data loss

---

### Day 2 — Core CRUD
**Tools: Claude Code (agent), Claude (web)**

**How I worked:**

Day 2 was more focused. I had a working foundation and a clear prompt. Used Claude Code as the primary agent with a structured prompt specifying exact files, Pydantic version, and test constraints. Used Claude web to understand what was generated — particularly the testing layer, which was new territory.

**Engineering decisions:**

- Kept `PATCH` instead of `PUT` after understanding the difference: PUT replaces the entire resource, PATCH updates only the fields provided. Partial update is the correct behavior for an edit endpoint
- Constrained the agent explicitly: do not touch `models.py` or `database.py` — separation of concerns, those were already correct
- Required the agent to use Pydantic v2 syntax explicitly — without that constraint it would have generated v1, which still runs but is deprecated

**Where AI went wrong / what I corrected:**

- Generated `PATCH` instead of the `PUT` specified in the plan — correct call semantically, but an undiscussed deviation. Kept it deliberately after understanding why
- Tests use SQLite instead of Postgres. SQLite doesn't enforce foreign keys by default and doesn't support Postgres-specific types — tests pass but don't fully reflect production behavior. Acceptable for this project (though I challenged Claude if this was the right decision 😄)
- First test run failed because `DATABASE_URL` isn't set in the test environment. `app.database` reads it at import time, so pytest crashed before running a single test. Agent self-diagnosed and added `conftest.py` to set a dummy value before imports run
- `POST /listings` currently requires `owner_id` in the request body — correct behavior would be extracting it from a JWT token. Deferred to Day 3, requires a manually seeded user in the DB to test

**What I learned:**

- PUT vs PATCH: PUT is a full replacement (send all fields), PATCH is a partial update (send only what changes). Most edit endpoints should be PATCH
- Pydantic schemas are the contract between the API and the outside world — they define what shape data must arrive in, validate types before anything touches the DB, and control what shape data leaves in the response. `Base → Create → Update → Response` is a clean separation of those concerns
- `conftest.py` is pytest's auto-loaded configuration file — anything defined there is available to all tests without importing. It runs before test collection, which is why it's the right place to set env vars that need to exist before imports happen
- FastAPI's `dependency_overrides` replaces the real DB with a test DB by swapping the `get_db` function at runtime — the endpoints don't know anything changed, which is what makes it a proper test isolation pattern
- The 11 tests cover: create (happy path, minimal fields, missing required), read (single, not found, list, pagination), update (partial update, not found), delete (success + verify gone, not found)
- Foreign key constraints are enforced by Postgres at the DB level — the 500 error on POST wasn't a code bug, it was the database correctly rejecting a listing pointing to a non-existent user