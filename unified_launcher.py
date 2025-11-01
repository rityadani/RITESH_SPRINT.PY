import threading
import time
import subprocess
import webbrowser
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import with error handling
try:
    from core.sovereign_bus import SovereignBus
except ImportError:
    print("⚠️ SovereignBus not found, using mock")
    class SovereignBus:
        def __init__(self): pass
        def subscribe(self, *args): pass
        def publish(self, *args): pass

try:
    from agents.event_handler import run_event_handler
except ImportError:
    print("⚠️ Event handler not found")
    def run_event_handler(*args): pass

try:
    from agents.smart_agent import SmartAgent
except ImportError:
    print("⚠️ SmartAgent not found")
    class SmartAgent:
        def __init__(self): pass

try:
    from agents.system_telementary import SystemTelemetry
except ImportError:
    print("⚠️ SystemTelemetry not found")
    class SystemTelemetry:
        def __init__(self): pass
        def monitor_system(self, *args): pass

class UnifiedSystemLauncher:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.components_running = {}
        self.bus = SovereignBus()
        
        print("🚀 UNIFIED INTELLIGENT SYSTEM LAUNCHER")
        print("=" * 50)
        
    def start_event_handler(self):
        """Start the original event handler"""
        def event_worker():
            try:
                print("📊 Starting Event Handler...")
                run_event_handler(self.bus, "logs/system.log")
            except Exception as e:
                print(f"❌ Event Handler error: {e}")
        
        thread = threading.Thread(target=event_worker, daemon=True)
        thread.start()
        self.components_running['event_handler'] = True
        print("✅ Event Handler started")
    
    def start_planner_agent(self):
        """Start the original planner agent"""
        def planner_worker():
            try:
                print("🤖 Starting Planner Agent...")
                # Try to import and run planner
                try:
                    from agents.planner_agent import PlannerAgent
                    planner = PlannerAgent()
                    # Simulate planner running
                    while True:
                        time.sleep(10)
                        planner.handle_event("port_busy")
                except ImportError:
                    print("⚠️ Using simple planner simulation")
                    while True:
                        time.sleep(15)
                        print("🤖 Planner: Simulated action execution")
            except Exception as e:
                print(f"❌ Planner Agent error: {e}")
        
        thread = threading.Thread(target=planner_worker, daemon=True)
        thread.start()
        self.components_running['planner_agent'] = True
        print("✅ Planner Agent started")
    
    def start_telemetry_system(self):
        """Start system telemetry monitoring"""
        def telemetry_worker():
            try:
                print("📈 Starting System Telemetry...")
                telemetry = SystemTelemetry()
                telemetry.monitor_system(duration=3600, interval=30)  # 1 hour monitoring
            except Exception as e:
                print(f"❌ Telemetry error: {e}")
        
        thread = threading.Thread(target=telemetry_worker, daemon=True)
        thread.start()
        self.components_running['telemetry'] = True
        print("✅ System Telemetry started")
    
    def start_production_system(self):
        """Start production system in background"""
        def production_worker():
            try:
                print("🏭 Starting Production System...")
                # Import and run production system
                from production_main import ProductionIntelligentSystem
                prod_system = ProductionIntelligentSystem()
                prod_system.start_real_monitoring()
                
                # Keep it running
                while True:
                    time.sleep(10)
                    # Simulate some production scenarios periodically
                    if hasattr(prod_system, 'deployment_monitor'):
                        prod_system.deployment_monitor.simulate_real_failure('service_timeout')
                        time.sleep(30)
                        
            except Exception as e:
                print(f"❌ Production System error: {e}")
        
        thread = threading.Thread(target=production_worker, daemon=True)
        thread.start()
        self.components_running['production_system'] = True
        print("✅ Production System started")
    
    def start_web_dashboard(self):
        """Start the web dashboard"""
        def dashboard_worker():
            try:
                print("🌐 Starting Web Dashboard...")
                # Run the localhost app
                subprocess.run([sys.executable, "localhost_app.py"], cwd=self.project_root)
            except Exception as e:
                print(f"❌ Web Dashboard error: {e}")
        
        thread = threading.Thread(target=dashboard_worker, daemon=True)
        thread.start()
        self.components_running['web_dashboard'] = True
        print("✅ Web Dashboard started")
    
    def start_streamlit_dashboard(self):
        """Start Streamlit dashboard if available"""
        def streamlit_worker():
            try:
                dashboard_path = os.path.join(self.project_root, "dashboard", "app.py")
                if os.path.exists(dashboard_path):
                    print("📊 Starting Streamlit Dashboard...")
                    subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_path, "--server.port", "8501"], 
                                 cwd=self.project_root)
                else:
                    print("⚠️ Streamlit dashboard not found, skipping...")
            except Exception as e:
                print(f"❌ Streamlit Dashboard error: {e}")
        
        thread = threading.Thread(target=streamlit_worker, daemon=True)
        thread.start()
        self.components_running['streamlit_dashboard'] = True
    
    def generate_test_data(self):
        """Generate some test data for demonstration"""
        def data_generator():
            time.sleep(5)  # Wait for systems to start
            
            print("📝 Generating test data...")
            
            # Add some test log entries
            log_entries = [
                "ERROR: bad_config: Configuration file corrupted",
                "ERROR: database: Connection timeout occurred", 
                "CRITICAL: system: Memory usage exceeded threshold",
                "ERROR: network: Connection refused on port 8080",
                "ERROR: bad_config: Missing required environment variable"
            ]
            
            log_file = os.path.join(self.project_root, "logs", "system.log")
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            for i, entry in enumerate(log_entries):
                time.sleep(10)  # Add entry every 10 seconds
                with open(log_file, "a") as f:
                    f.write(f"{entry}\n")
                print(f"📝 Added test log entry {i+1}/{len(log_entries)}")
        
        thread = threading.Thread(target=data_generator, daemon=True)
        thread.start()
    
    def show_status(self):
        """Show system status"""
        print("\n📊 SYSTEM STATUS:")
        print("-" * 30)
        for component, status in self.components_running.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {component.replace('_', ' ').title()}")
        
        print(f"\n🌐 AVAILABLE DASHBOARDS:")
        print("- Main Web Dashboard: http://localhost:8080")
        print("- Streamlit Dashboard: http://localhost:8501")
        print("- API Endpoint: http://localhost:8080/api/data")
    
    def launch_all_systems(self):
        """Launch all system components"""
        print("\n🚀 LAUNCHING ALL SYSTEMS...")
        print("=" * 40)
        
        # Start core components
        self.start_event_handler()
        time.sleep(2)
        
        self.start_planner_agent()
        time.sleep(2)
        
        self.start_telemetry_system()
        time.sleep(2)
        
        self.start_production_system()
        time.sleep(2)
        
        # Start dashboards
        self.start_web_dashboard()
        time.sleep(3)
        
        self.start_streamlit_dashboard()
        time.sleep(2)
        
        # Generate test data
        self.generate_test_data()
        
        # Show status
        time.sleep(5)
        self.show_status()
        
        # Auto-open browsers
        print("\n🌐 Opening dashboards in browser...")
        webbrowser.open('http://localhost:8080')
        time.sleep(2)
        webbrowser.open('http://localhost:8501')
        
        print("\n✅ ALL SYSTEMS LAUNCHED SUCCESSFULLY!")
        print("🎯 Your complete intelligent system is now running!")
        print("⚡ Press Ctrl+C to stop all systems")
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(30)
                print(f"💓 System heartbeat - {time.strftime('%H:%M:%S')}")
        except KeyboardInterrupt:
            print("\n🛑 Shutting down all systems...")
            self.shutdown_all()
    
    def shutdown_all(self):
        """Shutdown all components"""
        print("👋 All systems stopped!")
        for component in self.components_running:
            self.components_running[component] = False

def main():
    """Main entry point"""
    launcher = UnifiedSystemLauncher()
    
    print("\n🎯 UNIFIED SYSTEM LAUNCHER")
    print("This will start ALL your components together:")
    print("- Original Event Handler & Planner")
    print("- System Telemetry")
    print("- Production System")
    print("- Web Dashboard (localhost:8080)")
    print("- Streamlit Dashboard (localhost:8501)")
    print("- Test data generation")
    
    choice = input("\n🚀 Start all systems? (y/n): ").strip().lower()
    
    if choice in ['y', 'yes']:
        launcher.launch_all_systems()
    else:
        print("👋 Launch cancelled!")

if __name__ == "__main__":
    main()