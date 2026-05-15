import os
import json
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

MEMORY_FILE = DATA_DIR / "project_memory.json"

LOGS_DIR = DATA_DIR / "dev_agent_logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

IGNORE_FOLDERS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "node_modules",
    ".idea",
    ".vscode"
}

IMPORTANT_EXTENSIONS = {
    ".py",
    ".json",
    ".txt",
    ".md",
    ".csv",
    ".html",
    ".css",
    ".js"
}


def should_scan_file(file_path):
    if any(part in IGNORE_FOLDERS for part in file_path.parts):
        return False

    if file_path.suffix.lower() in IMPORTANT_EXTENSIONS:
        return True

    return False


def scan_project_files():
    project_files = []

    for file_path in ROOT_DIR.rglob("*"):
        if file_path.is_file() and should_scan_file(file_path):
            project_files.append(file_path)

    return project_files


def analyze_file(file_path):
    try:
        relative_path = str(file_path.relative_to(ROOT_DIR))

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        return {
            "path": relative_path,
            "extension": file_path.suffix,
            "size_bytes": file_path.stat().st_size,
            "lines": content.count("\n") + 1,
            "preview": content[:500]
        }

    except Exception as e:
        return {
            "path": str(file_path.relative_to(ROOT_DIR)),
            "error": str(e)
        }


def save_memory(memory_summary):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory_summary, f, indent=4)


def save_log(message):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_DIR / f"project_memory_agent_{timestamp}.log"

    with open(log_file, "w", encoding="utf-8") as f:
        f.write(message)

    return log_file


def main():
    print("=" * 60)
    print("[MEMORY AGENT] Project Memory Agent Started")
    print("=" * 60)

    print("[SCAN] Scanning important project files...")
    project_files = scan_project_files()

    print(f"[SCAN] Files found: {len(project_files)}")

    print("[ANALYZE] Analyzing project files...")
    analyzed_files = []

    for file_path in project_files:
        analyzed_files.append(analyze_file(file_path))

    memory_summary = {
        "timestamp": datetime.now().isoformat(),
        "project_root": str(ROOT_DIR),
        "files_analyzed": len(analyzed_files),
        "important_files": analyzed_files,
        "status": "memory_updated"
    }

    save_memory(memory_summary)

    log_message = (
        "Project Memory Agent Completed Successfully\n"
        f"Timestamp: {memory_summary['timestamp']}\n"
        f"Project Root: {memory_summary['project_root']}\n"
        f"Files Analyzed: {memory_summary['files_analyzed']}\n"
        f"Memory File: {MEMORY_FILE}\n"
    )

    log_file = save_log(log_message)

    print(f"[SUMMARY] Project memory saved: {MEMORY_FILE}")
    print(f"[SUMMARY] Files analyzed: {len(analyzed_files)}")
    print(f"[MEMORY AGENT] Log saved: {log_file}")

    print("=" * 60)
    print("[MEMORY AGENT] Completed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()