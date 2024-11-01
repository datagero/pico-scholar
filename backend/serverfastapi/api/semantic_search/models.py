from sqlalchemy import Column, Integer, String, Float, TEXT, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from serverfastapi.core.db import Base

class Query(Base):
    __tablename__ = 'query'
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False)  # Add project_id here
    query_text = Column(String(255), nullable=False)

    results = relationship("api.semantic_search.models.Result", back_populates="query")

class Result(Base):
    __tablename__ = 'result'
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey('query.id'), nullable=False)
    source_id = Column(Integer, nullable=False)
    similarity = Column(Float, nullable=False)
    authors = Column(TEXT)
    year = Column(Integer)
    title = Column(TEXT)
    abstract = Column(TEXT)
    pico_p = Column(TEXT, nullable=True)
    pico_i = Column(TEXT, nullable=True)
    pico_c = Column(TEXT, nullable=True)
    pico_o = Column(TEXT, nullable=True)
    funnel_stage = Column(TEXT, nullable=False)
    is_archived = Column(Boolean, default=False)
    has_pdf = Column(Boolean, default=False)

    query = relationship("api.semantic_search.models.Query", back_populates="results")

    def to_dict(self):
        return {
            "id": self.id,
            "query_id": self.query_id,
            "source_id": self.source_id,
            "similarity": self.similarity,
            "authors": self.authors,
            "year": self.year,
            "title": self.title,
            "abstract": self.abstract,
            "pico_p": self.pico_p,
            "pico_i": self.pico_i,
            "pico_c": self.pico_c,
            "pico_o": self.pico_o,
            "funnel_stage": self.funnel_stage,
            "is_archived": self.is_archived,
            "has_pdf": self.has_pdf,
        }

class SemanticQuery(Base):
    __tablename__ = 'semantic_query'
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(String(255), nullable=False)
    fields = Column(JSON, nullable=True)  # List of fields
    source_ids = Column(JSON, nullable=True)  # List of source IDs for filtering

    semantic_results = relationship("SemanticResult", back_populates="semantic_query")

class SemanticResult(Base):
    __tablename__ = 'semantic_result'
    id = Column(Integer, primary_key=True, index=True)
    semantic_query_id = Column(Integer, ForeignKey('semantic_query.id'), nullable=False)
    source_ids = Column(JSON, nullable=False)  # Stores list of source_ids as JSON

    semantic_query = relationship("SemanticQuery", back_populates="semantic_results")
