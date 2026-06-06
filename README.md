# Task Manager REST API

A production-ready REST API built with FastAPI, SQLAlchemy (async), and JWT authentication.

## Stack

- **Python 3.11+**
- **FastAPI** — ASGI web framework
- **SQLite** via `aiosqlite` + **SQLAlchemy 2.0** (async)
- **Alembic** — database migrations
- **python-jose** — JWT tokens
- **passlib[bcrypt]** — password hashing
- **Pydantic v2** — request/response validation
- **Uvicorn** — ASGI server

## Project Structure

```
app/
├── main.py               FastAPI app, middleware, router includes
├── database.py           Async SQLAlchemy engine and session factory
├── models.py             SQLAlchemy ORM models (User, Task)
├── schemas.py            Pydantic request/response schemas
├── dependencies.py       get_db and get_current_user FastAPI dependencies
├── routers/
│   ├── auth.py           POST /auth/register, POST /auth/login
│   └── tasks.py          Task CRUD routes (HTTP layer only)
├── services/
│   ├── auth_service.py   User creation, password verify, token issue
│   └── task_service.py   Task business logic + ownership enforcement
└── repositories/
    ├── user_repository.py  DB queries for User
    └── task_repository.py  DB queries for Task
alembic/                  Migration scripts
```

## Setup

### 1. Clone and install dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=sqlite+aiosqlite:///./tasks.db
JWT_SECRET=change-this-to-a-long-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
PORT=8000
```

### 3. Run database migrations

```bash
alembic upgrade head
```

> The app also calls `create_all` on startup as a convenience fallback, but **always run Alembic migrations in production**.

### 4. Start the server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or with the `$PORT` env var:

```bash
PORT=9000 python -m app.main
```

Interactive API docs available at: `http://localhost:8000/docs`

---

## Endpoints

### Health

| Method | Path      | Auth | Description       |
|--------|-----------|------|-------------------|
| GET    | `/health` | No   | Returns `{"status":"ok"}` |

```bash
curl http://localhost:8000/health
```

---

### Auth

#### Register

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com", "password": "secret123"}'
```

**Response 201:**
```json
{"id": 1, "username": "alice", "email": "alice@example.com"}
```

#### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret123"}'
```

**Response 200:**
```json
{"access_token": "<jwt>", "token_type": "bearer"}
```

---

### Tasks (Bearer token required)

Set the token in your shell for convenience:

```bash
TOKEN="<paste access_token here>"
```

#### List all tasks

```bash
curl http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN"
```

#### Create a task

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread", "status": "todo"}'
```

**Response 201:**
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "todo",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00",
  "owner_id": 1
}
```

#### Get a single task

```bash
curl http://localhost:8000/tasks/1 \
  -H "Authorization: Bearer $TOKEN"
```

#### Update a task

```bash
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'
```

#### Delete a task

```bash
curl -X DELETE http://localhost:8000/tasks/1 \
  -H "Authorization: Bearer $TOKEN"
```

**Response 204 No Content**

---

## Task Status Values

| Value        | Meaning       |
|--------------|---------------|
| `todo`       | Not started   |
| `in_progress`| In progress   |
| `done`       | Completed     |

---

## Security Notes

- Passwords are hashed with bcrypt and never returned in any response.
- JWT tokens are stateless and signed with `JWT_SECRET`.
- Ownership is enforced in the service layer — accessing another user's task returns 404.
- Missing or invalid tokens return 401.

---

## Alembic: Creating a New Migration

After modifying `app/models.py`:

```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```
