from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app import models

SECRET_KEY = "MYSECRETKEY"
ALGORITHM = "HS256"
bearer_scheme = HTTPBearer(auto_error=False)

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str):
	return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
	return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
	to_encode = data.copy()
	expire = datetime.now(timezone.utc) + timedelta(hours=1)
	to_encode.update({"exp": expire})
	return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
	credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
	db: Session = Depends(get_db),
):
	if credentials is None or credentials.scheme.lower() != "bearer" or not credentials.credentials:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Not authenticated",
			headers={"WWW-Authenticate": "Bearer"},
		)

	try:
		payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
		email = payload.get("sub")
		if not email:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Invalid authentication token",
				headers={"WWW-Authenticate": "Bearer"},
			)
	except JWTError as exc:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid authentication token",
			headers={"WWW-Authenticate": "Bearer"},
		) from exc

	user = db.query(models.User).filter(models.User.email == email).first()
	if user is None:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="User not found",
			headers={"WWW-Authenticate": "Bearer"},
		)
	return user
