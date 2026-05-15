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
