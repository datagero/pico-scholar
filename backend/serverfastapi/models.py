# models.py
import random
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Enum, TEXT
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from . import schemas


Base = declarative_base()

class Query(Base):
    __tablename__ = 'query'
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(String(255), nullable=False)

    results = relationship("Result", back_populates="query")

class Result(Base):
    __tablename__ = 'result'
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey('query.id'), nullable=False)
    source_id = Column(Integer, nullable=False)
    similarity = Column(Float, nullable=False)
    authors = Column(TEXT)
    year = Column(Integer)
    title = Column(TEXT)
    abstract = Column(LONGTEXT)
    pico_p = Column(TEXT)
    pico_i = Column(TEXT)
    pico_c = Column(TEXT)
    pico_o = Column(TEXT)
    funnel_stage = Column(TEXT, nullable=False)
    is_archived = Column(Boolean, default=False)
    has_pdf = Column(Boolean, default=False)

    query = relationship("Query", back_populates="results")


# crud.py
from sqlalchemy.orm import Session
from typing import List

class crud:

    def create_result(db: Session, result: schemas.ResultBase, query: schemas.Query):
        db_result = Result(**result.model_dump(), query_id=query.id)
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        return db_result

    def create_results(db: Session, source_nodes, query: schemas.Query):

        results = [
            schemas.ResultBase(
                source_id = source_node.metadata['source'],
                similarity = source_node.score,
                authors = source_node.metadata['authors'],
                year = source_node.metadata['year'],
                title = source_node.metadata['title'],
                abstract = source_node.text,
                pico_p = source_node.metadata['pico_p'],
                pico_i = source_node.metadata['pico_i'],
                pico_c = source_node.metadata['pico_c'],
                pico_o = source_node.metadata['pico_o'],
                funnel_stage = "Identified",
                is_archived = False,
                has_pdf = source_node.metadata['has_pdf']
            )
            for source_node in source_nodes
        ]

        # tmp dict representation of the results -- just first 10
        results_str = [
            {
                'source_id': source_node.metadata['source'],
                'similarity': source_node.score,
                'authors': source_node.metadata['authors'],
                'year': source_node.metadata['year'],
                'title': source_node.metadata['title'],
                'abstract': source_node.text,
                'pico_p': source_node.metadata['pico_p'],
                'pico_i': source_node.metadata['pico_i'],
                'pico_c': source_node.metadata['pico_c'],
                'pico_o': source_node.metadata['pico_o'],
                'funnel_stage': "Identified",
                'is_archived': False,
                'has_pdf': source_node.metadata['has_pdf']
            }
            for source_node in source_nodes[:10]
        ]

        db_results = [Result(**result.model_dump(), query_id=query.id) for result in results]
        db.add_all(db_results)
        db.commit()
        for db_result in db_results:
            db.refresh(db_result)

        return results_str

    def create_query(db: Session, query: schemas.QueryCreate):
        db_query = Query(**query.model_dump())
        db.add(db_query)
        db.commit()
        db.refresh(db_query)
        return db_query
