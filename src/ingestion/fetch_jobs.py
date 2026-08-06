import requests
import pandas as pd
import os
import sys
import time
from dotenv import load_dotenv
from datetime import datetime

# Fix Windows console encoding for emoji/unicode
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

load_dotenv()

# =========================
# API CREDENTIALS
# =========================

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
JSEARCH_API_KEY = os.getenv("LINKEDIN_RAPIDAPI_KEY")

# =========================
# CONFIGURATION
# =========================

ADZUNA_COUNTRIES = {
    "gb": "United Kingdom",
    "nl": "Netherlands",
    "de": "Germany",
    "fr": "France",
    "be": "Belgium",
    "es": "Spain",
    "it": "Italy",
    "pl": "Poland",
    "at": "Austria",
    "ch": "Switzerland"
}

SEARCH_TERMS = [
    "Data Analyst",
    "Business Intelligence Analyst",
    "Data Scientist",
    "Analytics Engineer",
    "Data Engineer",
    "Machine Learning Engineer"
]

# LinkedIn search queries (title + location pairs)
LINKEDIN_SEARCHES = [
    {"title": "Data Analyst", "location": "United Kingdom"},
    {"title": "Data Analyst", "location": "Germany"},
    {"title": "Data Analyst", "location": "Netherlands"},
    {"title": "Data Scientist", "location": "United Kingdom"},
    {"title": "Data Scientist", "location": "Germany"},
    {"title": "Data Scientist", "location": "France"},
    {"title": "Data Engineer", "location": "United Kingdom"},
    {"title": "Data Engineer", "location": "Germany"},
    {"title": "Data Engineer", "location": "Netherlands"},
    {"title": "Machine Learning Engineer", "location": "United Kingdom"},
    {"title": "Machine Learning Engineer", "location": "Germany"},
    {"title": "Business Intelligence Analyst", "location": "United Kingdom"},
    {"title": "Analytics Engineer", "location": "United Kingdom"},
    {"title": "Analytics Engineer", "location": "Germany"},
]

all_jobs = []


# ============================================================
# SOURCE 1: ADZUNA (Improved — only fresh jobs)
# ============================================================

def fetch_adzuna_jobs():
    """
    Fetch jobs from Adzuna API with max_days_old=7
    to ensure only fresh, active postings with valid URLs.
    """

    print("\n" + "=" * 60)
    print("SOURCE: ADZUNA (Fresh Jobs — Last 7 Days)")
    print("=" * 60)

    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("⚠️  Adzuna credentials not found. Skipping.")
        return

    adzuna_jobs = []

    for country_code, country_name in ADZUNA_COUNTRIES.items():

        print(f"\nCountry: {country_name}")

        for search_term in SEARCH_TERMS:

            print(f"  Searching: {search_term}")

            for page in range(1, 3):

                url = (
                    f"https://api.adzuna.com/v1/api/jobs/"
                    f"{country_code}/search/{page}"
                    f"?app_id={ADZUNA_APP_ID}"
                    f"&app_key={ADZUNA_APP_KEY}"
                    f"&results_per_page=50"
                    f"&what={search_term}"
                    f"&max_days_old=7"
                    f"&sort_by=date"
                )

                try:

                    response = requests.get(
                        url,
                        timeout=30
                    )

                    if response.status_code != 200:

                        print(
                            f"    Error {response.status_code} | "
                            f"Page {page}"
                        )

                        continue

                    data = response.json()

                    for job in data.get("results", []):

                        adzuna_jobs.append({
                            "country": country_name,
                            "search_term": search_term,
                            "title": job.get("title"),
                            "company": job.get(
                                "company", {}
                            ).get("display_name"),
                            "location": job.get(
                                "location", {}
                            ).get("display_name"),
                            "salary_min": job.get(
                                "salary_min"
                            ),
                            "salary_max": job.get(
                                "salary_max"
                            ),
                            "description": job.get(
                                "description"
                            ),
                            "created": job.get("created"),
                            "redirect_url": job.get(
                                "redirect_url"
                            ),
                            "source": "Adzuna"
                        })

                    print(
                        f"    Page {page}: "
                        f"{len(data.get('results', []))} jobs"
                    )

                    time.sleep(0.5)

                except Exception as e:

                    print(
                        f"    Failed: {country_name} | "
                        f"{search_term} | Page {page}"
                    )
                    print(f"    {e}")
                    continue

    all_jobs.extend(adzuna_jobs)

    print(f"\n✅ Adzuna: {len(adzuna_jobs)} jobs collected")


# ============================================================
# SOURCE 2: LINKEDIN (via LinkedIn Job Search API on RapidAPI)
# ============================================================

def fetch_linkedin_jobs():
    """
    Fetch jobs from LinkedIn via the LinkedIn Job Search API
    on RapidAPI. Uses /active-jb endpoint.
    """

    print("\n" + "=" * 60)
    print("SOURCE: LINKEDIN (via RapidAPI)")
    print("=" * 60)

    if (
        not JSEARCH_API_KEY
        or JSEARCH_API_KEY == "your_rapidapi_key_here"
    ):
        print(
            "⚠️  LinkedIn RapidAPI key not configured. "
            "Skipping.\n"
            "   Add LINKEDIN_RAPIDAPI_KEY to .env"
        )
        return

    linkedin_jobs = []

    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": "linkedin-job-search-api.p.rapidapi.com"
    }

    for search in LINKEDIN_SEARCHES:

        title = search["title"]
        location = search["location"]

        print(
            f"\n  Searching: {title} in {location}"
        )

        params = {
            "title": title,
            "location": location,
            "time_frame": "7d"
        }

        try:

            response = requests.get(
                "https://linkedin-job-search-api.p.rapidapi.com/active-jb",
                headers=headers,
                params=params,
                timeout=30
            )

            if response.status_code != 200:

                print(
                    f"    Error {response.status_code}: {response.text[:200]}"
                )

                if response.status_code == 429:
                    print(
                        "    Rate limit reached. "
                        "Stopping LinkedIn fetch."
                    )
                    break

                continue

            data = response.json()

            if isinstance(data, list):
                results = data
            elif isinstance(data, dict):
                results = (
                    data.get("data", [])
                    or data.get("jobs", [])
                    or data.get("results", [])
                )
            else:
                results = []

            for job in results:

                job_title = job.get("title", "")
                company = job.get("organization", "") or job.get("company", "")
                apply_url = job.get("url", "") or job.get("apply_url", "")

                # Location derived
                loc_derived = job.get("locations_derived", [])
                job_location = loc_derived[0] if loc_derived else location

                # Skip if no title or URL
                if not job_title or not apply_url:
                    continue

                # Description / Summary
                description = (
                    job.get("ai_requirements_summary", "")
                    or job.get("ai_core_responsibilities", "")
                    or job.get("org_linkedin_description", "")
                    or job_title
                )
                if description and isinstance(description, str):
                    import re
                    description = re.sub(r'<[^>]+>', '', description)[:500]

                # Salary
                salary_min = job.get("ai_salary_min_value")
                salary_max = job.get("ai_salary_max_value")

                created = job.get("date_posted") or datetime.now().isoformat()

                linkedin_jobs.append({
                    "country": location,
                    "search_term": title,
                    "title": job_title,
                    "company": company,
                    "location": job_location,
                    "salary_min": salary_min,
                    "salary_max": salary_max,
                    "description": description,
                    "created": created,
                    "redirect_url": apply_url,
                    "source": "LinkedIn"
                })

            print(
                f"    Found: {len(results)} jobs"
            )

            time.sleep(1)

        except Exception as e:

            print(
                f"    Failed: {title} in "
                f"{location}"
            )
            print(f"    {e}")
            continue

    all_jobs.extend(linkedin_jobs)

    print(
        f"\n✅ LinkedIn: {len(linkedin_jobs)} "
        f"jobs collected"
    )


# ============================================================
# SOURCE 3: ARBEITNOW (Free, No API Key, EU Jobs)
# ============================================================

def fetch_arbeitnow_jobs():
    """
    Fetch jobs from Arbeitnow — 100% free, no API key needed.
    Aggregates from Greenhouse, Lever, SmartRecruiters, etc.
    Focus on European jobs with direct apply URLs.
    """

    print("\n" + "=" * 60)
    print("SOURCE: ARBEITNOW (Free EU Jobs)")
    print("=" * 60)

    arbeitnow_jobs = []
    page = 1
    max_pages = 5

    while page <= max_pages:

        print(f"\n  Fetching page {page}...")

        try:

            url = (
                f"https://www.arbeitnow.com"
                f"/api/job-board-api"
                f"?page={page}"
            )

            response = requests.get(
                url,
                timeout=30,
                headers={
                    "Accept": "application/json"
                }
            )

            if response.status_code != 200:
                print(
                    f"    Error {response.status_code}"
                )
                break

            data = response.json()
            jobs_data = data.get("data", [])

            if not jobs_data:
                print("    No more jobs found.")
                break

            for job in jobs_data:

                # Filter for relevant roles
                title = job.get("title", "")
                tags = job.get("tags", [])

                title_lower = title.lower()

                # Check if job matches our search terms
                is_relevant = False
                matched_term = "Other"

                for term in SEARCH_TERMS:
                    term_parts = term.lower().split()
                    if any(
                        part in title_lower
                        for part in term_parts
                    ):
                        is_relevant = True
                        matched_term = term
                        break

                # Also check tags
                if not is_relevant:
                    relevant_tags = [
                        "data", "analytics",
                        "machine learning",
                        "business intelligence",
                        "software development",
                        "engineering"
                    ]
                    for tag in tags:
                        if any(
                            rt in tag.lower()
                            for rt in relevant_tags
                        ):
                            is_relevant = True
                            break

                if not is_relevant:
                    continue

                # Parse created timestamp
                created_ts = job.get("created_at", 0)
                if created_ts:
                    try:
                        created = datetime.fromtimestamp(
                            created_ts
                        ).isoformat()
                    except Exception:
                        created = datetime.now().isoformat()
                else:
                    created = datetime.now().isoformat()

                # Clean description (remove HTML)
                description = job.get("description", "")
                # Basic HTML tag removal
                import re
                description = re.sub(
                    r'<[^>]+>', '', description
                )[:500]

                arbeitnow_jobs.append({
                    "country": "Germany",
                    "search_term": matched_term,
                    "title": title,
                    "company": job.get(
                        "company_name", ""
                    ),
                    "location": job.get(
                        "location", ""
                    ),
                    "salary_min": None,
                    "salary_max": None,
                    "description": description,
                    "created": created,
                    "redirect_url": job.get("url", ""),
                    "source": "Arbeitnow"
                })

            print(
                f"    Page {page}: {len(jobs_data)} total, "
                f"matched {sum(1 for j in jobs_data if any(p in j.get('title', '').lower() for p in ['data', 'analyst', 'engineer', 'scientist', 'intelligence', 'machine', 'learning']))} relevant"
            )

            page += 1
            time.sleep(1)

        except Exception as e:

            print(f"    Failed: Page {page}")
            print(f"    {e}")
            break

    all_jobs.extend(arbeitnow_jobs)

    print(
        f"\n✅ Arbeitnow: {len(arbeitnow_jobs)} "
        f"relevant jobs collected"
    )


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("🚀 MULTI-PLATFORM JOB FETCHER")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Fetch from all sources
    fetch_adzuna_jobs()
    fetch_linkedin_jobs()
    fetch_arbeitnow_jobs()

    # Create DataFrame
    df = pd.DataFrame(all_jobs)

    if df.empty:
        print("\n⚠️  No jobs collected from any source!")
    else:
        # Deduplication across platforms
        before_dedup = len(df)

        df = df.drop_duplicates(
            subset=[
                "title",
                "company",
                "location"
            ]
        )

        after_dedup = len(df)
        dupes_removed = before_dedup - after_dedup

        # Remove jobs with empty URLs
        df = df[
            df["redirect_url"].notna()
            & (df["redirect_url"] != "")
        ]

        # Save to CSV
        os.makedirs("data/raw", exist_ok=True)

        df.to_csv(
            "data/raw/jobs_raw.csv",
            index=False
        )

        # Summary
        print("\n" + "=" * 60)
        print("📊 DATA COLLECTION COMPLETE")
        print("=" * 60)
        print(f"  Total Jobs: {len(df):,}")
        print(f"  Duplicates Removed: {dupes_removed:,}")
        print()

        # Source breakdown
        print("  Jobs by Source:")
        for source, count in (
            df["source"].value_counts().items()
        ):
            print(f"    {source}: {count:,}")

        print()

        # Country breakdown
        print("  Jobs by Country (Top 5):")
        for country, count in (
            df["country"]
            .value_counts()
            .head(5)
            .items()
        ):
            print(f"    {country}: {count:,}")

        print("=" * 60)