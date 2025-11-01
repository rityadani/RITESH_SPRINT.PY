import threading
import time
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.sovereign_bus import SovereignBus
from core.real_deployment_monitor import RealDeploymentMonitor
from agents.advanced_smart_agent import AdvancedSmartAgent
from agents.real_action_executor import RealActionExecutor

class ProductionIntelligentSystem:
    def __init__(self):
        print("🚀 Initializing Production Intelligent System...")
        
        # Core components
        self.bus = SovereignBus()
        self.deployment_monitor = RealDeploymentMonitor(self.bus)
        self.smart_agent = AdvancedSmartAgent()
        self.action_executor = RealActionExecutor()
        
        # Performance tracking
        self.total_issues_handled = 0
        self.successful_resolutions = 0
        self.start_time = time.time()
        
        # Setup event subscriptions
        self.setup_event_handlers()
        
    def setup_event_handlers(self):
        """Setup real deployment event handlers"""
        self.bus.subscribe("deployment.issue.detected", self.handle_real_deployment_issue)
        print("✅ Event handlers configured for real deployment monitoring")
    
    def handle_real_deployment_issue(self, issue_data):
        """Handle real deployment issues with advanced RL"""
        self.total_issues_handled += 1
        
        print(f"\n🚨 REAL DEPLOYMENT ISSUE #{self.total_issues_handled}")
        print(f"   Type: {issue_data.get('error_type', 'unknown')}")
        print(f"   Service: {issue_data.get('service', 'unknown')}")
        print(f"   Severity: {issue_data.get('severity', 'unknown')}")
        print(f"   Details: {issue_data.get('details', {})}")
        
        # Use advanced smart agent for action selection
        start_time = time.time()
        action = self.smart_agent.choose_action_enhanced(issue_data)
        
        print(f"🤖 Advanced RL Selected Action: {action}")
        
        # Execute real action
        execution_context = {
            'service': issue_data.get('service', 'unknown'),
            'severity': issue_data.get('severity', 'medium'),
            'issue_data': issue_data
        }
        
        execution_result = self.action_executor.execute_action(action, execution_context)
        execution_time = time.time() - start_time
        
        print(f"🔧 Real Execution Result: {execution_result['success']}")
        print(f"⏱️  Execution Time: {execution_time:.2f}s")
        
        # Update RL agent with real results and reward shaping
        shaped_reward = self.smart_agent.update_enhanced(
            issue_data, 
            action, 
            execution_result['success'], 
            execution_time
        )
        
        print(f"🏆 Shaped Reward: {shaped_reward:.3f}")
        
        # Track success rate
        if execution_result['success']:
            self.successful_resolutions += 1
        
        # Display performance metrics
        self.display_performance_metrics()
        
        # Publish resolution event
        resolution_data = {
            'issue': issue_data,
            'action_taken': action,
            'result': execution_result,
            'reward': shaped_reward,
            'execution_time': execution_time
        }
        self.bus.publish("issue.resolved", resolution_data)
    
    def display_performance_metrics(self):
        """Display real-time performance metrics"""
        if self.total_issues_handled > 0:
            success_rate = (self.successful_resolutions / self.total_issues_handled) * 100
            uptime = time.time() - self.start_time
            
            print(f"\n📊 SYSTEM PERFORMANCE METRICS")
            print(f"   Issues Handled: {self.total_issues_handled}")
            print(f"   Success Rate: {success_rate:.1f}%")
            print(f"   System Uptime: {uptime/60:.1f} minutes")
            
            # Get RL performance metrics
            rl_metrics = self.smart_agent.get_performance_metrics()
            if rl_metrics.get("status") != "no_data":
                print(f"   Average Reward: {rl_metrics.get('average_reward', 0):.3f}")
                print(f"   Reward Trend: {rl_metrics.get('reward_trend', 0):.3f}")
                print(f"   Total RL Actions: {rl_metrics.get('total_actions', 0)}")
    
    def start_real_monitoring(self):
        """Start real deployment monitoring"""
        print("\n🔍 Starting Real Deployment Monitoring...")
        
        # Start deployment monitor in background thread
        monitor_thread = threading.Thread(
            target=self.deployment_monitor.monitor_deployment_health,
            daemon=True
        )
        monitor_thread.start()
        
        print("✅ Real deployment monitoring active")
        return monitor_thread
    
    def simulate_production_scenarios(self):
        """Simulate realistic production failure scenarios"""
        print("\n🧪 Running Production Scenario Simulations...")
        
        scenarios = [
            'service_timeout',
            'database_connection_lost', 
            'high_memory_usage'
        ]
        
        for scenario in scenarios:
            print(f"\n🎭 Simulating: {scenario}")
            self.deployment_monitor.simulate_real_failure(scenario)
            time.sleep(5)  # Wait between scenarios
    
    def interactive_production_mode(self):
        """Interactive mode for production system management"""
        while True:
            print("\n" + "="*50)
            print("🏭 PRODUCTION INTELLIGENT SYSTEM")
            print("="*50)
            print("1. View System Status")
            print("2. Simulate Production Failure")
            print("3. View Performance Metrics") 
            print("4. Test Action Execution")
            print("5. View RL Learning Progress")
            print("0. Exit")
            
            choice = input("\nSelect option (0-5): ").strip()
            
            if choice == "1":
                self.display_performance_metrics()
                
            elif choice == "2":
                print("\nAvailable failure scenarios:")
                print("1. service_timeout")
                print("2. database_connection_lost")
                print("3. high_memory_usage")
                
                scenario_choice = input("Select scenario (1-3): ").strip()
                scenarios = ['service_timeout', 'database_connection_lost', 'high_memory_usage']
                
                if scenario_choice in ['1', '2', '3']:
                    scenario = scenarios[int(scenario_choice) - 1]
                    self.deployment_monitor.simulate_real_failure(scenario)
                else:
                    print("❌ Invalid scenario")
                    
            elif choice == "3":
                rl_metrics = self.smart_agent.get_performance_metrics()
                print(f"\n📈 DETAILED PERFORMANCE METRICS")
                for key, value in rl_metrics.items():
                    print(f"   {key}: {value}")
                    
            elif choice == "4":
                action = input("Enter action to test: ").strip()
                service = input("Enter service name: ").strip()
                
                context = {'service': service}
                result = self.action_executor.execute_action(action, context)
                print(f"🔧 Test Result: {result}")
                
            elif choice == "5":
                print("\n🧠 RL LEARNING PROGRESS")
                # Display Q-table summary
                states_count = len(self.smart_agent.q_table)
                total_actions = sum(len(actions) for actions in self.smart_agent.q_table.values())
                print(f"   States Learned: {states_count}")
                print(f"   Total State-Action Pairs: {total_actions}")
                print(f"   Exploration Rate: {self.smart_agent.epsilon}")
                
            elif choice == "0":
                print("👋 Shutting down production system...")
                break
            else:
                print("❌ Invalid option!")

def main():
    """Main entry point for production system"""
    print("🏭 PRODUCTION INTELLIGENT DEPLOYMENT SYSTEM")
    print("=" * 60)
    
    # Initialize production system
    system = ProductionIntelligentSystem()
    
    # Start real monitoring
    monitor_thread = system.start_real_monitoring()
    
    print("\n🎯 System Ready for Production Deployment Issues!")
    print("💡 The system will now monitor real deployments and learn from actual failures.")
    
    try:
        # Run interactive mode
        system.interactive_production_mode()
        
    except KeyboardInterrupt:
        print("\n🛑 System shutdown requested...")
    
    print("✅ Production system stopped.")

if __name__ == "__main__":
    main()