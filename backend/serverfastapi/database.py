# database.py
from sqlalchemy.orm import sessionmaker
from lamatidb.interfaces.database_interfaces.database_interface import DatabaseInterface

# Initialize MySQL interface and set up the database
mysql_interface = DatabaseInterface(force_recreate_db=True)
mysql_interface.setup_database()

# Create engine, session, and base
engine = mysql_interface.engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Dependency for FastAPI to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
