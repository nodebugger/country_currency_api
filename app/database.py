from sqlmodel import SQLModel, create_engine, Session
from .config import DATABASE_URL

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL must be set in environment")

# DATABASE_URL = "sqlite:///./strings.db"

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
