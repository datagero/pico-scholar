# models.py
import enum
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Enum
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
    authors = Column(String(255))
    year = Column(Integer)
    title = Column(String(255))
    abstract = Column(LONGTEXT)
    pico_p = Column(String(255))
    pico_i = Column(String(255))
    pico_c = Column(String(255))
    pico_o = Column(String(255))
    funnel_stage =Column(Enum(FunnelEnum, name='funnelenum'))
    is_reviewed = Column(Boolean, default=False)

    query = relationship("Query", back_populates="results")
