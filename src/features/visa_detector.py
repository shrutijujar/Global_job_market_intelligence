import pandas as pd

df = pd.read_csv(
    "data/processed/jobs_clean.csv"
)

keywords = [
    "visa sponsorship",
    "work permit",
    "relocation",
    "relocation package",
    "visa support",
    "sponsor visa",
    "international applicants"
]

def detect_visa(text):

    text = str(text).lower()

    for keyword in keywords:

        if keyword in text:
            return 1

    return 0

df["visa_flag"] = (
    df["description"]
    .apply(detect_visa)
)

df.to_csv(
    "data/processed/jobs_visa.csv",
    index=False
)

print(
    "Visa Sponsored Jobs:",
    df["visa_flag"].sum()
)