from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# MySQL Database URL configuration
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:your_password@localhost:3306/real_time_chat"

# Create SQLAlchemy engine with MySQL-specific configuration
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()