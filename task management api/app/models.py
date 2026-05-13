from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	username = Column(String, unique=True, nullable=False)
	email = Column(String, unique=True, nullable=False)
	hashed_password = Column(String, nullable=False)

	tasks = relationship("Task", back_populates="owner")


class Task(Base):
	__tablename__ = "tasks"

	id = Column(Integer, primary_key=True, index=True)
	title = Column(String, nullable=False)
	description = Column(String)
	priority = Column(String)
	due_date = Column(DateTime)
	completed = Column(Boolean, default=False, nullable=False)
	owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

	owner = relationship("User", back_populates="tasks")
