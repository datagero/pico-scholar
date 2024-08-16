from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/projects/{project_id}/search/")
def create_query_and_search(project_id: int, query: schemas.QueryCreate, db: Session = Depends(get_db)):
    db_query = crud.create_query(db, query=query)
    # TODO vectorize query and retrieve results
    result1 = schemas.ResultBase(
        source_id = 55,
        similarity = .71,
        authors = "Albert and Ryan",
        year = 1992,
        title = "A Very Good Paper About Papers",
        abstract = "BLA BLA BLA BLA BLA",
        pico_p = "P Bla Bla",
        pico_i = "I Bla Bla",
        pico_c = "C Bla Bla",
        pico_o = "O Bla Bla",
        funnel_stage = models.FunnelEnum.IDENTIFIED,
        is_reviewed = False
    )
    result2 = schemas.ResultBase(
        source_id = 56,
        similarity = .33,
        authors = "DB and Ryan",
        year = 1994,
        title = "Readme and find out",
        abstract = "BLA BLA BLA BLA BLA",
        pico_p = "P Bla Bla",
        pico_i = "I Bla Bla",
        pico_c = "C Bla Bla",
        pico_o = "O Bla Bla",
        funnel_stage = models.FunnelEnum.IDENTIFIED,
        is_reviewed = False
    )
    print(db_query)
    db_results = crud.create_results(db, [result1,result2],db_query)

    return {
        "query": db_query,
        "results": db_results
    }    













# @app.post("/users/", response_model=schemas.User)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_email(db, email=user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     return crud.create_user(db=db, user=user)


# @app.get("/users/", response_model=list[schemas.User])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     users = crud.get_users(db, skip=skip, limit=limit)
#     return users


# @app.get("/users/{user_id}", response_model=schemas.User)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


# @app.post("/users/{user_id}/items/", response_model=schemas.Item)
# def create_item_for_user(
#     user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
# ):
#     return crud.create_user_item(db=db, item=item, user_id=user_id)


# @app.get("/items/", response_model=list[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items