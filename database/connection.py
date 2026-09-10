import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

load_dotenv()

def get_engine() -> Engine:
   

    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB")

    if not all([user, password, database]):
        raise ValueError(
            "Missing PostgreSQL credentials. "
            "Check your .env file."
        )

    connection_url = (
        f"postgresql+psycopg2://"
        f"{user}:{password}@{host}:{port}/{database}"
    )

    return create_engine(connection_url)


def load_to_postgres(df: pd.DataFrame,table_name: str,if_exists: str = "replace") -> None:
    if df.empty:
        raise ValueError(
            f"Cannot load empty DataFrame into '{table_name}'.")

    engine = get_engine()
    try:
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists=if_exists,
            index=False,
            method="multi",
            chunksize=5000
        )

        print(
            f" Loaded {len(df):,} rows "
            f"into PostgreSQL table '{table_name}'"
        )

    finally:
        engine.dispose()