import os
import re
import csv
from collections import Counter

RESULTS_FILE = "data/semantic_job_results.csv"
MASTER_PROFILE_FILE = "data/master_profile.txt"
JOB_DESCRIPTIONS_FOLDER = "data/job_descriptions"
TAILORED_RESUMES_FOLDER = "data/tailored_resumes"
COVER_LETTERS_FOLDER = "data/cover_letters"


def read_master_profile():
    with open(MASTER_PROFILE_FILE, "r", encoding="utf-8") as file:
        return file.read()


def read_high_match_jobs():
    high_match_jobs = []

    with open(RESULTS_FILE, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            if row["Status"].strip().upper() == "HIGH MATCH":
                job_filename = row["Job"].strip()
                job_path = os.path.join(JOB_DESCRIPTIONS_FOLDER, job_filename)
                high_match_jobs.append(job_path)

    return high_match_jobs


def extract_keywords(text):
    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.\-]*\b", text.lower())

    stop_words = {
        "the", "and", "or", "to", "of", "in", "for", "with", "a", "an",
        "is", "are", "as", "on", "by", "from", "this", "that", "you",
        "we", "our", "your", "will", "be", "have", "has"
    }

    filtered_words = [word for word in words if word not in stop_words]

    return Counter(filtered_words)


def generate_tailored_summary(master_profile, job_description):
    job_keywords = extract_keywords(job_description)
    profile_lower = master_profile.lower()

    matched_keywords = []

    for keyword, count in job_keywords.most_common(30):
        if keyword in profile_lower:
            matched_keywords.append(keyword)

    summary = "Tailored Resume Summary\n\n"
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
        "with a strong focus on intelligent workflow automation and career intelligence systems."
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


def generate_cover_letter(master_profile, job_description):
    return (
        "Dear Hiring Manager,\n\n"
        "I am excited to apply for this role. My background combines backend development, "
        "AI automation, REST API development, CI/CD workflows, and scalable system design.\n\n"
        "I have worked on backend automation systems, AI-powered workflows, GitHub Actions pipelines, "
        "and intelligent analysis tools. This gives me a strong foundation to contribute to engineering teams "
        "working on automation, backend services, and AI-enabled products.\n\n"
        "I am particularly interested in roles where I can combine backend engineering, automation, "
        "DevOps practices, and AI workflow development to build reliable and useful systems.\n\n"
        "Regards,\n"
        "Muhammad Ibrahim"
    )


def save_outputs(master_profile, high_match_jobs):
    os.makedirs(TAILORED_RESUMES_FOLDER, exist_ok=True)
    os.makedirs(COVER_LETTERS_FOLDER, exist_ok=True)

    for job_path in high_match_jobs:
        if not os.path.exists(job_path):
            print(f"Job file not found: {job_path}")
            continue

        with open(job_path, "r", encoding="utf-8") as file:
            job_description = file.read()

        job_name = os.path.splitext(os.path.basename(job_path))[0]

        tailored_summary = generate_tailored_summary(master_profile, job_description)
        suggestions = suggest_resume_improvements(master_profile, job_description)
        cover_letter = generate_cover_letter(master_profile, job_description)

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

        print(f"Generated tailored resume: {tailored_resume_path}")
        print(f"Generated cover letter: {cover_letter_path}")


def main():
    master_profile = read_master_profile()
    high_match_jobs = read_high_match_jobs()

    if not high_match_jobs:
        print("No HIGH MATCH jobs found.")
        return

    save_outputs(master_profile, high_match_jobs)
    print("\nResume tailoring complete!")


if __name__ == "__main__":
    main()