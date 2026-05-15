from pathlib import Path
import shutil
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parent.parent

FILES_TO_CREATE = {
    "app/__init__.py": r'''
from flask import Flask


def create_app():
    app = Flask(__name__)

    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app
''',

    "app/routes.py": r'''
import csv
from pathlib import Path
from flask import Blueprint, render_template, request, send_file, abort


main_bp = Blueprint("main", __name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRACKER_FILE = PROJECT_ROOT / "data" / "application_tracker.csv"
JOB_DESCRIPTION_FOLDER = PROJECT_ROOT / "data" / "job_descriptions"


def read_tracker_rows():
    if not TRACKER_FILE.exists():
        return []

    with TRACKER_FILE.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)


def build_stats(rows):
    return {
        "total_jobs": len(rows),
        "high_match": sum(1 for row in rows if row.get("Match Status") == "HIGH MATCH"),
        "medium_match": sum(1 for row in rows if row.get("Match Status") == "MEDIUM MATCH"),
        "low_match": sum(1 for row in rows if row.get("Match Status") == "LOW MATCH"),
        "not_applied": sum(1 for row in rows if row.get("Apply Status") == "NOT APPLIED"),
    }


@main_bp.route("/")
@main_bp.route("/dashboard")
def dashboard():
    rows = read_tracker_rows()
    stats = build_stats(rows)
    return render_template("index.html", rows=rows, stats=stats)


@main_bp.route("/view-file")
def view_file():
    file_path = request.args.get("path", "").strip()

    if not file_path:
        abort(400, "Missing file path.")

    safe_path = (PROJECT_ROOT / file_path).resolve()

    if PROJECT_ROOT not in safe_path.parents and safe_path != PROJECT_ROOT:
        abort(403, "Unsafe file path blocked.")

    if not safe_path.exists():
        abort(404, "File not found.")

    return send_file(safe_path)


@main_bp.route("/job-description/<path:job_filename>")
def job_description(job_filename):
    safe_path = (JOB_DESCRIPTION_FOLDER / job_filename).resolve()

    if JOB_DESCRIPTION_FOLDER.resolve() not in safe_path.parents:
        abort(403, "Unsafe job path blocked.")

    if not safe_path.exists():
        abort(404, "Job description not found.")

    return send_file(safe_path)
''',

    "app/templates/base.html": r'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AI Career Automation Dashboard</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="layout">
        <aside class="sidebar">
            <h2>AI Career OS</h2>
            <p>Automation Dashboard</p>
            <nav>
                <a href="{{ url_for('main.dashboard') }}">Dashboard</a>
            </nav>
        </aside>

        <main class="content">
            {% block content %}{% endblock %}
        </main>
    </div>
</body>
</html>
''',

    "app/templates/index.html": r'''
{% extends "base.html" %}

{% block content %}
<section class="hero">
    <div>
        <h1>AI Career Automation Dashboard</h1>
        <p>Track matched jobs, tailored resumes, cover letters, and application status.</p>
    </div>
</section>

<section class="stats-grid">
    <div class="stat-card">
        <span>Total Jobs</span>
        <strong>{{ stats.total_jobs }}</strong>
    </div>
    <div class="stat-card high">
        <span>HIGH MATCH</span>
        <strong>{{ stats.high_match }}</strong>
    </div>
    <div class="stat-card medium">
        <span>MEDIUM MATCH</span>
        <strong>{{ stats.medium_match }}</strong>
    </div>
    <div class="stat-card low">
        <span>LOW MATCH</span>
        <strong>{{ stats.low_match }}</strong>
    </div>
    <div class="stat-card">
        <span>Not Applied</span>
        <strong>{{ stats.not_applied }}</strong>
    </div>
</section>

<section class="table-card">
    <div class="table-header">
        <h2>Matched Jobs</h2>
        <p>Data source: data/application_tracker.csv</p>
    </div>

    {% if rows %}
    <table>
        <thead>
            <tr>
                <th>Job</th>
                <th>Match</th>
                <th>Score</th>
                <th>Apply Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for row in rows %}
            <tr>
                <td class="job-name">{{ row["Job"] }}</td>
                <td>
                    <span class="badge {{ row['Match Status'].lower().replace(' ', '-') }}">
                        {{ row["Match Status"] }}
                    </span>
                </td>
                <td>{{ row["Similarity Score"] }}</td>
                <td>{{ row["Apply Status"] }}</td>
                <td class="actions">
                    <a href="{{ url_for('main.view_file', path=row['Tailored Resume Path']) }}" target="_blank">Resume</a>
                    <a href="{{ url_for('main.view_file', path=row['Cover Letter Path']) }}" target="_blank">Cover Letter</a>
                    <a href="{{ url_for('main.job_description', job_filename=row['Job']) }}" target="_blank">Job Description</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% else %}
        <div class="empty-state">
            <h3>No tracker data found.</h3>
            <p>Run the backend pipeline first: python scripts/job_scraper_script.py</p>
        </div>
    {% endif %}
</section>
{% endblock %}
''',

    "app/static/css/style.css": r'''
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #0f172a;
    color: #e5e7eb;
}

.layout {
    display: flex;
    min-height: 100vh;
}

.sidebar {
    width: 260px;
    background: #020617;
    padding: 28px;
    border-right: 1px solid #1e293b;
}

.sidebar h2 {
    margin: 0;
    color: #ffffff;
}

.sidebar p {
    color: #94a3b8;
    margin-bottom: 30px;
}

.sidebar a {
    display: block;
    color: #cbd5e1;
    text-decoration: none;
    padding: 12px;
    background: #1e293b;
    border-radius: 12px;
}

.content {
    flex: 1;
    padding: 32px;
}

.hero {
    background: linear-gradient(135deg, #1e3a8a, #312e81);
    border-radius: 24px;
    padding: 30px;
    margin-bottom: 24px;
}

.hero h1 {
    margin: 0 0 8px;
}

.hero p {
    margin: 0;
    color: #dbeafe;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}

.stat-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 18px;
    padding: 20px;
}

.stat-card span {
    display: block;
    color: #94a3b8;
    font-size: 14px;
    margin-bottom: 8px;
}

.stat-card strong {
    font-size: 30px;
}

.stat-card.high strong {
    color: #22c55e;
}

.stat-card.medium strong {
    color: #f59e0b;
}

.stat-card.low strong {
    color: #ef4444;
}

.table-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 20px;
    padding: 24px;
    overflow-x: auto;
}

.table-header {
    margin-bottom: 18px;
}

.table-header h2 {
    margin: 0;
}

.table-header p {
    color: #94a3b8;
    margin: 6px 0 0;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th {
    text-align: left;
    color: #94a3b8;
    padding: 14px;
    border-bottom: 1px solid #334155;
}

td {
    padding: 14px;
    border-bottom: 1px solid #1f2937;
}

.job-name {
    color: #f8fafc;
    font-weight: 600;
}

.badge {
    padding: 6px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
}

.high-match {
    background: rgba(34, 197, 94, 0.15);
    color: #4ade80;
}

.medium-match {
    background: rgba(245, 158, 11, 0.15);
    color: #fbbf24;
}

.low-match {
    background: rgba(239, 68, 68, 0.15);
    color: #f87171;
}

.actions {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.actions a {
    color: #bfdbfe;
    background: #1e293b;
    padding: 8px 10px;
    border-radius: 10px;
    text-decoration: none;
    font-size: 13px;
}

.actions a:hover {
    background: #2563eb;
    color: white;
}

.empty-state {
    padding: 30px;
    background: #020617;
    border-radius: 16px;
    color: #cbd5e1;
}

@media (max-width: 1000px) {
    .layout {
        flex-direction: column;
    }

    .sidebar {
        width: 100%;
    }

    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}
''',

    "run_dashboard.py": r'''
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
'''
}


def backup_file(file_path: Path):
    if not file_path.exists():
        return

    backup_dir = PROJECT_ROOT / "backups" / "dashboard_builder"
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = file_path.name + f".{timestamp}.bak"
    backup_path = backup_dir / backup_name

    shutil.copy2(file_path, backup_path)
    print(f"[BACKUP] {file_path} -> {backup_path}")


def write_file(relative_path: str, content: str):
    file_path = PROJECT_ROOT / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)

    backup_file(file_path)

    with file_path.open("w", encoding="utf-8") as file:
        file.write(content.strip() + "\n")

    print(f"[CREATED] {relative_path}")


def main():
    print("=" * 60)
    print("[BUILDER AGENT] Creating Flask dashboard files...")
    print("=" * 60)

    for relative_path, content in FILES_TO_CREATE.items():
        write_file(relative_path, content)

    print("=" * 60)
    print("[BUILDER AGENT] Dashboard files generated successfully.")
    print("Run dashboard with:")
    print("python run_dashboard.py")
    print("=" * 60)


if __name__ == "__main__":
    main()