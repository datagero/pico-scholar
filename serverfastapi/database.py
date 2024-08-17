import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# DATABASE_URI = "sqlite:///./sql_app.db"
# DATABASE_URI = "postgresql://user:password@postgresserver/db"
MYSQL_ROOT_PASSWORD=os.environ['MYSQL_ROOT_PASSWORD']
DATABASE_URI = f'mysql+pymysql://root:{MYSQL_ROOT_PASSWORD}@127.0.0.1:3306/docker_test'

engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
