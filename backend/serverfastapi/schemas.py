import enum
from sqlalchemy import Column, Integer, Float, String, Text, Boolean, Enum
from pydantic import BaseModel
from typing import Union

class FunnelEnum(enum.Enum):
    IDENTIFIED = 'Identified'
    SCREENED = 'Screened'
    SOUGHT = 'Sought Retrieval'
    ASSESSED = 'Assessed Eligibility'
    FINAL = 'Included in Review'

class ResultBase(BaseModel):
    source_id: int
    similarity: float
    authors: str
    year: int
    title: str
    abstract: str
    pico_p: Union[str, None] = None
    pico_i: Union[str, None] = None
    pico_c: Union[str, None] = None
    pico_o: Union[str, None] = None
    funnel_stage: str
    is_archived: bool = False
    has_pdf: bool = False

class Result(ResultBase):
    id: int
    query_id: int 

    class Config:
        orm_mode = True  

class QueryBase(BaseModel):
    query_text: str

class QueryCreate(QueryBase):
    pass

class Query(QueryBase):
    id: int

    class Config:
        orm_mode = True
