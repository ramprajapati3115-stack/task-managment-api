from fastapi import FastAPI

from app.database import Base, engine
from routes.tasks import router as tasks_router
from routes.users import router as users_router


app = FastAPI(title="Task Management API")


@app.on_event("startup")
def on_startup() -> None:
	Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
	return {"message": "Task API Running"}


app.include_router(users_router)
app.include_router(tasks_router)
