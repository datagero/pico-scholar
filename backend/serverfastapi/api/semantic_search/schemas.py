# Defines the request and response schemas for the API endpoint, validating the data format.

from pydantic import BaseModel
from typing import Optional, List
import enum

class FunnelEnum(enum.Enum):
    IDENTIFIED = 'Identified'
    SCREENED = 'Screened'
    SOUGHT = 'Sought Retrieval'
    ASSESSED = 'Assessed Eligibility'
    FINAL = 'Included in Review'

class QueryBase(BaseModel):
    query_text: str

class QueryCreate(QueryBase):
    pass

class SemanticQueryCreate(QueryBase):
    fields: Optional[List[str]] = ["All Fields"]
    source_ids: Optional[List[int]] = []

class Query(QueryBase):
    id: int
    results: List['Result'] = []

    class Config:
        orm_mode = True

class ResultBase(BaseModel):
    id: int
    query_id: int
    source_id: int
    similarity: float
    authors: str
    year: Optional[int] = None
    title: str
    abstract: str
    pico_p: Optional[str] = None
    pico_i: Optional[str] = None
    pico_c: Optional[str] = None
    pico_o: Optional[str] = None
    funnel_stage: str
    is_archived: bool = False
    has_pdf: bool = False

class Result(ResultBase):
    id: int
    query_id: int
