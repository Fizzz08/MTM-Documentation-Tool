from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from pathlib import Path
import snowflake.connector
from typing import Generator

# Load .env from root directory
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# Read environment variables
user = os.environ["SNOWFLAKE_USER"]
password = os.environ["SNOWFLAKE_PASSWORD"]
account = os.environ["SNOWFLAKE_ACCOUNT"]
warehouse = os.environ["SNOWFLAKE_WAREHOUSE"]
database = os.environ["SNOWFLAKE_DATABASE"]
schema = os.environ["SNOWFLAKE_SCHEMA"]
role = os.environ["SNOWFLAKE_ROLE"]

# SQLAlchemy engine for ORM
DATABASE_URL = (
    f"snowflake://{user}:{password}@{account}/{database}/{schema}"
    f"?warehouse={warehouse}&role={role}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# Direct Snowflake connector
def get_snowflake_connection():
    return snowflake.connector.connect(
        user=user,
        password=password,
        account=account,
        warehouse=warehouse,
        database=database,
        schema=schema,
        role=role
    )

# Dependency for FastAPI routes
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
