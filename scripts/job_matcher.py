import csv


def load_jobs():
    with open("data/job_listings.csv", mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def load_resume():
    with open("data/resume.txt", mode="r", encoding="utf-8") as file:
        return file.read().lower()


def calculate_match_score(resume_text, job):
    resume_words = set(resume_text.split())

    job_text = f"""
    {job.get('title', '')}
    {job.get('company', '')}
    {job.get('tags', '')}
    """.lower()

    job_words = set(job_text.split())

    intersection = resume_words.intersection(job_words)
    union = resume_words.union(job_words)

    if not union:
        return 0

    return round(len(intersection) / len(union), 2)


def generate_match_report():
    jobs = load_jobs()
    resume_text = load_resume()

    matched_jobs = []

    for job in jobs:
        score = calculate_match_score(resume_text, job)

        matched_jobs.append({
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "location": job.get("location", ""),
            "tags": job.get("tags", ""),
            "url": job.get("url", ""),
            "scraped_at": job.get("scraped_at", ""),
            "match_score": score
        })

    matched_jobs.sort(key=lambda x: x["match_score"], reverse=True)

    with open(
        "data/job_match_report.csv",
        mode="w",
        newline="",
        encoding="utf-8"
    ) as file:
        fieldnames = [
            "title",
            "company",
            "location",
            "tags",
            "url",
            "scraped_at",
            "match_score"
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()

        for row in matched_jobs:
            writer.writerow(row)

    print("Job match report generated successfully.")


if __name__ == "__main__":
    generate_match_report()