import os
import sys

# Use the same Python interpreter to run all steps
python = sys.executable

os.system(f'"{python}" src/ingestion/fetch_jobs.py')
os.system(f'"{python}" src/ingestion/cleaning/clean_jobs.py')
os.system(f'"{python}" database/load_jobs.py')

print("Pipeline Complete")