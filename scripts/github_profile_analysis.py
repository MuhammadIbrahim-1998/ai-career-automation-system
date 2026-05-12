import csv
from pathlib import Path
import requests


GITHUB_USERNAME = "MuhammadIbrahim-1998"


def fetch_repositories(username):
    repos = []

    for page in range(1, 5):
        url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}"
        response = requests.get(url, timeout=30)

        if response.status_code != 200:
            print(f"Failed to fetch repositories: {response.status_code}")
            break

        data = response.json()

        if not data:
            break

        repos.extend(data)

    return repos


def analyze_repositories(repos):
    results = []

    for repo in repos:
        name = repo.get("name", "")
        description = repo.get("description") or ""
        language = repo.get("language") or "Not specified"

        results.append({
            "name": name,
            "description": description,
            "language": language,
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "has_readme_signal": "readme" in description.lower(),
            "has_ai_signal": any(word in (name + " " + description).lower() for word in ["ai", "ml", "agent", "automation"]),
            "has_dotnet_signal": any(word in (name + " " + description).lower() for word in ["dotnet", ".net", "asp.net", "csharp", "c#"]),
        })

    return results


def save_report(results):
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    csv_path = output_dir / "github_profile_analysis.csv"

    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        fieldnames = [
            "name",
            "description",
            "language",
            "stars",
            "forks",
            "has_readme_signal",
            "has_ai_signal",
            "has_dotnet_signal"
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Analyzed {len(results)} repositories")
    print(f"GitHub profile analysis saved to {csv_path}")


if __name__ == "__main__":
    repositories = fetch_repositories(GITHUB_USERNAME)
    analysis_results = analyze_repositories(repositories)
    save_report(analysis_results)