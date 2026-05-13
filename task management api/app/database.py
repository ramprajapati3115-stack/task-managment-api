import os

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./task_manager.db"


def _create_engine(database_url: str):
	if database_url.startswith("sqlite"):
		return create_engine(database_url, connect_args={"check_same_thread": False})
	return create_engine(database_url, pool_pre_ping=True)


engine = _create_engine(DATABASE_URL)

try:
	with engine.connect():
		pass
except OperationalError:
	fallback_url = "sqlite:///./task_manager.db"
	engine = _create_engine(fallback_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()