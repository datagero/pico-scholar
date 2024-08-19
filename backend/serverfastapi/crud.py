# crud.py
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas

def create_result(db: Session, result: schemas.ResultBase, query: schemas.Query):
    db_result = models.Result(**result.model_dump(), query_id=query.id)
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

def create_results(db: Session, results: List[schemas.ResultBase], query: schemas.Query):
    db_results = [models.Result(**result.model_dump(), query_id=query.id) for result in results]
    db.add_all(db_results)
    db.commit()
    for db_result in db_results:
        db.refresh(db_result)
    return db_results

def create_query(db: Session, query: schemas.QueryCreate):
    db_query = models.Query(**query.model_dump())
    db.add(db_query)
    db.commit()
    db.refresh(db_query)
    return db_query
