import random
import time
from agents.planner_agent import PlannerAgent

# Possible error states (same as your YAML)
error_states = [
    "port_busy",
    "api_down",
    "config_error",
    "container_crash",
    "network_issue"
]

def simulate_errors(runs=30):
    planner = PlannerAgent()

    for i in range(runs):
        state = random.choice(error_states)
        print(f"\n======= Test Run {i+1} / {runs} =======")
        planner.handle_event(state)
        time.sleep(0.5)

if __name__ == "__main__":
    simulate_errors(30)  # 30 simulations (change if needed)
