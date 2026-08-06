from queries import load_jobs

df = load_jobs()

print(df.head())

print("\nRows:", len(df))