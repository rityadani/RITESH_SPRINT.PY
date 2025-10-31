import time
import os
import csv
from smart_agent import SmartAgent
def execute_fix(action):
    """Simple auto-fix function that simulates fixing actions"""
    fix_actions = {
        "clear_port": True,
        "restart_service": True, 
        "restart_container": True,
        "rollback_config": True,
        "check_network": True
    }
    return fix_actions.get(action, False)

PLANNER_LOG = "logs/planner_log.csv"
HUMAN_FEEDBACK_FILE = "data/human_feedback.csv"

class PlannerAgent:
    def __init__(self):
        self.agent = SmartAgent()
        self.ensure_files()

    def ensure_files(self):
        # create logs folder
        if not os.path.exists("logs"):
            os.makedirs("logs")

        # create planner log file if not exists
        if not os.path.exists(PLANNER_LOG):
            with open(PLANNER_LOG, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp","state","action","result","reward"])

        # create human feedback file if not exists
        if not os.path.exists(HUMAN_FEEDBACK_FILE):
            with open(HUMAN_FEEDBACK_FILE, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp","state","action","feedback"])

    def log_fix(self, state, action, result, reward):
        with open(PLANNER_LOG, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), state, action, result, reward])

    def store_human_feedback(self, state, action, feedback):
        with open(HUMAN_FEEDBACK_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), state, action, feedback])

        # update RL table from human learning
        self.agent.human_update(state, action, feedback)

    def handle_event(self, error_type):
        print(f"\n🚨 Error detected: {error_type}")

        # Ask RL agent for best action
        action = self.agent.choose_action(error_type)
        print(f"🤖 RL chosen action: {action}")

        # Auto fix run
        result = execute_fix(action)
        print(f"🔧 Fix result: {result}")

        # RL reward
        reward = 1 if result else -1
        self.agent.update(error_type, action, reward)

        # Log
        self.log_fix(error_type, action, result, reward)
        print(f"🏆 Reward: {reward} | ✅ RL Table Updated")

        # HUMAN FEEDBACK PROMPT ✅
        fb = input("Give feedback (1 = correct, -1 = wrong, skip = ignore): ")

        if fb.strip() in ["1", "-1"]:
            fb = int(fb)
            self.store_human_feedback(error_type, action, fb)
            print(f"🧠 Human feedback applied: {fb}")
        else:
            print("➖ Feedback skipped")

        return result


# Test Run
if __name__ == "__main__":
    planner = PlannerAgent()
    planner.handle_event("port_busy")
