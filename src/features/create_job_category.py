import pandas as pd

# Load dataset
df = pd.read_csv("data/processed/jobs_clean.csv")


def get_category(title):

    title = str(title).lower()

    if "data analyst" in title:
        return "Data Analyst"

    elif "business intelligence" in title or "bi" in title:
        return "Business Intelligence"

    elif "data engineer" in title:
        return "Data Engineer"

    elif "data scientist" in title:
        return "Data Scientist"

    elif "machine learning" in title or "ml engineer" in title:
        return "Machine Learning"

    elif "ai" in title:
        return "Artificial Intelligence"

    elif "analytics engineer" in title:
        return "Analytics Engineer"

    elif "software" in title:
        return "Software Engineer"

    elif "cloud" in title:
        return "Cloud Engineer"

    else:
        return "Other"


df["job_category"] = df["title"].apply(get_category)

df.to_csv(
    "data/processed/jobs_clean.csv",
    index=False
)

print(df[["title", "job_category"]].head(20))

print("\n✅ Job categories created successfully.")