import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient


@pytest.fixture()
def client(monkeypatch, tmp_path):
	db_path = tmp_path / "test_task_manager.db"
	monkeypatch.delenv("DATABASE_URL", raising=False)

	for module_name in ["app.main", "app.database", "app.models", "app.auth", "routes.users", "routes.tasks"]:
		sys.modules.pop(module_name, None)

	import app.main as main_module
	import app.database as database_module
	from app.database import Base
	import app.models as models_module

	engine = create_engine(f"sqlite:///{db_path.as_posix()}", connect_args={"check_same_thread": False})
	TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
	database_module.engine = engine
	database_module.SessionLocal = TestingSessionLocal
	main_module.engine = engine
	_ = models_module.User, models_module.Task
	Base.metadata.create_all(bind=engine)

	with TestClient(main_module.app) as test_client:
		yield test_client


def _signup_and_login(client: TestClient):
	client.post(
		"/signup",
		json={"username": "alice", "email": "alice@example.com", "password": "secret123"},
	)
	response = client.post(
		"/login",
		json={"email": "alice@example.com", "password": "secret123"},
	)
	assert response.status_code == 200
	return response.json()["access_token"]


def test_home_endpoint(client):
	response = client.get("/")
	assert response.status_code == 200
	assert response.json() == {"message": "Task API Running"}


def test_signup_login_and_task_ownership(client):
	token = _signup_and_login(client)
	headers = {"Authorization": f"Bearer {token}"}

	create_response = client.post(
		"/tasks",
		headers=headers,
		json={"title": "Write docs", "priority": "high"},
	)
	assert create_response.status_code == 200
	created_task = create_response.json()
	assert created_task["owner_id"] == 1
	assert created_task["title"] == "Write docs"

	list_response = client.get("/tasks", headers=headers)
	assert list_response.status_code == 200
	assert len(list_response.json()) == 1

	search_response = client.get("/search", headers=headers, params={"priority": "high"})
	assert search_response.status_code == 200
	assert len(search_response.json()) == 1


def test_task_endpoints_require_auth(client):
	response = client.get("/tasks")
	assert response.status_code == 401