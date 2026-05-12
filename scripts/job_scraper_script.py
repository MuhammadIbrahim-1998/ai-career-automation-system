import csv
from datetime import datetime
from pathlib import Path

JOBS = [
    {
        "title": "AI Backend Developer",
        "company": "Demo Company",
        "location": "Remote",
        "skills": "Python, APIs, LLMs, GitHub Actions",
        "source": "Demo Data"
    },
    {
        "title": ".NET AI Automation Engineer",
        "company": "Demo Tech",
        "location": "Remote",
        "skills": "C#, ASP.NET Core, Python, Automation",
        "source": "Demo Data"
    }
]

def save_jobs():
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    file_path = output_dir / "job_listings.csv"

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["title", "company", "location", "skills", "source", "scraped_at"]
        )
        writer.writeheader()

        for job in JOBS:
            job["scraped_at"] = datetime.utcnow().isoformat()
            writer.writerow(job)

    print(f"Saved {len(JOBS)} jobs to {file_path}")

if __name__ == "__main__":
    save_jobs()