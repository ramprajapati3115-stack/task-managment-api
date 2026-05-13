from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
	username: str
	email: str
	password: str


class UserLogin(BaseModel):
	email: str
	password: str


class Token(BaseModel):
	access_token: str
	token_type: str


class TaskCreate(BaseModel):
	title: str
	description: Optional[str] = None
	priority: Optional[str] = None
	due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
	title: Optional[str] = None
	description: Optional[str] = None
	priority: Optional[str] = None
	due_date: Optional[datetime] = None
	completed: Optional[bool] = None


class TaskResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	title: str
	description: Optional[str] = None
	priority: Optional[str] = None
	due_date: Optional[datetime] = None
	completed: bool
	owner_id: Optional[int] = None
