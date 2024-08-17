from sqlalchemy.orm import Session
from typing import List

from . import models, schemas

def create_result(db:Session, result: schemas.ResultBase, query: schemas.Query):
    db_result = models.Result(**result.model_dump(), query_id=query.id)
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

def create_results(db:Session, results: List[schemas.ResultBase], query: schemas.Query):
    db_results = [models.Result(**result.model_dump(), query_id=query.id) for result in results]
    db.add_all(db_results)
    db.commit()
    for db_result in db_results:
        db.refresh(db_result)
    return db_results

def create_query(db:Session, query: schemas.QueryCreate):
    db_query = models.Query(**query.model_dump())
    db.add(db_query)
    db.commit()
    db.refresh(db_query)
    return db_query


# def get_user(db: Session, user_id: int):
#     return db.query(models.User).filter(models.User.id == user_id).first()


# def get_user_by_email(db: Session, email: str):
#     return db.query(models.User).filter(models.User.email == email).first()


# def get_users(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.User).offset(skip).limit(limit).all()


# def create_user(db: Session, user: schemas.UserCreate):
#     fake_hashed_password = user.password + "notreallyhashed"
#     db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user


# def get_items(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Item).offset(skip).limit(limit).all()


# def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
#     db_item = models.Item(**item.dict(), owner_id=user_id)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item