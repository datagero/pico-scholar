from pydantic import BaseModel
from . import models

class ResultBase(BaseModel):
    source_id: int
    similarity: float
    authors: str
    year: int
    title: str
    abstract: str
    pico_p: str | None = None
    pico_i: str | None = None
    pico_c: str | None = None
    pico_o: str | None = None
    funnel_stage: models.FunnelEnum
    is_reviewed: bool = False


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

# class ItemBase(BaseModel):
#     title: str
#     description: str | None = None


# class ItemCreate(ItemBase):
#     pass


# class Item(ItemBase):
#     id: int
#     owner_id: int

#     class Config:
#         orm_mode = True


# class UserBase(BaseModel):
#     email: str


# class UserCreate(UserBase):
#     password: str


# class User(UserBase):
#     id: int
#     is_active: bool
#     items: list[Item] = []

#     class Config:
#         orm_mode = True