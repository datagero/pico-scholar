from fastapi import Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

# Centralized metadata and Base class
metadata = MetaData()
Base = declarative_base(metadata=metadata)

# @retry(stop=stop_after_attempt(2), wait=wait_fixed(1), retry=retry_if_exception_type(OperationalError))
def get_db(request: Request):
    """Get a database session from the app state."""
    db = request.app.state.services["SessionLocal"]()
    try:
        yield db
    finally:
        db.close()