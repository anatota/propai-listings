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
| PUT | `/listings/{id}` | ✅ | Update listing |
| DELETE | `/listings/{id}` | ✅ | Delete listing |

## Built with AI

### Prompts used
- _to be filled as project progresses_

### Where AI was wrong / needed correction
- _to be filled as project progresses_

### What I learned
- _to be filled as project progresses_