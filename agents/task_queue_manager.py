import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
QUEUE_FILE = ROOT_DIR / "data" / "task_queue.json"


def load_tasks():
    if not QUEUE_FILE.exists():
        QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
        save_tasks([])
        return []

    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tasks(tasks):
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4)


def add_task(task_name, agent_name):
    tasks = load_tasks()

    already_pending = any(
        t["task"] == task_name and t["status"] == "pending"
        for t in tasks
    )

    if already_pending:
        print(f"[QUEUE] Task already pending: {task_name}")
        return

    task = {
        "task": task_name,
        "agent": agent_name,
        "status": "pending"
    }

    tasks.append(task)
    save_tasks(tasks)

    print(f"[QUEUE] Task added: {task_name}")


def get_pending_tasks():
    tasks = load_tasks()
    return [t for t in tasks if t["status"] == "pending"]


def mark_completed(task_name):
    tasks = load_tasks()

    for t in tasks:
        if t["task"] == task_name and t["status"] == "pending":
            t["status"] = "completed"

    save_tasks(tasks)

    print(f"[QUEUE] Task completed: {task_name}")