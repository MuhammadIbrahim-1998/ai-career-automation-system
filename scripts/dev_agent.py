import os
import subprocess
from pathlib import Path
from shutil import copy2
from datetime import datetime


ROOT_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT_DIR / "data" / "dev_agent_logs"
BACKUP_DIR = ROOT_DIR / "backups" / "dev_agent"


SAFE_COMMANDS = {
    "1": {
        "label": "Check Python version",
        "args": ["python", "--version"]
    },
    "2": {
        "label": "Check Git status",
        "args": ["git", "status"]
    },
    "3": {
        "label": "Run full AI career pipeline",
        "args": ["python", "scripts/job_scraper_script.py"]
    },
    "4": {
        "label": "Run application tracker",
        "args": ["python", "scripts/application_tracker.py"]
    },
    "5": {
        "label": "Run Flask dashboard",
        "args": ["python", "run_dashboard.py"]
    }
}


def ensure_dirs():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def log_action(action, details):
    ensure_dirs()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"dev_agent_{timestamp}.log"

    with log_file.open("a", encoding="utf-8") as file:
        file.write(f"[{datetime.now()}] {action}\n")
        file.write(f"{details}\n\n")

    print(f"[DEV AGENT] Log saved: {log_file}")


def ensure_inside_project(path):
    resolved_path = path.resolve()

    try:
        resolved_path.relative_to(ROOT_DIR.resolve())
        return resolved_path
    except ValueError:
        raise ValueError(f"[BLOCKED] Unsafe path outside project: {resolved_path}")


def scan_project():
    print("\n[DEV AGENT] Project structure scan:\n")

    ignored_dirs = {".git", "__pycache__", ".venv", "venv", "node_modules"}

    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]

        root_path = Path(root)
        relative_root = root_path.relative_to(ROOT_DIR)

        for file_name in files:
            file_path = root_path / file_name
            relative_file = file_path.relative_to(ROOT_DIR)
            print(relative_file)

    log_action("SCAN_PROJECT", "Project structure scanned.")


def read_file_safe(relative_path):
    target_path = ensure_inside_project(ROOT_DIR / relative_path)

    if not target_path.exists():
        print(f"[DEV AGENT] File not found: {target_path}")
        return

    if not target_path.is_file():
        print(f"[DEV AGENT] Not a file: {target_path}")
        return

    print(f"\n[DEV AGENT] Reading file: {target_path}\n")

    content = target_path.read_text(encoding="utf-8", errors="replace")
    print(content)

    log_action("READ_FILE", f"Read file: {relative_path}")


def backup_file(target_path):
    target_path = ensure_inside_project(target_path)

    if not target_path.exists():
        return None

    relative_path = target_path.relative_to(ROOT_DIR)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    safe_backup_name = str(relative_path).replace("\\", "__").replace("/", "__")
    backup_path = BACKUP_DIR / f"{safe_backup_name}.{timestamp}.bak"

    backup_path.parent.mkdir(parents=True, exist_ok=True)
    copy2(target_path, backup_path)

    print(f"[BACKUP] {relative_path} -> {backup_path}")
    log_action("BACKUP_FILE", f"{relative_path} backed up to {backup_path}")

    return backup_path


def approve(message):
    print(f"\n{message}")
    answer = input("Approve? (y/n): ").strip().lower()
    return answer == "y"


def write_file_safe(relative_path, content):
    target_path = ensure_inside_project(ROOT_DIR / relative_path)

    print(f"[DEV AGENT] Target file: {target_path}")

    if not approve(f"[APPROVAL REQUIRED] Write/update file: {relative_path}"):
        print("[BLOCKED] Write cancelled by user.")
        return

    target_path.parent.mkdir(parents=True, exist_ok=True)

    if target_path.exists():
        backup_file(target_path)

    target_path.write_text(content, encoding="utf-8")

    print(f"[DEV AGENT] File written successfully: {relative_path}")
    log_action("WRITE_FILE", f"Wrote file: {relative_path}")


def run_safe_command(command_key):
    command_info = SAFE_COMMANDS.get(command_key)

    if not command_info:
        print("[BLOCKED] Invalid command selection.")
        return

    label = command_info["label"]
    args = command_info["args"]

    print(f"\n[SAFE COMMAND] {label}")
    print("Command:", " ".join(args))

    if not approve("[APPROVAL REQUIRED] Run this command"):
        print("[BLOCKED] Command cancelled by user.")
        return

    try:
        result = subprocess.run(
            args,
            cwd=str(ROOT_DIR),
            text=True,
            capture_output=True
        )

        print("\n[COMMAND OUTPUT]")
        print(result.stdout)

        if result.stderr:
            print("\n[COMMAND ERRORS]")
            print(result.stderr)

        log_action(
            "RUN_COMMAND",
            f"Command: {' '.join(args)}\nReturn code: {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )

    except Exception as error:
        print(f"[DEV AGENT] Command failed: {error}")
        log_action("COMMAND_ERROR", str(error))


def show_safe_commands():
    print("\nAvailable safe commands:\n")

    for key, command in SAFE_COMMANDS.items():
        print(f"{key}. {command['label']}")
        print(f"   {' '.join(command['args'])}")


def main_menu():
    ensure_dirs()

    while True:
        print("\n" + "=" * 60)
        print("[DEV AGENT] Safe AI Developer Agent Foundation")
        print("=" * 60)
        print("1. Scan project")
        print("2. Read file")
        print("3. Run approved safe command")
        print("4. Exit")

        choice = input("\nChoose option: ").strip()

        if choice == "1":
            scan_project()

        elif choice == "2":
            relative_path = input("Enter file path from project root: ").strip()
            read_file_safe(relative_path)

        elif choice == "3":
            show_safe_commands()
            command_key = input("\nChoose safe command number: ").strip()
            run_safe_command(command_key)

        elif choice == "4":
            print("[DEV AGENT] Exiting.")
            break

        else:
            print("[DEV AGENT] Invalid option.")


if __name__ == "__main__":
    main_menu()