from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db


router = APIRouter(tags=["tasks"])


@router.post("/tasks", response_model=schemas.TaskResponse)
def create_task(
	task: schemas.TaskCreate,
	db: Session = Depends(get_db),
	current_user: models.User = Depends(get_current_user),
):
	new_task = models.Task(
		title=task.title,
		description=task.description,
		priority=task.priority,
		due_date=task.due_date,
		owner_id=current_user.id,
	)
	db.add(new_task)
	db.commit()
	db.refresh(new_task)
	return new_task


@router.get("/tasks", response_model=list[schemas.TaskResponse])
def get_tasks(
	skip: int = 0,
	limit: int = 5,
	db: Session = Depends(get_db),
	current_user: models.User = Depends(get_current_user),
):
	tasks = (
		db.query(models.Task)
		.filter(models.Task.owner_id == current_user.id)
		.offset(skip)
		.limit(limit)
		.all()
	)
	return tasks


@router.get("/search", response_model=list[schemas.TaskResponse])
def search_tasks(
	priority: str = Query(..., description="Priority value to filter by"),
	db: Session = Depends(get_db),
	current_user: models.User = Depends(get_current_user),
):
	tasks = (
		db.query(models.Task)
		.filter(models.Task.priority == priority, models.Task.owner_id == current_user.id)
		.all()
	)
	return tasks


@router.put("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(
	task_id: int,
	task: schemas.TaskUpdate,
	db: Session = Depends(get_db),
	current_user: models.User = Depends(get_current_user),
):
	db_task = (
		db.query(models.Task)
		.filter(models.Task.id == task_id, models.Task.owner_id == current_user.id)
		.first()
	)
	if not db_task:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

	update_data = task.model_dump(exclude_unset=True)
	for field, value in update_data.items():
		setattr(db_task, field, value)

	db.commit()
	db.refresh(db_task)
	return db_task


@router.delete("/tasks/{task_id}")
def delete_task(
	task_id: int,
	db: Session = Depends(get_db),
	current_user: models.User = Depends(get_current_user),
):
	task = (
		db.query(models.Task)
		.filter(models.Task.id == task_id, models.Task.owner_id == current_user.id)
		.first()
	)
	if not task:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

	db.delete(task)
	db.commit()
	return {"message": "Task deleted"}
