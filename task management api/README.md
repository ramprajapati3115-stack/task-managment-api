# Task Management API

FastAPI + JWT authentication task management backend based on the guide provided.

By default the app boots against a local SQLite database so it can run immediately in a fresh workspace. Set `DATABASE_URL` to a PostgreSQL connection string when you want to use Postgres.

## Run

1. Optionally set `DATABASE_URL` to your PostgreSQL connection string. If you do not set it, the app will use a local SQLite file named `task_manager.db`.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the API:

```bash
uvicorn app.main:app --reload
```

4. Open Swagger UI at `http://127.0.0.1:8000/docs`.

## Sample Requests

Use [requests.http](requests.http) for ready-to-run signup, login, and authorized task requests in VS Code REST Client or as a Postman reference.