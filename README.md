# Code Review Bot

A self-hosted AI code review tool powered by [Ollama](https://ollama.com) and FastAPI. Paste code into the web UI and get streaming feedback on bugs, security, performance, or a plain-English explanation — all running locally.

## Stack

- **FastAPI** — async API, JWT auth middleware, streaming responses
- **Ollama** (`qwen2.5-coder:7b`) — local LLM for code review
- **PostgreSQL** — user accounts
- **Docker Compose** — one-command setup

## Quick start

```bash
cp .env.example .env   # fill in JWT_SECRET at minimum
make build
make start
```

Open [http://localhost:8000](http://localhost:8000), sign up, and start reviewing code.

Interactive API docs at [http://localhost:8000/docs](http://localhost:8000/docs).

## Make commands

```bash
make build      # build images
make start      # docker-compose up
make stop       # docker-compose down
make rebuild    # stop → build → start
make remove     # stop and remove volumes/orphans
make test       # run pytest inside the fast-api container
```

## Running locally without Docker

Point env vars at reachable Postgres and Ollama instances, then:

```bash
pip install -r requirements.txt
python main.py
```

## Environment variables

Copy `.env.example` to `.env`:

| Variable | Default | Notes |
|---|---|---|
| `API_PORT` | `8000` | Host port for the FastAPI service |
| `OLLAMA_HOST` | `http://ollama:11434` | Use `http://localhost:11434` for local dev |
| `OLLAMA_MODEL` | `qwen2.5-coder:7b` | Swap models without code changes |
| `DATABASE_URL` | `postgresql://...@postgres:5432/...` | Full SQLAlchemy connection string |
| `POSTGRES_USER` | `code_review_bot` | Used by the postgres Docker service |
| `POSTGRES_PASSWORD` | `changeme` | Change in production |
| `POSTGRES_DB` | `code_review_bot` | |
| `JWT_SECRET` | *(required)* | Long random string — sign/verify tokens |
| `JWT_EXPIRE_MINUTES` | `60` | Token lifetime |
| `BCRYPT_ROUNDS` | `12` | Password hashing cost |

## API

### Auth

| Method | Path | Description |
|---|---|---|
| `POST` | `/users` | Sign up — `{first_name, last_name, email, password}` |
| `POST` | `/login` | Get JWT — `{email, password}` → `{access_token, token_type}` |

Pass the token on protected endpoints:
```
Authorization: Bearer <token>
```

### LLM endpoints (require auth)

| Method | Path | Description |
|---|---|---|
| `POST` | `/review` | Stream a code review — `{code, language?, mode?}` |
| `POST` | `/stream` | Stream a raw chat response — `{query}` |
| `POST` | `/chat` | Full (non-streaming) chat response — `{query}` |

**Review modes:** `full` (default) · `security` · `performance` · `explain`

## Architecture

```
main.py                              # entrypoint — reads API_PORT, starts uvicorn
application/
  app.py                             # FastAPI app: middleware, routers, startup, handlers
  logger.py                          # shared logger
  models/schemas.py                  # Pydantic models
  static/
    index.html                       # review UI
    login.html                       # login form
    signup.html                      # signup form
auth/
  apis.py                            # POST /login
  backend.py                         # JWTAuthBackend (Starlette AuthenticationMiddleware)
  dependencies.py                    # require_authenticated_user dependency
  jwt.py                             # create_access_token / decode_access_token
  passwords.py                       # hash_password / verify_password (bcrypt)
database/
  db.py                              # SQLAlchemy engine, SessionLocal, Base, get_db
users/
  models.py                          # User ORM model
  apis.py                            # POST /users
compose/Dockerfile                   # python:3.11-slim, hot-reload via uvicorn --reload
docker-compose.yml                   # fast-api + postgres + ollama + ollama-init
```
