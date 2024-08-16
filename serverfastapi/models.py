import enum

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Enum
from sqlalchemy.orm import relationship

from .database import Base


class FunnelEnum(enum.Enum):
    IDENTIFIED = 'identified'
    SCREENED = 'screened'
    SOUGHT = 'sought'
    ASSESSED = 'assessed'
    FINAL = 'final'

class Query(Base):
    __tablename__ = "query"
    id = Column(Integer, primary_key=True)
    query_text = Column(String, nullable = False)


class Result(Base):
    __tablename__ = "result"

    id = Column(Integer, primary_key=True)
    query_id = Column(Integer, ForeignKey("query.id"))
    source_id = Column(Integer, index=True, nullable=False)
    similarity = Column(Float, nullable=False)
    authors = Column(String)
    year = Column(Integer, index=True)
    title = Column(String, index=True)
    abstract = Column(String)
    pico_p = Column(String)
    pico_i = Column(String)
    pico_c = Column(String)
    pico_o = Column(String)
    funnel_stage = Column(Enum(FunnelEnum))
    is_reviewed = Column(Boolean)

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
