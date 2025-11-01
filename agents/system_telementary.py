import time
import os
import json

class SystemTelemetry:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.telemetry_file = os.path.join(self.project_root, "insightflow", "system_metrics.json")
        self.ensure_telemetry_dir()
    
    def ensure_telemetry_dir(self):
        """Create telemetry directory if it doesn't exist"""
        telemetry_dir = os.path.dirname(self.telemetry_file)
        if not os.path.exists(telemetry_dir):
            os.makedirs(telemetry_dir)

    def get_metrics(self):
        """Get system metrics - simplified version without psutil dependency"""
        try:
            # Try to use psutil if available
            import psutil
            disk_path = "C:\\" if os.name == 'nt' else "/"
            metrics = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage(disk_path).percent,
                "status": "active"
            }
        except ImportError:
            # Fallback metrics without psutil
            metrics = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "cpu_percent": "N/A (psutil not installed)",
                "memory_percent": "N/A (psutil not installed)", 
                "disk_percent": "N/A (psutil not installed)",
                "status": "limited"
            }
        
        return metrics
    
    def log_metrics(self, metrics):
        """Log metrics to file"""
        try:
            with open(self.telemetry_file, "a") as f:
                f.write(json.dumps(metrics) + "\n")
        except Exception as e:
            print(f"Error logging metrics: {e}")
    
    def monitor_system(self, duration=60, interval=5):
        """Monitor system for specified duration"""
        print(f"🔍 Starting system monitoring for {duration} seconds...")
        start_time = time.time()
        
        while time.time() - start_time < duration:
            metrics = self.get_metrics()
            self.log_metrics(metrics)
            print(f"📊 {metrics}")
            time.sleep(interval)
        
        print("✅ Monitoring completed!")

if __name__ == "__main__":
    telemetry = SystemTelemetry()
    
    print("System Telemetry Options:")
    print("1. Single metrics check")
    print("2. Continuous monitoring (60 seconds)")
    print("3. Custom monitoring")
    
    choice = input("Select option (1-3): ").strip()
    
    if choice == "1":
        metrics = telemetry.get_metrics()
        print(f"📊 Current metrics: {metrics}")
    elif choice == "2":
        telemetry.monitor_system(duration=60, interval=5)
    elif choice == "3":
        duration = int(input("Duration (seconds): ") or 30)
        interval = int(input("Interval (seconds): ") or 2)
        telemetry.monitor_system(duration=duration, interval=interval)
    else:
        print("Invalid option")
