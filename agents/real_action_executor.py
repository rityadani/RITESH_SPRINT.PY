import subprocess
import time
import os
import json
from datetime import datetime

# Optional imports
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    requests = None
    REQUESTS_AVAILABLE = False

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    docker = None
    DOCKER_AVAILABLE = False

class RealActionExecutor:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.execution_log = os.path.join(self.project_root, "logs", "action_execution.log")
        self.load_execution_config()
        
        # Initialize Docker client if available
        if DOCKER_AVAILABLE:
            try:
                self.docker_client = docker.from_env()
                self.docker_available = True
            except:
                self.docker_client = None
                self.docker_available = False
                print("⚠️ Docker daemon not running - container actions will be simulated")
        else:
            self.docker_client = None
            self.docker_available = False
            print("⚠️ Docker module not installed - container actions will be simulated")

    def load_execution_config(self):
        """Load real execution configurations"""
        config_path = os.path.join(self.project_root, "config", "execution_config.json")
        
        default_config = {
            "services": {
                "web_server": {
                    "restart_command": "systemctl restart nginx",
                    "status_command": "systemctl status nginx",
                    "config_path": "/etc/nginx/nginx.conf",
                    "log_path": "/var/log/nginx/error.log"
                },
                "database": {
                    "restart_command": "systemctl restart postgresql",
                    "status_command": "systemctl status postgresql", 
                    "config_path": "/etc/postgresql/postgresql.conf",
                    "backup_command": "pg_dump -U postgres mydb > backup.sql"
                },
                "api_service": {
                    "restart_command": "pm2 restart api-service",
                    "status_command": "pm2 status api-service",
                    "config_path": "./config/api.json",
                    "log_path": "./logs/api.log"
                }
            },
            "containers": {
                "web_container": "nginx-container",
                "api_container": "api-service-container", 
                "db_container": "postgres-container"
            },
            "network": {
                "interface": "eth0",
                "dns_servers": ["8.8.8.8", "1.1.1.1"]
            }
        }
        
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            if not os.path.exists(config_path):
                with open(config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
            
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"Config error: {e}")
            self.config = default_config

    def log_execution(self, action, result, details):
        """Log real action execution results"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "result": result,
            "details": details
        }
        
        try:
            os.makedirs(os.path.dirname(self.execution_log), exist_ok=True)
            with open(self.execution_log, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"Logging error: {e}")

    def execute_restart_service_graceful(self, service_name):
        """Gracefully restart a system service"""
        start_time = time.time()
        
        try:
            service_config = self.config["services"].get(service_name, {})
            restart_cmd = service_config.get("restart_command", f"systemctl restart {service_name}")
            
            print(f"🔄 Gracefully restarting {service_name}...")
            
            # Check service status first
            status_cmd = service_config.get("status_command", f"systemctl status {service_name}")
            status_result = subprocess.run(status_cmd, shell=True, capture_output=True, text=True)
            
            # Perform graceful restart
            restart_result = subprocess.run(restart_cmd, shell=True, capture_output=True, text=True)
            
            execution_time = time.time() - start_time
            
            if restart_result.returncode == 0:
                result = {
                    "success": True,
                    "execution_time": execution_time,
                    "message": f"Service {service_name} restarted successfully",
                    "output": restart_result.stdout
                }
            else:
                result = {
                    "success": False,
                    "execution_time": execution_time,
                    "message": f"Failed to restart {service_name}",
                    "error": restart_result.stderr
                }
            
            self.log_execution("restart_service_graceful", result["success"], result)
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            result = {
                "success": False,
                "execution_time": execution_time,
                "message": f"Exception during restart: {str(e)}",
                "error": str(e)
            }
            self.log_execution("restart_service_graceful", False, result)
            return result

    def execute_restart_container(self, container_name):
        """Restart Docker container"""
        start_time = time.time()
        
        if not self.docker_available:
            return {
                "success": False,
                "execution_time": 0,
                "message": "Docker not available",
                "error": "Docker client not initialized"
            }
        
        try:
            print(f"🐳 Restarting container {container_name}...")
            
            container = self.docker_client.containers.get(container_name)
            container.restart()
            
            # Wait for container to be healthy
            time.sleep(2)
            container.reload()
            
            execution_time = time.time() - start_time
            
            result = {
                "success": container.status == "running",
                "execution_time": execution_time,
                "message": f"Container {container_name} restarted",
                "status": container.status
            }
            
            self.log_execution("restart_container", result["success"], result)
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            result = {
                "success": False,
                "execution_time": execution_time,
                "message": f"Failed to restart container: {str(e)}",
                "error": str(e)
            }
            self.log_execution("restart_container", False, result)
            return result

    def execute_scale_horizontal(self, service_name, target_instances=3):
        """Scale service horizontally"""
        start_time = time.time()
        
        try:
            print(f"📈 Scaling {service_name} to {target_instances} instances...")
            
            if self.docker_available:
                # Docker Swarm scaling
                scale_cmd = f"docker service scale {service_name}={target_instances}"
                result = subprocess.run(scale_cmd, shell=True, capture_output=True, text=True)
                
                execution_time = time.time() - start_time
                
                if result.returncode == 0:
                    response = {
                        "success": True,
                        "execution_time": execution_time,
                        "message": f"Scaled {service_name} to {target_instances} instances",
                        "output": result.stdout
                    }
                else:
                    response = {
                        "success": False,
                        "execution_time": execution_time,
                        "message": f"Failed to scale {service_name}",
                        "error": result.stderr
                    }
            else:
                # Simulate scaling
                time.sleep(1)  # Simulate scaling time
                execution_time = time.time() - start_time
                response = {
                    "success": True,
                    "execution_time": execution_time,
                    "message": f"Simulated scaling {service_name} to {target_instances} instances",
                    "simulated": True
                }
            
            self.log_execution("scale_horizontal", response["success"], response)
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            result = {
                "success": False,
                "execution_time": execution_time,
                "message": f"Scaling failed: {str(e)}",
                "error": str(e)
            }
            self.log_execution("scale_horizontal", False, result)
            return result

    def execute_rollback_deployment(self, service_name):
        """Rollback to previous deployment version"""
        start_time = time.time()
        
        try:
            print(f"⏪ Rolling back deployment for {service_name}...")
            
            # Git-based rollback
            rollback_commands = [
                "git log --oneline -n 5",  # Show recent commits
                "git reset --hard HEAD~1",  # Rollback to previous commit
                f"docker-compose up -d {service_name}"  # Redeploy
            ]
            
            results = []
            for cmd in rollback_commands:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                results.append({
                    "command": cmd,
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                })
            
            execution_time = time.time() - start_time
            
            # Check if all commands succeeded
            success = all(r["returncode"] == 0 for r in results)
            
            response = {
                "success": success,
                "execution_time": execution_time,
                "message": f"Rollback {'completed' if success else 'failed'} for {service_name}",
                "commands_executed": results
            }
            
            self.log_execution("rollback_deployment", success, response)
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            result = {
                "success": False,
                "execution_time": execution_time,
                "message": f"Rollback failed: {str(e)}",
                "error": str(e)
            }
            self.log_execution("rollback_deployment", False, result)
            return result

    def execute_reset_connection_pool(self, service_name):
        """Reset database connection pool"""
        start_time = time.time()
        
        try:
            print(f"🔄 Resetting connection pool for {service_name}...")
            
            # Send SIGHUP to reload configuration
            reload_cmd = f"pkill -HUP -f {service_name}"
            result = subprocess.run(reload_cmd, shell=True, capture_output=True, text=True)
            
            execution_time = time.time() - start_time
            
            response = {
                "success": result.returncode == 0,
                "execution_time": execution_time,
                "message": f"Connection pool reset for {service_name}",
                "output": result.stdout if result.returncode == 0 else result.stderr
            }
            
            self.log_execution("reset_connection_pool", response["success"], response)
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            result = {
                "success": False,
                "execution_time": execution_time,
                "message": f"Connection pool reset failed: {str(e)}",
                "error": str(e)
            }
            self.log_execution("reset_connection_pool", False, result)
            return result

    def execute_action(self, action, context=None):
        """Execute real deployment action based on action type"""
        context = context or {}
        service_name = context.get('service', 'default_service')
        
        action_map = {
            "restart_service_graceful": lambda: self.execute_restart_service_graceful(service_name),
            "restart_service_force": lambda: self.execute_restart_service_graceful(service_name),
            "restart_container": lambda: self.execute_restart_container(service_name),
            "scale_horizontal": lambda: self.execute_scale_horizontal(service_name),
            "rollback_deployment": lambda: self.execute_rollback_deployment(service_name),
            "reset_connection_pool": lambda: self.execute_reset_connection_pool(service_name),
        }
        
        if action in action_map:
            return action_map[action]()
        else:
            # Default action for unknown actions
            return {
                "success": False,
                "execution_time": 0,
                "message": f"Unknown action: {action}",
                "error": f"Action '{action}' not implemented"
            }

if __name__ == "__main__":
    executor = RealActionExecutor()
    
    # Test real action execution
    test_context = {"service": "web_server"}
    result = executor.execute_action("restart_service_graceful", test_context)
    
    print(f"🔧 Execution Result: {result}")