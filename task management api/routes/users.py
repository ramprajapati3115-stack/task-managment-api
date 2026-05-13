from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import create_access_token, hash_password, verify_password
from app import models, schemas
from app.database import get_db


router = APIRouter(tags=["users"])


@router.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
	existing_user = (
		db.query(models.User)
		.filter((models.User.email == user.email) | (models.User.username == user.username))
		.first()
	)
	if existing_user:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail="Username or email already registered",
		)

	new_user = models.User(
		username=user.username,
		email=user.email,
		hashed_password=hash_password(user.password),
	)
	db.add(new_user)
	db.commit()
	db.refresh(new_user)
	return {"message": "User created successfully"}


@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
	db_user = db.query(models.User).filter(models.User.email == user.email).first()
	if not db_user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")

	if not verify_password(user.password, db_user.hashed_password):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid password",
			headers={"WWW-Authenticate": "Bearer"},
		)

	token = create_access_token({"sub": db_user.email})
	return {"access_token": token, "token_type": "bearer"}
