import csv
import os
from pathlib import Path

RESULTS_FILE = Path("data/semantic_job_results.csv")
TRACKER_FILE = Path("data/application_tracker.csv")
TAILORED_RESUMES_FOLDER = Path("data/tailored_resumes")
COVER_LETTERS_FOLDER = Path("data/cover_letters")

ALLOWED_STATUSES = ["HIGH MATCH", "MEDIUM MATCH"]


def get_output_paths(job_filename):
    job_stem = Path(job_filename).stem

    tailored_resume_path = TAILORED_RESUMES_FOLDER / f"{job_stem}_tailored_summary.txt"
    cover_letter_path = COVER_LETTERS_FOLDER / f"{job_stem}_cover_letter.txt"

    return tailored_resume_path, cover_letter_path


def read_selected_jobs():
    selected_jobs = []

    if not RESULTS_FILE.exists():
        print(f"[TRACKER] Results file not found: {RESULTS_FILE}")
        return selected_jobs

    with RESULTS_FILE.open("r", encoding="utf-8", newline="") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            status = row.get("Status", "").strip().upper()

            if status in ALLOWED_STATUSES:
                selected_jobs.append(row)

    return selected_jobs


def build_application_tracker():
    selected_jobs = read_selected_jobs()

    TRACKER_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "Job",
        "Match Status",
        "Similarity Score",
        "Tailored Resume Path",
        "Tailored Resume Exists",
        "Cover Letter Path",
        "Cover Letter Exists",
        "Apply Status",
        "Notes"
    ]

    with TRACKER_FILE.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for job in selected_jobs:
            job_filename = job.get("Job", "").strip()
            status = job.get("Status", "").strip()
            score = job.get("Similarity Score", "").strip()

            tailored_resume_path, cover_letter_path = get_output_paths(job_filename)

            writer.writerow({
                "Job": job_filename,
                "Match Status": status,
                "Similarity Score": score,
                "Tailored Resume Path": str(tailored_resume_path),
                "Tailored Resume Exists": "YES" if tailored_resume_path.exists() else "NO",
                "Cover Letter Path": str(cover_letter_path),
                "Cover Letter Exists": "YES" if cover_letter_path.exists() else "NO",
                "Apply Status": "NOT APPLIED",
                "Notes": ""
            })

    print(f"[TRACKER] Application tracker created: {TRACKER_FILE}")
    print(f"[TRACKER] Jobs tracked: {len(selected_jobs)}")


def main():
    build_application_tracker()


if __name__ == "__main__":
    main()