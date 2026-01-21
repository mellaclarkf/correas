from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

USER = 'Fernando'
PASSWORD = 'vision2025.'
HOST = '127.0.0.1'
DATABASE = 'vision'
PORT = 3307

DATABASE_URL = (
    f"mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
    "?use_pure=True&charset=utf8mb4"
)

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args={
        "use_unicode": True,
        "charset": "utf8mb4"
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
