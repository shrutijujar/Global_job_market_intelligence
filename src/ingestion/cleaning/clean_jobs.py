import pandas as pd
import os
import re

df = pd.read_csv("data/raw/jobs_raw.csv")

print("Original Rows:", len(df))

# Drop full duplicates
df = df.drop_duplicates()

# Drop rows without title
df = df.dropna(subset=["title"])

# Fill missing salary values
df["salary_min"] = df["salary_min"].fillna(0)
df["salary_max"] = df["salary_max"].fillna(0)

# Ensure source column exists
if "source" not in df.columns:
    df["source"] = "Adzuna"

# Fill missing source
df["source"] = df["source"].fillna("Unknown")

# Remove jobs with empty or invalid URLs
df = df[
    df["redirect_url"].notna()
    & (df["redirect_url"].str.strip() != "")
    & (df["redirect_url"].str.startswith("http"))
]

# Cross-platform deduplication
# Keep the first occurrence (prioritize by source reliability)
source_priority = {
    "LinkedIn": 1,
    "Indeed": 2,
    "Glassdoor": 3,
    "Arbeitnow": 4,
    "Adzuna": 5,
    "ZipRecruiter": 6,
    "JSearch": 7,
    "Unknown": 8
}

df["source_priority"] = df["source"].map(
    source_priority
).fillna(9)

df = df.sort_values("source_priority")

df = df.drop_duplicates(
    subset=["title", "company", "location"],
    keep="first"
)

df = df.drop(columns=["source_priority"])

# Clean title (remove HTML entities)
df["title"] = df["title"].apply(
    lambda x: re.sub(r'<[^>]+>', '', str(x))
    if pd.notna(x) else x
)

# Save cleaned data
os.makedirs("data/processed", exist_ok=True)

df.to_csv(
    "data/processed/jobs_clean.csv",
    index=False
)

print("Rows After Cleaning:", len(df))

# Source breakdown
print("\nJobs by Source:")
for source, count in (
    df["source"].value_counts().items()
):
    print(f"  {source}: {count}")

print("Cleaning Complete")