import json
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

MEMORY_FILE = DATA_DIR / "project_memory.json"
DECISION_FILE = DATA_DIR / "decision_engine_output.json"
LOGS_DIR = DATA_DIR / "decision_engine_logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def load_memory():
    if not MEMORY_FILE.exists():
        return {}

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_decision(decision):
    with open(DECISION_FILE, "w", encoding="utf-8") as f:
        json.dump(decision, f, indent=4)


def main():
    print("=" * 60)
    print("[DECISION ENGINE] Started")
    print("=" * 60)

    memory = load_memory()

    files_analyzed = memory.get("files_analyzed", 0)

    if files_analyzed > 0:
        next_action = "Project memory is available. System is ready for autonomous workflow."
        recommended_task = "Run Job Hunter Agent"
        recommended_agent = "agents/job_hunter_agent.py"
    else:
        next_action = "Project memory missing or incomplete. Update project memory first."
        recommended_task = "Update Project Memory"
        recommended_agent = "scripts/project_memory_agent.py"

    decision = {
        "timestamp": datetime.now().isoformat(),
        "next_action": next_action,
        "recommended_task": recommended_task,
        "recommended_agent": recommended_agent,
        "status": "decision_created"
    }

    save_decision(decision)

    log_file = LOGS_DIR / f"decision_engine_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    with open(log_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(decision, indent=4))

    print("[DECISION] Next Action:", next_action)
    print("[DECISION] Recommended Task:", recommended_task)
    print("[DECISION] Recommended Agent:", recommended_agent)
    print(f"[DECISION] Saved: {DECISION_FILE}")
    print(f"[LOG] Saved: {log_file}")

    print("=" * 60)
    print("[DECISION ENGINE] Completed successfully")
    print("=" * 60)


if __name__ == "__main__":
    main()