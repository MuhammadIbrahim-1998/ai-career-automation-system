import csv


def load_best_jobs(limit=3):
    with open(
        "data/job_match_report.csv",
        mode="r",
        encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)

        jobs = sorted(
            list(reader),
            key=lambda x: float(x["match_score"]),
            reverse=True
        )

        return jobs[:limit]


def generate_cover_letter(job):
    return f"""
========================================
Company: {job['company']}
Role: {job['title']}
========================================

Dear Hiring Manager,

I am excited to apply for the position of {job['title']} at {job['company']}.

My background in .NET development, backend systems, AI automation, APIs, DevOps, and cloud technologies aligns well with the role requirements.

I have experience working with:
- ASP.NET Core
- REST APIs
- Python automation
- GitHub Actions
- Docker
- AI integration
- Automation workflows

I would welcome the opportunity to contribute my technical skills and problem-solving abilities to your team.

Best regards,
Muhammad Ibrahim

Job URL:
{job['url']}

"""


def save_cover_letters():
    jobs = load_best_jobs()

    letters = []

    for job in jobs:
        letters.append(generate_cover_letter(job))

    with open(
        "data/cover_letters.txt",
        mode="w",
        encoding="utf-8"
    ) as file:
        file.write("\n\n".join(letters))

    print("Cover letters generated successfully.")


if __name__ == "__main__":
    save_cover_letters()