import subprocess
import socket
import time
import json
import os
from datetime import datetime

# Optional requests import
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    requests = None
    REQUESTS_AVAILABLE = False

class RealDeploymentMonitor:
    def __init__(self, bus):
        self.bus = bus
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_file = os.path.join(self.project_root, "config", "deployment_config.json")
        self.load_deployment_config()
        
    def load_deployment_config(self):
        """Load real deployment endpoints and services to monitor"""
        default_config = {
            "services": [
                {"name": "web_server", "url": "http://localhost:8080/health", "type": "http"},
                {"name": "database", "host": "localhost", "port": 5432, "type": "tcp"},
                {"name": "redis", "host": "localhost", "port": 6379, "type": "tcp"},
                {"name": "api_service", "url": "http://localhost:3000/api/health", "type": "http"}
            ],
            "system_processes": [
                {"name": "nginx", "process": "nginx"},
                {"name": "postgres", "process": "postgres"},
                {"name": "docker", "process": "docker"}
            ],
            "file_monitors": [
                {"name": "app_logs", "path": "logs/app.log"},
                {"name": "error_logs", "path": "logs/error.log"},
                {"name": "nginx_logs", "path": "/var/log/nginx/error.log"}
            ]
        }
        
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            if not os.path.exists(self.config_file):
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
            
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"Config error: {e}, using defaults")
            self.config = default_config

    def check_http_service(self, service):
        """Check HTTP service health"""
        if not REQUESTS_AVAILABLE:
            return {"status": "skipped", "error": "requests module not available"}
        
        try:
            response = requests.get(service['url'], timeout=5)
            if response.status_code == 200:
                return {"status": "healthy", "response_time": response.elapsed.total_seconds()}
            else:
                return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"status": "failed", "error": str(e)}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def check_tcp_service(self, service):
        """Check TCP service connectivity"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((service['host'], service['port']))
            sock.close()
            
            if result == 0:
                return {"status": "healthy", "port": service['port']}
            else:
                return {"status": "unreachable", "error": f"Port {service['port']} closed"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def check_process_status(self, process_config):
        """Check if system process is running"""
        try:
            if os.name == 'nt':  # Windows
                cmd = f'tasklist /FI "IMAGENAME eq {process_config["process"]}.exe"'
            else:  # Linux/Mac
                cmd = f'pgrep {process_config["process"]}'
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0 and process_config["process"] in result.stdout:
                return {"status": "running", "process": process_config["process"]}
            else:
                return {"status": "stopped", "process": process_config["process"]}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def monitor_deployment_health(self):
        """Continuously monitor real deployment health"""
        print("🔍 Starting real deployment monitoring...")
        
        while True:
            deployment_issues = []
            
            # Check HTTP services
            for service in self.config.get('services', []):
                if service['type'] == 'http':
                    result = self.check_http_service(service)
                    if result['status'] != 'healthy':
                        issue = {
                            'error_type': 'service_down',
                            'service': service['name'],
                            'details': result,
                            'severity': 'critical',
                            'timestamp': datetime.now().isoformat()
                        }
                        deployment_issues.append(issue)
                        
                elif service['type'] == 'tcp':
                    result = self.check_tcp_service(service)
                    if result['status'] != 'healthy':
                        issue = {
                            'error_type': 'port_unreachable',
                            'service': service['name'],
                            'details': result,
                            'severity': 'high',
                            'timestamp': datetime.now().isoformat()
                        }
                        deployment_issues.append(issue)
            
            # Check system processes
            for process in self.config.get('system_processes', []):
                result = self.check_process_status(process)
                if result['status'] != 'running':
                    issue = {
                        'error_type': 'process_down',
                        'service': process['name'],
                        'details': result,
                        'severity': 'critical',
                        'timestamp': datetime.now().isoformat()
                    }
                    deployment_issues.append(issue)
            
            # Publish real deployment issues
            for issue in deployment_issues:
                print(f"🚨 REAL DEPLOYMENT ISSUE: {issue}")
                self.bus.publish("deployment.issue.detected", issue)
            
            if not deployment_issues:
                print("✅ All services healthy")
            
            time.sleep(30)  # Check every 30 seconds

    def simulate_real_failure(self, failure_type):
        """Simulate real deployment failures for testing"""
        real_failures = {
            'service_timeout': {
                'error_type': 'service_timeout',
                'service': 'api_service',
                'details': {'status': 'timeout', 'error': 'Connection timeout after 5s'},
                'severity': 'high',
                'timestamp': datetime.now().isoformat()
            },
            'database_connection_lost': {
                'error_type': 'database_connection_lost',
                'service': 'postgres',
                'details': {'status': 'connection_failed', 'error': 'FATAL: database connection lost'},
                'severity': 'critical',
                'timestamp': datetime.now().isoformat()
            },
            'high_memory_usage': {
                'error_type': 'resource_exhaustion',
                'service': 'web_server',
                'details': {'status': 'resource_limit', 'memory_usage': '95%'},
                'severity': 'critical',
                'timestamp': datetime.now().isoformat()
            }
        }
        
        if failure_type in real_failures:
            issue = real_failures[failure_type]
            print(f"🧪 SIMULATING REAL FAILURE: {issue}")
            self.bus.publish("deployment.issue.detected", issue)
            return issue
        else:
            print(f"❌ Unknown failure type: {failure_type}")
            return None