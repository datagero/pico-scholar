from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from serverfastapi.core.db import Base

class RAGQuery(Base):
    __tablename__ = 'rag_queries'
    
    id = Column(Integer, primary_key=True, index=True)
    initial_query = Column(String, nullable=False)
    expanded_queries = Column(Text)  # Stores JSON of alternative queries
    
    # Relations
    summaries = relationship("RAGSummary", back_populates="query")
    chats = relationship("RAGChat", back_populates="query")

class RAGSummary(Base):
    __tablename__ = 'rag_summaries'
    
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey('rag_queries.id'), nullable=False)
    document_id = Column(Integer, nullable=False)
    summary = Column(Text, nullable=False)
    
    # Relations
    query = relationship("RAGQuery", back_populates="summaries")

class RAGChat(Base):
    __tablename__ = 'rag_chats'
    
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey('rag_queries.id'), nullable=False)
    document_id = Column(Integer, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)  # The answer can be generated later
    
    # Relations
    query = relationship("RAGQuery", back_populates="chats")
