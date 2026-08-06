import pandas as pd

jobs_df = pd.read_csv(
    "data/processed/jobs_clean.csv"
)

skills_df = pd.read_csv(
    "data/processed/job_skills.csv"
)

jobs_df["salary_min"] = pd.to_numeric(
    jobs_df["salary_min"],
    errors="coerce"
)

jobs_df["salary_max"] = pd.to_numeric(
    jobs_df["salary_max"],
    errors="coerce"
)

jobs_df["avg_salary"] = (
    jobs_df["salary_min"].fillna(0)
    +
    jobs_df["salary_max"].fillna(0)
) / 2


def answer_question(question):

    q = question.lower()

    # -----------------------------------
    # TOTAL JOBS
    # -----------------------------------

    if "total jobs" in q:

        return f"Total Jobs Available: {len(jobs_df):,}"

    # -----------------------------------
    # TOP COUNTRY
    # -----------------------------------

    elif "top country" in q:

        country = (
            jobs_df["country"]
            .value_counts()
            .idxmax()
        )

        return f"Top Hiring Country: {country}"

    # -----------------------------------
    # TOP SKILL
    # -----------------------------------

    elif "top skill" in q:

        skill = (
            skills_df["skill"]
            .value_counts()
            .idxmax()
        )

        return f"Most In-Demand Skill: {skill}"

    # -----------------------------------
    # TOP COMPANY
    # -----------------------------------

    elif "top company" in q:

        company = (
            jobs_df["company"]
            .value_counts()
            .idxmax()
        )

        return f"Top Hiring Company: {company}"

    # -----------------------------------
    # AVERAGE SALARY
    # -----------------------------------

    elif "average salary" in q:

        avg_salary = (
            jobs_df["avg_salary"]
            .mean()
        )

        return f"Average Salary: €{avg_salary:,.0f}"

    # -----------------------------------
    # HIGHEST PAYING COUNTRY
    # -----------------------------------

    elif "highest paying country" in q:

        country = (
            jobs_df
            .groupby("country")["avg_salary"]
            .mean()
            .idxmax()
        )

        return f"Highest Paying Country: {country}"

    # -----------------------------------
    # DATA ANALYST SALARY
    # -----------------------------------

    elif "data analyst salary" in q:

        analyst_jobs = jobs_df[
            jobs_df["title"]
            .str.contains(
                "data analyst",
                case=False,
                na=False
            )
        ]

        avg_salary = (
            analyst_jobs["avg_salary"]
            .mean()
        )

        return f"Average Data Analyst Salary: €{avg_salary:,.0f}"

    # -----------------------------------
    # VISA JOBS
    # -----------------------------------

    elif "visa" in q:

        visa_jobs = jobs_df[
            jobs_df["description"]
            .str.contains(
                "visa|sponsorship|work permit",
                case=False,
                na=False
            )
        ]

        return f"Visa Related Jobs Found: {len(visa_jobs)}"

    # -----------------------------------
    # TOP 10 SKILLS
    # -----------------------------------

    elif "top skills" in q:

        skills = (
            skills_df["skill"]
            .value_counts()
            .head(10)
        )

        return skills

    else:

        return """
Try asking:

• total jobs
• top country
• top company
• top skill
• average salary
• highest paying country
• visa jobs
• data analyst salary
• top skills
"""