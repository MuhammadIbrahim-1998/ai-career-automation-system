import os
import re
import csv
import subprocess
import sys
from collections import Counter
from pathlib import Path

RESULTS_FILE = "data/semantic_job_results.csv"
MASTER_PROFILE_FILE = "data/master_profile.txt"
JOB_DESCRIPTIONS_FOLDER = "data/job_descriptions"
TAILORED_RESUMES_FOLDER = "data/tailored_resumes"
COVER_LETTERS_FOLDER = "data/cover_letters"
APPLICATION_TRACKER_SCRIPT = Path("scripts/application_tracker.py")

ALLOWED_STATUSES = ["HIGH MATCH", "MEDIUM MATCH"]


def read_master_profile():
    with open(MASTER_PROFILE_FILE, "r", encoding="utf-8") as file:
        return file.read()


def read_selected_match_jobs():
    selected_jobs = []

    if not os.path.exists(RESULTS_FILE):
        print(f"Results file not found: {RESULTS_FILE}")
        return selected_jobs

    with open(RESULTS_FILE, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            status = row.get("Status", "").strip().upper()

            if status in ALLOWED_STATUSES:
                job_filename = row.get("Job", "").strip()
                score = row.get("Similarity Score", "").strip()

                job_path = os.path.join(JOB_DESCRIPTIONS_FOLDER, job_filename)

                selected_jobs.append({
                    "job_path": job_path,
                    "status": status,
                    "score": score
                })

    return selected_jobs


def extract_keywords(text):
    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.\-]*\b", text.lower())

    stop_words = {
        "the", "and", "or", "to", "of", "in", "for", "with", "a", "an",
        "is", "are", "as", "on", "by", "from", "this", "that", "you",
        "we", "our", "your", "will", "be", "have", "has", "it", "at",
        "their", "they", "them", "can", "may", "about", "into"
    }

    filtered_words = [word for word in words if word not in stop_words]

    return Counter(filtered_words)


def generate_tailored_summary(master_profile, job_description, status, score):
    job_keywords = extract_keywords(job_description)
    profile_lower = master_profile.lower()

    matched_keywords = []

    for keyword, count in job_keywords.most_common(30):
        if keyword in profile_lower:
            matched_keywords.append(keyword)

    summary = "Tailored Resume Summary\n\n"
    summary += f"Match Status: {status}\n"
    summary += f"Similarity Score: {score}\n\n"

    summary += "This profile is aligned with the target role through the following matching areas:\n\n"

    for keyword in matched_keywords[:15]:
        summary += f"- {keyword}\n"

    if not matched_keywords:
        summary += "- Backend development\n- APIs\n- Automation\n- AI workflows\n"

    summary += "\nSuggested Profile Summary:\n\n"
    summary += (
        "Backend and AI Automation Engineer with experience in building REST APIs, "
        "automation workflows, CI/CD pipelines, and AI-powered backend systems. "
        "Skilled in Python, ASP.NET Core, Docker, GitHub Actions, and scalable backend architecture, "
        "with a strong focus on intelligent workflow automation, AI agents, and career intelligence systems."
    )

    return summary


def suggest_resume_improvements(master_profile, job_description):
    job_keywords = extract_keywords(job_description)
    profile_keywords = extract_keywords(master_profile)

    missing_keywords = []

    for keyword, count in job_keywords.most_common(40):
        if keyword not in profile_keywords:
            missing_keywords.append(keyword)

    suggestions = "Resume Improvement Suggestions\n\n"

    for keyword in missing_keywords[:15]:
        suggestions += f"- Add relevant proof or experience for: {keyword}\n"

    return suggestions


def generate_cover_letter(master_profile, job_description, status, score):
    return (
        "Dear Hiring Manager,\n\n"
        f"I am excited to apply for this role. Based on my profile analysis, this opportunity is marked as "
        f"{status} with a similarity score of {score}.\n\n"
        "My background combines backend development, AI automation, REST API development, CI/CD workflows, "
        "and scalable system design. I have worked on backend automation systems, AI-powered workflows, "
        "GitHub Actions pipelines, and intelligent analysis tools.\n\n"
        "I am particularly interested in roles where I can combine backend engineering, automation, "
        "DevOps practices, and AI workflow development to build reliable and useful systems.\n\n"
        "Regards,\n"
        "Muhammad Ibrahim"
    )


def save_outputs(master_profile, selected_jobs):
    os.makedirs(TAILORED_RESUMES_FOLDER, exist_ok=True)
    os.makedirs(COVER_LETTERS_FOLDER, exist_ok=True)

    generated_count = 0

    for job in selected_jobs:
        job_path = job["job_path"]
        status = job["status"]
        score = job["score"]

        if not os.path.exists(job_path):
            print(f"Job file not found: {job_path}")
            continue

        with open(job_path, "r", encoding="utf-8") as file:
            job_description = file.read()

        job_name = os.path.splitext(os.path.basename(job_path))[0]

        tailored_summary = generate_tailored_summary(master_profile, job_description, status, score)
        suggestions = suggest_resume_improvements(master_profile, job_description)
        cover_letter = generate_cover_letter(master_profile, job_description, status, score)

        tailored_resume_path = os.path.join(
            TAILORED_RESUMES_FOLDER,
            f"{job_name}_tailored_summary.txt"
        )

        cover_letter_path = os.path.join(
            COVER_LETTERS_FOLDER,
            f"{job_name}_cover_letter.txt"
        )

        with open(tailored_resume_path, "w", encoding="utf-8") as file:
            file.write(tailored_summary)
            file.write("\n\n")
            file.write(suggestions)

        with open(cover_letter_path, "w", encoding="utf-8") as file:
            file.write(cover_letter)

        generated_count += 1

        print(f"Generated tailored resume: {tailored_resume_path}")
        print(f"Generated cover letter: {cover_letter_path}")

    return generated_count


def trigger_application_tracker():
    if not APPLICATION_TRACKER_SCRIPT.exists():
        print("[TRACKER PIPELINE] application_tracker.py not found in scripts folder.")
        return

    print("[TRACKER PIPELINE] Triggering application_tracker.py...")

    try:
        subprocess.run(
            [sys.executable, str(APPLICATION_TRACKER_SCRIPT)],
            check=True
        )
        print("[TRACKER PIPELINE] Application tracker completed successfully.")
    except subprocess.CalledProcessError as error:
        print(f"[TRACKER PIPELINE] Application tracker failed: {error}")


def main():
    master_profile = read_master_profile()
    selected_jobs = read_selected_match_jobs()

    if not selected_jobs:
        print("No HIGH or MEDIUM MATCH jobs found.")
        return

    print(f"Found {len(selected_jobs)} HIGH/MEDIUM MATCH jobs for tailoring.")

    generated_count = save_outputs(master_profile, selected_jobs)

    print(f"\nResume tailoring complete! Total jobs processed: {generated_count}")

    trigger_application_tracker()


if __name__ == "__main__":
    main()