import json
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

JOBS_FILE = DATA_DIR / "job_hunter_results.json"

LOGS_DIR = DATA_DIR / "job_hunter_logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def generate_sample_jobs():
    return [
        {
            "title": "AI Backend Engineer",
            "company": "Sample Remote AI Company",
            "location": "Remote",
            "salary_range": "1500-2500 USD",
            "skills_required": [
                "Python",
                "Flask",
                "REST APIs",
                "LLMs",
                "RAG",
                "Vector Database",
                ".NET",
                "SQL"
            ],
            "match_reason": "Strong match with your AI backend, Flask, API, RAG and .NET background.",
            "status": "new"
        },
        {
            "title": "AI Automation Engineer",
            "company": "Sample Automation Startup",
            "location": "Remote",
            "salary_range": "1000-2000 USD",
            "skills_required": [
                "n8n",
                "AI Agents",
                "Python",
                "API Integration",
                "Google Sheets",
                "Gmail Automation"
            ],
            "match_reason": "Strong match with your n8n, AI agents, automation and workflow experience.",
            "status": "new"
        },
        {
            "title": ".NET Backend Developer with AI Integration",
            "company": "Sample SaaS Company",
            "location": "Remote",
            "salary_range": "1200-2200 USD",
            "skills_required": [
                "ASP.NET Core",
                "MVC",
                "Web API",
                "SQL Server",
                "Azure DevOps",
                "AI API Integration"
            ],
            "match_reason": "Strong match with your .NET MVC, Web API, SQL Server and AI integration profile.",
            "status": "new"
        }
    ]


def save_jobs(jobs):
    with open(JOBS_FILE, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=4)


def save_log(jobs):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_DIR / f"job_hunter_{timestamp}.log"

    with open(log_file, "w", encoding="utf-8") as f:
        f.write("Job Hunter Agent Completed Successfully\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Jobs Found: {len(jobs)}\n")

    return log_file


def main():
    print("=" * 60)
    print("[JOB HUNTER] Job Hunter Agent Started")
    print("=" * 60)

    print("[SEARCH] Generating sample matched jobs...")
    jobs = generate_sample_jobs()

    save_jobs(jobs)
    log_file = save_log(jobs)

    print(f"[RESULT] Jobs saved: {JOBS_FILE}")
    print(f"[RESULT] Jobs found: {len(jobs)}")
    print(f"[LOG] Saved: {log_file}")

    print("=" * 60)
    print("[JOB HUNTER] Completed successfully")
    print("=" * 60)


if __name__ == "__main__":
    main()