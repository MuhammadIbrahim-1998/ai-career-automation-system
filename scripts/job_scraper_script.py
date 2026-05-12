import requests
import csv
from pathlib import Path
from datetime import datetime

def fetch_remoteok_jobs():
    url = "https://remoteok.com/api"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Failed to fetch jobs")
        return []

    data = response.json()

    jobs = []

    for job in data[1:]:
        jobs.append({
            "title": job.get("position"),
            "company": job.get("company"),
            "location": job.get("location"),
            "tags": ", ".join(job.get("tags", [])),
            "url": job.get("url"),
            "scraped_at": datetime.utcnow().isoformat()
        })

    return jobs

def save_jobs_to_csv(jobs):
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    csv_file = output_dir / "job_listings.csv"

    with open(csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "title",
                "company",
                "location",
                "tags",
                "url",
                "scraped_at"
            ]
        )

        writer.writeheader()
        writer.writerows(jobs)

    print(f"Saved {len(jobs)} jobs to {csv_file}")

if __name__ == "__main__":
    jobs = fetch_remoteok_jobs()

    if jobs:
        save_jobs_to_csv(jobs)
    else:
        print("No jobs found")