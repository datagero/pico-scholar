import enum

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Enum
from sqlalchemy.dialects.mysql import MEDIUMTEXT, LONGTEXT
from sqlalchemy.orm import relationship

from .database import Base


class FunnelEnum(enum.Enum):
    IDENTIFIED = 'identified'
    SCREENED = 'screened'
    SOUGHT = 'sought'
    ASSESSED = 'assessed'
    FINAL = 'final'

class Query(Base):
    __tablename__ = 'query'
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(String(255), nullable=False)

    # Relationship to Result (if needed)
    # results = relationship("Result", back_populates="query")

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
    funnel_stage = Column(Enum(FunnelEnum, name='funnelenum'))
    is_reviewed = Column(Boolean, default=False)

    # Relationship back to Query (if needed)
    # query = relationship("Query", back_populates="results")

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)
#     is_active = Column(Boolean, default=True)

#     items = relationship("Item", back_populates="owner")


# class Item(Base):
#     __tablename__ = "items"

#     id = Column(Integer, primary_key=True)
#     title = Column(String, index=True)
#     description = Column(String, index=True)
#     owner_id = Column(Integer, ForeignKey("users.id"))

#     owner = relationship("User", back_populates="items")
