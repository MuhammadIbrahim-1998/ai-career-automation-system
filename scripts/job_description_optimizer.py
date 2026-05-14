import re
from collections import Counter

TECH_KEYWORDS = [
    "python", "c#", ".net", "asp.net core", "asp.net mvc", "flask", "fastapi",
    "javascript", "typescript", "node.js", "next.js", "react",
    "rest api", "restful api", "graphql", "microservices",
    "postgresql", "sql server", "mysql", "mongodb", "redis",
    "docker", "kubernetes", "github actions", "azure devops", "ci/cd",
    "aws", "azure", "gcp", "cloud",
    "ai", "llm", "rag", "automation", "ai agents",
    "authentication", "authorization", "jwt", "oauth",
    "testing", "unit testing", "integration testing", "monitoring",
    "security", "owasp", "backend", "api design", "distributed systems"
]

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().lower()

def normalize(text):
    text = text.replace("ci / cd", "ci/cd").replace("ci-cd", "ci/cd")
    text = text.replace("rest apis", "rest api").replace("restful apis", "restful api")
    return text

def extract_matches(text):
    text = normalize(text)
    found = []
    for keyword in TECH_KEYWORDS:
        if keyword in text:
            found.append(keyword)
    return sorted(set(found))

def calculate_score(jd_keywords, resume_keywords):
    if not jd_keywords:
        return 0
    matched = set(jd_keywords) & set(resume_keywords)
    return round((len(matched) / len(jd_keywords)) * 100, 2)

def main():
    jd = read_file("data/job_description.txt")
    resume = read_file("data/resume.txt")

    jd_keywords = extract_matches(jd)
    resume_keywords = extract_matches(resume)

    matched = sorted(set(jd_keywords) & set(resume_keywords))
    missing = sorted(set(jd_keywords) - set(resume_keywords))

    score = calculate_score(jd_keywords, resume_keywords)

    with open("data/job_description_analysis.txt", "w", encoding="utf-8") as f:
        f.write("Job Description Analysis\n\n")
        f.write(f"ATS Match Score: {score}%\n\n")

        f.write("Strong Matching Keywords:\n")
        for item in matched:
            f.write(f"- {item}\n")

        f.write("\nMissing Important Keywords:\n")
        for item in missing:
            f.write(f"- {item}\n")

        f.write("\nResume Improvement Suggestions:\n")
        for item in missing:
            f.write(f"- Add relevant experience or project proof for: {item}\n")

    print("Analysis complete!")
    print(f"ATS Match Score: {score}%")

if __name__ == "__main__":
    main()