import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from agents.task_queue_manager import add_task, get_pending_tasks, mark_completed

DATA_DIR = ROOT_DIR / "data"
MEMORY_FILE = DATA_DIR / "project_memory.json"
DECISION_FILE = DATA_DIR / "decision_engine_output.json"

LOGS_DIR = DATA_DIR / "orchestrator_logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def run_agent(agent_path):
    full_path = ROOT_DIR / agent_path

    if not full_path.exists():
        print(f"[FAILED] Agent file not found: {agent_path}")
        return False

    try:
        subprocess.run(
            ["python", str(full_path)],
            check=True,
            cwd=str(ROOT_DIR)
        )
        print(f"[SUCCESS] {agent_path}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"[FAILED] {agent_path}")
        print(str(e))
        return False


def load_decision():
    if not DECISION_FILE.exists():
        return None

    with open(DECISION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    print("=" * 60)
    print("[ORCHESTRATOR] Autonomous Orchestrator Started")
    print("=" * 60)

    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            memory = json.load(f)

        print(f"[MEMORY] Files analyzed: {memory.get('files_analyzed', 0)}")
    else:
        print("[WARNING] Memory file not found.")

    print("\n[STEP 1] Updating Project Memory...")
    run_agent("scripts/project_memory_agent.py")

    print("\n[STEP 2] Running Decision Engine...")
    decision_engine_success = run_agent("agents/decision_engine_agent.py")

    if decision_engine_success:
        decision = load_decision()

        if decision:
            task_name = decision.get("recommended_task")
            agent_name = decision.get("recommended_agent")

            print("\n[DECISION OUTPUT]")
            print(f"Next Action: {decision.get('next_action')}")
            print(f"Recommended Task: {task_name}")
            print(f"Recommended Agent: {agent_name}")

            if task_name and agent_name:
                add_task(task_name, agent_name)

    tasks = get_pending_tasks()

    print("\n[TASKS] Pending tasks:")

    if not tasks:
        print(" - No pending tasks found.")
    else:
        for task in tasks:
            print(f" - {task['task']} -> {task['agent']}")

    print("\n[STEP 3] Running Pending Tasks...\n")

    for task in tasks:
        agent = task["agent"]

        success = run_agent(agent)

        if success:
            mark_completed(task["task"])

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_DIR / f"orchestrator_{timestamp}.log"

    with open(log_file, "w", encoding="utf-8") as f:
        f.write("Autonomous orchestrator executed.\n")
        f.write(f"Tasks processed: {len(tasks)}\n")

    print("\n" + "=" * 60)
    print("[ORCHESTRATOR] Completed successfully")
    print("=" * 60)


if __name__ == "__main__":
    main()