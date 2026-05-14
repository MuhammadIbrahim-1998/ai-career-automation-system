import os
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load embedding model once
model = SentenceTransformer('all-MiniLM-L6-v2')

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

def main():
    profile = read_master_profile()

    jobs = load_job_descriptions('data/job_descriptions')

    results = []

    for job_name, job_text in jobs.items():

        score = calculate_similarity(profile, job_text)

        if score >= 0.75:
            status = "HIGH MATCH"
            print(f"{job_name}: HIGH MATCH ({score})")
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

if __name__ == "__main__":
    main()