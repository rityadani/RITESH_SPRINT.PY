import csv
import os
import json
import time
import numpy as np
from collections import defaultdict
import random

class AdvancedSmartAgent:
    def __init__(self, alpha=0.1, gamma=0.95, epsilon=0.1):
        # Get proper paths
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(script_dir)
        
        # Enhanced RL parameters
        self.alpha = alpha  # Lower learning rate for stability
        self.gamma = gamma  # Higher discount for long-term rewards
        self.epsilon = epsilon  # Lower exploration for production
        
        # Enhanced state representation
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.state_visit_count = defaultdict(int)
        self.action_success_history = defaultdict(list)
        
        # Load configurations
        self.load_enhanced_config()
        self.load_q_table()
        
        # Reward shaping parameters
        self.reward_history = []
        self.performance_baseline = 0.7
        
    def load_enhanced_config(self):
        """Load enhanced state-action mappings with granular states"""
        config_path = os.path.join(self.project_root, "data", "enhanced_states_actions.json")
        
        enhanced_config = {
            "states": {
                # Service-level granular states
                "service_down_critical": {
                    "description": "Critical service completely down",
                    "severity": "critical",
                    "context": ["service_name", "downtime_duration", "user_impact"]
                },
                "service_degraded_performance": {
                    "description": "Service running but slow",
                    "severity": "high", 
                    "context": ["response_time", "error_rate", "throughput"]
                },
                "database_connection_lost": {
                    "description": "Database connectivity issues",
                    "severity": "critical",
                    "context": ["connection_pool", "query_timeout", "transaction_failures"]
                },
                "resource_exhaustion_memory": {
                    "description": "Memory usage above threshold",
                    "severity": "high",
                    "context": ["memory_percentage", "process_count", "swap_usage"]
                },
                "resource_exhaustion_cpu": {
                    "description": "CPU usage above threshold", 
                    "severity": "high",
                    "context": ["cpu_percentage", "load_average", "process_queue"]
                },
                "network_connectivity_lost": {
                    "description": "Network connectivity issues",
                    "severity": "critical",
                    "context": ["packet_loss", "latency", "bandwidth"]
                },
                "deployment_failure": {
                    "description": "Deployment process failed",
                    "severity": "critical",
                    "context": ["deployment_stage", "error_code", "rollback_available"]
                }
            },
            "actions": {
                "service_down_critical": [
                    "restart_service_graceful",
                    "restart_service_force", 
                    "failover_to_backup",
                    "scale_horizontal",
                    "rollback_deployment"
                ],
                "service_degraded_performance": [
                    "optimize_queries",
                    "clear_cache",
                    "restart_service_graceful",
                    "scale_vertical",
                    "enable_circuit_breaker"
                ],
                "database_connection_lost": [
                    "restart_database_service",
                    "reset_connection_pool",
                    "failover_to_replica",
                    "increase_connection_timeout",
                    "restart_application"
                ],
                "resource_exhaustion_memory": [
                    "restart_high_memory_processes",
                    "clear_application_cache",
                    "scale_vertical",
                    "enable_memory_limits",
                    "garbage_collection_force"
                ],
                "resource_exhaustion_cpu": [
                    "scale_horizontal",
                    "optimize_cpu_intensive_tasks",
                    "restart_cpu_heavy_processes",
                    "enable_cpu_throttling",
                    "load_balance_redistribute"
                ],
                "network_connectivity_lost": [
                    "restart_network_service",
                    "switch_network_interface",
                    "reset_network_stack",
                    "failover_to_backup_network",
                    "contact_network_team"
                ],
                "deployment_failure": [
                    "rollback_to_previous_version",
                    "retry_deployment",
                    "manual_deployment_fix",
                    "revert_configuration",
                    "emergency_maintenance_mode"
                ]
            },
            "reward_shaping": {
                "success_bonus": 1.0,
                "failure_penalty": -1.0,
                "time_penalty": -0.1,
                "user_impact_multiplier": 2.0,
                "cost_efficiency_bonus": 0.5
            }
        }
        
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            if not os.path.exists(config_path):
                with open(config_path, 'w') as f:
                    json.dump(enhanced_config, f, indent=2)
            
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"Config error: {e}")
            self.config = enhanced_config

    def load_q_table(self):
        """Load Q-table with enhanced tracking"""
        rl_table_path = os.path.join(self.project_root, "data", "enhanced_rl_table.csv")
        
        if not os.path.exists(rl_table_path):
            return
            
        try:
            with open(rl_table_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    state = row["state"]
                    action = row["action"]
                    q_value = float(row["q_value"])
                    visit_count = int(row.get("visit_count", 0))
                    
                    self.q_table[state][action] = q_value
                    self.state_visit_count[f"{state}_{action}"] = visit_count
        except Exception as e:
            print(f"Error loading Q-table: {e}")

    def save_q_table(self):
        """Save enhanced Q-table with metadata"""
        rl_table_path = os.path.join(self.project_root, "data", "enhanced_rl_table.csv")
        
        try:
            rows = []
            for state, actions in self.q_table.items():
                for action, q_value in actions.items():
                    visit_count = self.state_visit_count.get(f"{state}_{action}", 0)
                    rows.append([state, action, q_value, visit_count, time.time()])
            
            with open(rl_table_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["state", "action", "q_value", "visit_count", "last_updated"])
                writer.writerows(rows)
        except Exception as e:
            print(f"Error saving Q-table: {e}")

    def get_enhanced_state(self, issue_data):
        """Convert issue data to enhanced state representation"""
        error_type = issue_data.get('error_type', 'unknown')
        severity = issue_data.get('severity', 'medium')
        service = issue_data.get('service', 'unknown')
        
        # Create granular state based on context
        if error_type == 'service_down':
            if severity == 'critical':
                return 'service_down_critical'
            else:
                return 'service_degraded_performance'
        elif 'database' in error_type.lower():
            return 'database_connection_lost'
        elif 'memory' in str(issue_data.get('details', {})):
            return 'resource_exhaustion_memory'
        elif 'cpu' in str(issue_data.get('details', {})):
            return 'resource_exhaustion_cpu'
        elif 'network' in error_type.lower():
            return 'network_connectivity_lost'
        elif 'deployment' in error_type.lower():
            return 'deployment_failure'
        else:
            return f"unknown_{error_type}"

    def choose_action_enhanced(self, issue_data):
        """Enhanced action selection with context awareness"""
        state = self.get_enhanced_state(issue_data)
        available_actions = self.config["actions"].get(state, ["investigate_manual"])
        
        if not available_actions:
            return "investigate_manual"
        
        # Epsilon-greedy with UCB (Upper Confidence Bound)
        if random.random() < self.epsilon:
            return random.choice(available_actions)
        
        # Calculate UCB values for exploration vs exploitation
        best_action = None
        best_value = float('-inf')
        
        total_visits = sum(self.state_visit_count.get(f"{state}_{a}", 0) for a in available_actions)
        
        for action in available_actions:
            q_value = self.q_table[state][action]
            visit_count = self.state_visit_count.get(f"{state}_{action}", 0)
            
            # UCB calculation
            if visit_count == 0:
                ucb_value = float('inf')  # Prioritize unvisited actions
            else:
                confidence = np.sqrt(2 * np.log(total_visits + 1) / visit_count)
                ucb_value = q_value + confidence
            
            if ucb_value > best_value:
                best_value = ucb_value
                best_action = action
        
        return best_action or available_actions[0]

    def calculate_shaped_reward(self, issue_data, action, result, execution_time):
        """Advanced reward shaping based on multiple factors"""
        base_reward = 1.0 if result else -1.0
        
        # Time-based penalty (faster resolution is better)
        time_penalty = min(execution_time * 0.1, 1.0)
        
        # Severity-based multiplier
        severity = issue_data.get('severity', 'medium')
        severity_multiplier = {'critical': 2.0, 'high': 1.5, 'medium': 1.0, 'low': 0.5}.get(severity, 1.0)
        
        # User impact consideration
        user_impact = issue_data.get('user_impact', 'medium')
        impact_multiplier = {'high': 2.0, 'medium': 1.0, 'low': 0.5}.get(user_impact, 1.0)
        
        # Action efficiency (prefer less disruptive actions)
        action_efficiency = {
            'restart_service_graceful': 1.0,
            'restart_service_force': 0.8,
            'rollback_deployment': 0.6,
            'manual_intervention': 0.4
        }.get(action, 0.7)
        
        # Calculate final shaped reward
        shaped_reward = (base_reward * severity_multiplier * impact_multiplier * action_efficiency) - time_penalty
        
        return max(shaped_reward, -2.0)  # Cap negative rewards

    def update_enhanced(self, issue_data, action, result, execution_time=1.0):
        """Enhanced Q-learning update with reward shaping"""
        state = self.get_enhanced_state(issue_data)
        
        # Calculate shaped reward
        reward = self.calculate_shaped_reward(issue_data, action, result, execution_time)
        
        # Update visit count
        state_action_key = f"{state}_{action}"
        self.state_visit_count[state_action_key] += 1
        
        # Q-learning update
        current_q = self.q_table[state][action]
        
        # Get max Q-value for next state (assuming same state for simplicity)
        available_actions = self.config["actions"].get(state, [action])
        max_next_q = max([self.q_table[state][a] for a in available_actions], default=0)
        
        # Q-learning formula with reward shaping
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state][action] = new_q
        
        # Track performance
        self.reward_history.append(reward)
        self.action_success_history[action].append(1 if result else 0)
        
        # Save updated table
        self.save_q_table()
        
        return reward

    def get_performance_metrics(self):
        """Get detailed performance metrics"""
        if not self.reward_history:
            return {"status": "no_data"}
        
        recent_rewards = self.reward_history[-100:]  # Last 100 actions
        
        metrics = {
            "average_reward": np.mean(recent_rewards),
            "reward_trend": np.mean(recent_rewards[-10:]) - np.mean(recent_rewards[-20:-10]) if len(recent_rewards) >= 20 else 0,
            "total_actions": len(self.reward_history),
            "exploration_rate": self.epsilon,
            "top_actions": {}
        }
        
        # Calculate action success rates
        for action, successes in self.action_success_history.items():
            if successes:
                success_rate = np.mean(successes[-20:])  # Last 20 attempts
                metrics["top_actions"][action] = success_rate
        
        return metrics

if __name__ == "__main__":
    agent = AdvancedSmartAgent()
    
    # Test with realistic deployment issue
    test_issue = {
        'error_type': 'service_down',
        'service': 'api_gateway',
        'severity': 'critical',
        'user_impact': 'high',
        'details': {'status': 'unreachable', 'error': 'Connection refused'}
    }
    
    action = agent.choose_action_enhanced(test_issue)
    print(f"🤖 Enhanced Action Selected: {action}")
    
    # Simulate execution and update
    result = True  # Assume success
    execution_time = 2.5  # 2.5 seconds
    reward = agent.update_enhanced(test_issue, action, result, execution_time)
    
    print(f"🏆 Shaped Reward: {reward}")
    print(f"📊 Performance Metrics: {agent.get_performance_metrics()}")