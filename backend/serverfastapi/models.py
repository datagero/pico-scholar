# models.py
import enum
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Enum, TEXT
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class FunnelEnum(enum.Enum):
    IDENTIFIED = 'Identified'
    SCREENED = 'Screened'
    SOUGHT = 'Sought Retrieval'
    ASSESSED = 'Assessed Eligibility'
    FINAL = 'Included in Review'

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
    funnel_stage =Column(Enum(FunnelEnum, name='funnelenum'))
    is_archived = Column(Boolean, default=False)
    has_pdf = Column(Boolean, default=False)

    query = relationship("Query", back_populates="results")
