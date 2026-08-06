import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv("data/processed/jobs_clean.csv")

# Make results reproducible
np.random.seed(42)

# Estimate experience based on job title
def estimate_experience(title):

    title = str(title).lower()

    if "intern" in title:
        return np.random.randint(0, 2)

    elif "junior" in title:
        return np.random.randint(1, 3)

    elif "analyst" in title:
        return np.random.randint(1, 5)

    elif "engineer" in title:
        return np.random.randint(2, 6)

    elif "scientist" in title:
        return np.random.randint(2, 7)

    elif "senior" in title:
        return np.random.randint(5, 10)

    elif "lead" in title:
        return np.random.randint(7, 12)

    elif "manager" in title:
        return np.random.randint(8, 15)

    elif "director" in title:
        return np.random.randint(12, 20)

    else:
        return np.random.randint(1, 5)

# Create the new column
df["experience"] = df["title"].apply(estimate_experience)

# Save the updated dataset
df.to_csv(
    "data/processed/jobs_clean.csv",
    index=False
)

print(df[["title", "experience"]].head())

print("\nExperience column added successfully!")