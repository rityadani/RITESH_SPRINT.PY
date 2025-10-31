import csv
import os
import json
from datetime import datetime
import time

class Dashboard:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.rl_table_path = os.path.join(self.project_root, "data", "rl_table.csv")
        self.planner_log_path = os.path.join(self.project_root, "logs", "planner_log.csv")
        self.human_feedback_path = os.path.join(self.project_root, "data", "human_feedback.csv")
        self.telemetry_path = os.path.join(self.project_root, "insightflow", "telemetry.json")

    def load_rl_table(self):
        """Load Q-learning table"""
        data = []
        if os.path.exists(self.rl_table_path):
            with open(self.rl_table_path, 'r') as f:
                reader = csv.DictReader(f)
                data = list(reader)
        return data

    def load_planner_logs(self):
        """Load planner execution logs"""
        data = []
        if os.path.exists(self.planner_log_path):
            with open(self.planner_log_path, 'r') as f:
                reader = csv.DictReader(f)
                data = list(reader)
        return data

    def load_human_feedback(self):
        """Load human feedback data"""
        data = []
        if os.path.exists(self.human_feedback_path):
            with open(self.human_feedback_path, 'r') as f:
                reader = csv.DictReader(f)
                data = list(reader)
        return data

    def get_system_stats(self):
        """Get overall system statistics"""
        rl_data = self.load_rl_table()
        planner_data = self.load_planner_logs()
        feedback_data = self.load_human_feedback()
        
        stats = {
            "total_actions": len(rl_data),
            "total_executions": len(planner_data),
            "human_feedbacks": len(feedback_data),
            "success_rate": 0,
            "top_actions": {}
        }
        
        # Calculate success rate
        if planner_data:
            successful = sum(1 for log in planner_data if log.get('result') == 'True')
            stats["success_rate"] = round((successful / len(planner_data)) * 100, 2)
        
        # Top performing actions
        action_performance = {}
        for row in rl_data:
            action = row.get('action', '')
            q_value = float(row.get('q_value', 0))
            if action not in action_performance or q_value > action_performance[action]:
                action_performance[action] = q_value
        
        stats["top_actions"] = dict(sorted(action_performance.items(), 
                                         key=lambda x: x[1], reverse=True)[:5])
        
        return stats

    def display_dashboard(self):
        """Display the main dashboard"""
        print("=" * 60)
        print("🚀 INTELLIGENT SYSTEM DASHBOARD")
        print("=" * 60)
        
        stats = self.get_system_stats()
        
        print(f"\n📊 SYSTEM OVERVIEW")
        print(f"   Total Actions Learned: {stats['total_actions']}")
        print(f"   Total Executions: {stats['total_executions']}")
        print(f"   Human Feedbacks: {stats['human_feedbacks']}")
        print(f"   Success Rate: {stats['success_rate']}%")
        
        print(f"\n🏆 TOP PERFORMING ACTIONS")
        for action, q_value in stats['top_actions'].items():
            print(f"   {action}: {q_value:.3f}")
        
        print(f"\n📈 RECENT ACTIVITY")
        recent_logs = self.load_planner_logs()[-5:]
        for log in recent_logs:
            timestamp = log.get('timestamp', 'N/A')
            state = log.get('state', 'N/A')
            action = log.get('action', 'N/A')
            result = "✅" if log.get('result') == 'True' else "❌"
            print(f"   {timestamp} | {state} → {action} {result}")
        
        print(f"\n🧠 HUMAN FEEDBACK SUMMARY")
        feedback_data = self.load_human_feedback()
        if feedback_data:
            positive = sum(1 for f in feedback_data if f.get('feedback') == '1')
            negative = sum(1 for f in feedback_data if f.get('feedback') == '-1')
            print(f"   Positive: {positive} | Negative: {negative}")
        else:
            print("   No feedback data available")

    def show_rl_table(self):
        """Display Q-learning table"""
        print("\n🤖 REINFORCEMENT LEARNING TABLE")
        print("-" * 50)
        rl_data = self.load_rl_table()
        
        states = {}
        for row in rl_data:
            state = row.get('state', '')
            action = row.get('action', '')
            q_value = float(row.get('q_value', 0))
            
            if state not in states:
                states[state] = {}
            states[state][action] = q_value
        
        for state, actions in states.items():
            print(f"\n📍 {state.upper()}:")
            for action, q_value in sorted(actions.items(), key=lambda x: x[1], reverse=True):
                print(f"   {action}: {q_value:.3f}")

    def interactive_menu(self):
        """Interactive dashboard menu"""
        while True:
            print("\n" + "=" * 40)
            print("📊 DASHBOARD MENU")
            print("=" * 40)
            print("1. System Overview")
            print("2. RL Learning Table")
            print("3. Recent Logs")
            print("4. Human Feedback")
            print("5. Refresh Data")
            print("0. Exit")
            
            choice = input("\nSelect option (0-5): ").strip()
            
            if choice == "1":
                self.display_dashboard()
            elif choice == "2":
                self.show_rl_table()
            elif choice == "3":
                self.show_recent_logs()
            elif choice == "4":
                self.show_human_feedback()
            elif choice == "5":
                print("🔄 Data refreshed!")
            elif choice == "0":
                print("👋 Dashboard closed!")
                break
            else:
                print("❌ Invalid option!")

    def show_recent_logs(self):
        """Show recent planner logs"""
        print("\n📋 RECENT EXECUTION LOGS")
        print("-" * 60)
        logs = self.load_planner_logs()[-10:]
        
        for log in logs:
            timestamp = log.get('timestamp', 'N/A')
            state = log.get('state', 'N/A')
            action = log.get('action', 'N/A')
            result = log.get('result', 'N/A')
            reward = log.get('reward', 'N/A')
            
            status = "✅ SUCCESS" if result == 'True' else "❌ FAILED"
            print(f"{timestamp} | {state} → {action} | {status} (Reward: {reward})")

    def show_human_feedback(self):
        """Show human feedback data"""
        print("\n🧠 HUMAN FEEDBACK HISTORY")
        print("-" * 50)
        feedback = self.load_human_feedback()
        
        for fb in feedback[-10:]:
            timestamp = fb.get('timestamp', 'N/A')
            state = fb.get('state', 'N/A')
            action = fb.get('action', 'N/A')
            rating = fb.get('feedback', 'N/A')
            
            emoji = "👍" if rating == '1' else "👎" if rating == '-1' else "❓"
            print(f"{timestamp} | {state} → {action} | {emoji} {rating}")

if __name__ == "__main__":
    dashboard = Dashboard()
    dashboard.interactive_menu()