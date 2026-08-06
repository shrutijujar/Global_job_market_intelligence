import pandas as pd
import os

df = pd.read_csv("data/processed/jobs_clean.csv")

skills = [
    "Python",
    "SQL",
    "Power BI",
    "Tableau",
    "Excel",

    "Azure",
    "AWS",
    "Google Cloud",
    "Databricks",
    "Snowflake",

    "Spark",
    "Hadoop",
    "Kafka",

    "Machine Learning",
    "Deep Learning",
    "AI",
    "GenAI",
    "LLM",

    "Pandas",
    "NumPy",
    "Scikit-Learn",
    "TensorFlow",
    "PyTorch",

    "ETL",
    "Airflow",
    "Docker",
    "Kubernetes",
    "Git",

    "PostgreSQL",
    "MySQL",
    "MongoDB",

    "BigQuery",
    "Redshift",

    "Looker",
    "Qlik",
    "Data Analysis",
    "Data Analytics"
]

skill_records = []

for _, row in df.iterrows():

    description = str(row.get("description", "")).lower()

    for skill in skills:

        if skill.lower() in description:

            skill_records.append({
                "job_title": row["title"],
                "skill": skill
            })

skills_df = pd.DataFrame(skill_records)

skills_df.to_csv(
    "data/processed/job_skills.csv",
    index=False
)

print("Skills Extracted:", len(skills_df))
print(skills_df.head())