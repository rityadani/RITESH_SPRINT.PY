# main.py
import threading
import time

# ---- Imports ----
from core.sovereign_bus import SovereignBus
from agents.event_handler import run_event_handler
from agents.planner_agent import run_planner


# ---- Callback Functions ----
def print_issue(data):
    """Whenever event_handler detects an error, print it."""
    print(f"[Main] ISSUE DETECTED → {data}")


def print_plan(data):
    """Whenever planner creates a plan, print it."""
    print(f"[Main] PLAN GENERATED → {data}")


# ---- Main Controller ----
def main():
    # 1️⃣ Start local event bus
    bus = SovereignBus()

    # 2️⃣ Subscribe to events for console visibility
    bus.subscribe("issue.detected", print_issue)
    bus.subscribe("plan.generated", print_plan)

    # 3️⃣ Start Event Handler (reads logs/system.log)
    event_thread = threading.Thread(
        target=run_event_handler, args=(bus, "logs/system.log"), daemon=True
    )
    event_thread.start()

    # 4️⃣ Start Planner Agent (rule-based)
    planner_thread = threading.Thread(
        target=run_planner, args=(bus,), daemon=True
    )
    planner_thread.start()

    print("\n✅ System + Planner started successfully.")
    print("💡 Add a line like 'ERROR: bad_config: Something failed' to logs/system.log")
    print("🔍 Watch console — you’ll see issue → plan chain in real time.\n")

    # 5️⃣ Keep the system alive
    try:
        while True:
            time.sleep(3)
    except KeyboardInterrupt:
        print("\n🛑 System stopped.")


# ---- Entry Point ----
if __name__ == "__main__":
    main()
