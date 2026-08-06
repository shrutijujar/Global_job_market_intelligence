import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://postgres:shruti65@localhost:5432/job_market_db"
)

def load_jobs(only_released=True):

    query = """
    SELECT *
    FROM jobs
    """

    if only_released:
        query += " WHERE is_released = TRUE"

    return pd.read_sql(
        query,
        engine
    )