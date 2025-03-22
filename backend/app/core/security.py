from datetime import datetime, timedelta
from typing import Optional, Set
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.db import get_db
from app.models import Users

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm="HS256"
    )
    return encoded_jwt


# Token blacklist for logout functionality
token_blacklist: Set[str] = set()
blacklist_expiry: dict[str, datetime] = {}


def blacklist_token(token: str) -> None:
    """Add token to blacklist with expiration time based on the JWT expiry"""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=["HS256"], 
            options={"verify_signature": True}
        )
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            expiry = datetime.fromtimestamp(exp_timestamp)
            blacklist_expiry[token] = expiry
    except JWTError:
        # If we can't decode the token, blacklist it for 24 hours as a precaution
        blacklist_expiry[token] = datetime.utcnow() + timedelta(hours=24)
    
    token_blacklist.add(token)
    # Clean expired tokens occasionally to prevent memory leaks
    clean_expired_tokens()


def is_token_blacklisted(token: str) -> bool:
    return token in token_blacklist


def clean_expired_tokens() -> None:
    """Remove expired tokens from the blacklist"""
    current_time = datetime.utcnow()
    expired_tokens = [
        token 
        for token, expiry in blacklist_expiry.items() 
        if expiry < current_time
    ]
    
    for token in expired_tokens:
        if token in token_blacklist:
            token_blacklist.remove(token)
        if token in blacklist_expiry:
            del blacklist_expiry[token]


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Users:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Check if token is blacklisted
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(Users).filter(Users.email == email).first()
    if user is None:
        raise credentials_exception
    return user