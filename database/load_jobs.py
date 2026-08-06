import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql://postgres:shruti65@localhost:5432/job_market_db"
)

df = pd.read_csv(
    "data/processed/jobs_clean.csv"
)

df["is_released"] = True

# Ensure source column exists
if "source" not in df.columns:
    df["source"] = "Adzuna"

# ========================================
# Add source column to DB if not exists
# ========================================

with engine.connect() as conn:
    try:
        conn.execute(text(
            "ALTER TABLE jobs "
            "ADD COLUMN IF NOT EXISTS "
            "source VARCHAR(50) DEFAULT 'Adzuna'"
        ))
        conn.commit()
        print("Source column ensured in database.")
    except Exception as e:
        print(f"Column check: {e}")

# ========================================
# Remove old stale jobs, load fresh ones
# ========================================

# Clear existing jobs and load fresh data
# This ensures we don't accumulate stale postings
df.to_sql(
    "jobs",
    engine,
    if_exists="replace",
    index=False
)

print("Jobs Loaded Successfully")
print("Rows:", len(df))

# Source breakdown
print("\nJobs by Source:")
for source, count in (
    df["source"].value_counts().items()
):
    print(f"  {source}: {count}")