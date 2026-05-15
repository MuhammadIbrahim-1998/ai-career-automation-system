import os
import pandas as pd
import csv
import subprocess
import sys
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load embedding model once
model = SentenceTransformer('all-MiniLM-L6-v2')

HIGH_MATCH_THRESHOLD = 0.45
MEDIUM_MATCH_THRESHOLD = 0.35


def read_master_profile():
    with open('data/master_profile.txt', 'r', encoding='utf-8') as f:
        return f.read()


def load_job_descriptions(folder_path):
    jobs = {}

    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as f:
                jobs[filename] = f.read()

    return jobs


def get_embedding(text):
    return model.encode(text)


def calculate_similarity(profile_text, job_text):
    profile_embedding = get_embedding(profile_text)
    job_embedding = get_embedding(job_text)

    similarity = cosine_similarity(
        [profile_embedding],
        [job_embedding]
    )[0][0]

    return round(float(similarity), 4)


def trigger_resume_tailoring_agent():
    results_file = Path("data/semantic_job_results.csv")
    tailoring_script = Path("scripts/resume_tailoring_agent.py")

    if not results_file.exists():
        print("[PIPELINE] semantic_job_results.csv missing. Skipping resume tailoring agent.")
        return

    if not tailoring_script.exists():
        print("[PIPELINE] resume_tailoring_agent.py missing in scripts folder.")
        return

    selected_jobs = []

    try:
        with results_file.open("r", encoding="utf-8", newline="") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                status = row.get("Status", "").strip().upper()
                job_name = row.get("Job", "Unknown Job")

                if status in ["HIGH MATCH", "MEDIUM MATCH"]:
                    print(f"[PIPELINE] {status} detected: {job_name}")
                    selected_jobs.append(job_name)

    except Exception as error:
        print(f"[PIPELINE] Error reading semantic_job_results.csv: {error}")
        return

    if not selected_jobs:
        print("[PIPELINE] No HIGH or MEDIUM MATCH jobs detected. Resume tailoring skipped.")
        return

    print(f"[PIPELINE] Found {len(selected_jobs)} selected job(s).")
    print("[PIPELINE] Triggering resume_tailoring_agent.py...")

    try:
        subprocess.run(
            [sys.executable, str(tailoring_script)],
            check=True
        )
        print("[PIPELINE] Resume tailoring completed successfully.")
    except subprocess.CalledProcessError as error:
        print(f"[PIPELINE] Resume tailoring agent failed: {error}")


def main():
    profile = read_master_profile()

    jobs = load_job_descriptions('data/job_descriptions')

    results = []

    for job_name, job_text in jobs.items():

        score = calculate_similarity(profile, job_text)

        if score >= HIGH_MATCH_THRESHOLD:
            status = "HIGH MATCH"
            print(f"{job_name}: HIGH MATCH ({score})")
        elif score >= MEDIUM_MATCH_THRESHOLD:
            status = "MEDIUM MATCH"
            print(f"{job_name}: MEDIUM MATCH ({score})")
        else:
            status = "LOW MATCH"
            print(f"{job_name}: LOW MATCH ({score})")

        results.append({
            "Job": job_name,
            "Similarity Score": score,
            "Status": status
        })

    df = pd.DataFrame(results)

    df.to_csv(
        'data/semantic_job_results.csv',
        index=False
    )

    print("\nSemantic filtering complete!")

    trigger_resume_tailoring_agent()


if __name__ == "__main__":
    main()