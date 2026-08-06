import os

print("Fetching latest jobs...")

os.system(
    "python src/ingestion/fetch_jobs.py"
)

print("Pipeline Complete")