import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import requests


JOB_API_URL = "https://remoteok.com/api"
JOB_OUTPUT_DIR = Path("data/job_descriptions")
SEMANTIC_GATEKEEPER_SCRIPT = Path("scripts/semantic_gatekeeper.py")

MAX_JOBS_TO_SAVE = 10

ALLOWED_TITLE_TERMS = [
    "software engineer",
    "backend engineer",
    "backend developer",
    "python developer",
    "python engineer",
    "ai engineer",
    "ml engineer",
    "machine learning engineer",
    "automation engineer",
    "full stack developer",
    "fullstack developer",
    "api developer",
    ".net developer",
    "dotnet developer",
    "c# developer",
    "asp.net developer",
    "developer",
    "engineer"
]

BLOCKED_TITLE_TERMS = [
    "sales",
    "marketing",
    "seo",
    "customer success",
    "support",
    "director",
    "vice president",
    "vp",
    "manager",
    "advocate",
    "strategist",
    "editor",
    "medical",
    "pricing",
    "business development",
    "account executive",
    "recruiter",
    "hr",
    "finance",
    "legal",
    "content",
    "copywriter"
]

TECH_TERMS = [
    "python",
    "backend",
    "api",
    "fastapi",
    "flask",
    "django",
    ".net",
    "dotnet",
    "c#",
    "asp.net",
    "ai",
    "machine learning",
    "ml",
    "llm",
    "rag",
    "automation",
    "docker",
    "kubernetes",
    "azure",
    "aws",
    "sql",
    "postgresql",
    "mongodb"
]


def safe_filename(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = text.strip("_")
    return text[:90] if text else "remote_job"


def ensure_folders():
    JOB_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def fetch_remoteok_jobs():
    print("[JOB HUNTER] Fetching jobs from RemoteOK API...")

    headers = {
        "User-Agent": "Mozilla/5.0 AI-Career-System/1.0"
    }

    response = requests.get(JOB_API_URL, headers=headers, timeout=30)
    response.raise_for_status()

    data = response.json()

    jobs = []

    for item in data:
        if isinstance(item, dict) and item.get("position"):
            jobs.append(item)

    print(f"[JOB HUNTER] Total jobs fetched: {len(jobs)}")
    return jobs


def get_title(job):
    return str(job.get("position", "")).lower().strip()


def get_full_text(job):
    title = str(job.get("position", "")).lower()
    company = str(job.get("company", "")).lower()
    description = str(job.get("description", "")).lower()

    tags = job.get("tags", [])
    if isinstance(tags, list):
        tags = " ".join(tags).lower()
    else:
        tags = str(tags).lower()

    return f"{title} {company} {description} {tags}"


def is_relevant_job(job):
    title = get_title(job)
    full_text = get_full_text(job)

    for blocked in BLOCKED_TITLE_TERMS:
        if blocked in title:
            return False

    allowed_title_found = any(term in title for term in ALLOWED_TITLE_TERMS)
    if not allowed_title_found:
        return False

    tech_matches = [term for term in TECH_TERMS if term in full_text]

    if len(tech_matches) < 2:
        return False

    return True


def build_job_text(job):
    title = job.get("position", "Unknown Role")
    company = job.get("company", "Unknown Company")
    location = job.get("location", "Remote")
    salary_min = job.get("salary_min", "")
    salary_max = job.get("salary_max", "")
    url = job.get("url", "")
    tags = job.get("tags", [])
    description = job.get("description", "")

    if isinstance(tags, list):
        tags_text = ", ".join(tags)
    else:
        tags_text = str(tags)

    return f"""
Job Title: {title}
Company: {company}
Location: {location}
Salary Min: {salary_min}
Salary Max: {salary_max}
Tags: {tags_text}
Job URL: {url}

Job Description:
{description}
""".strip()


def clear_old_scraped_jobs():
    print("[JOB HUNTER] Cleaning old scraped jobs...")

    for file in JOB_OUTPUT_DIR.glob("*.txt"):
        file.unlink(missing_ok=True)


def save_jobs(jobs):
    saved_count = 0

    for job in jobs:
        if saved_count >= MAX_JOBS_TO_SAVE:
            break

        if not is_relevant_job(job):
            continue

        title = job.get("position", "remote_job")
        company = job.get("company", "company")

        filename = safe_filename(f"{company}_{title}") + ".txt"
        filepath = JOB_OUTPUT_DIR / filename

        job_text = build_job_text(job)

        with filepath.open("w", encoding="utf-8") as file:
            file.write(job_text)

        saved_count += 1
        print(f"[JOB HUNTER] Saved relevant job {saved_count}: {filepath}")

    print(f"[JOB HUNTER] Relevant jobs saved: {saved_count}")
    return saved_count


def trigger_semantic_gatekeeper():
    if not SEMANTIC_GATEKEEPER_SCRIPT.exists():
        print("[JOB HUNTER] semantic_gatekeeper.py not found in scripts folder.")
        return

    print("[JOB HUNTER] Triggering Semantic Gatekeeper...")

    try:
        subprocess.run(
            [sys.executable, str(SEMANTIC_GATEKEEPER_SCRIPT)],
            check=True
        )
        print("[JOB HUNTER] Semantic Gatekeeper completed successfully.")
    except subprocess.CalledProcessError as error:
        print(f"[JOB HUNTER] Semantic Gatekeeper failed: {error}")


def main():
    print("=" * 60)
    print("[JOB HUNTER] AI Career Job Hunter Started")
    print(f"[JOB HUNTER] Time: {datetime.now()}")
    print("=" * 60)

    ensure_folders()
    clear_old_scraped_jobs()

    try:
        jobs = fetch_remoteok_jobs()
    except Exception as error:
        print(f"[JOB HUNTER] Failed to fetch jobs: {error}")
        return

    saved_count = save_jobs(jobs)

    if saved_count == 0:
        print("[JOB HUNTER] No relevant jobs saved. Semantic Gatekeeper skipped.")
        return

    trigger_semantic_gatekeeper()


if __name__ == "__main__":
    main()