import http.server
import socketserver
import threading
import webbrowser
import json
import csv
import os
import time
from urllib.parse import urlparse, parse_qs

# Import your system components
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.sovereign_bus import SovereignBus
from agents.smart_agent import SmartAgent

class IntelligentSystemWebApp:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.bus = SovereignBus()
        self.smart_agent = SmartAgent()
        self.system_running = False
        self.issues_handled = 0
        self.success_count = 0
        
        # Start background system
        self.start_background_system()
    
    def start_background_system(self):
        """Start the intelligent system in background"""
        def background_worker():
            self.system_running = True
            print("🤖 Background intelligent system started...")
            
            while self.system_running:
                # Simulate periodic system checks
                time.sleep(10)
                
                # Simulate random issues for demo
                import random
                if random.random() < 0.3:  # 30% chance of issue
                    self.simulate_issue()
        
        thread = threading.Thread(target=background_worker, daemon=True)
        thread.start()
    
    def simulate_issue(self):
        """Simulate a system issue for demo"""
        issues = [
            {"error_type": "port_busy", "service": "web_server", "severity": "medium"},
            {"error_type": "api_down", "service": "api_service", "severity": "high"},
            {"error_type": "config_error", "service": "database", "severity": "critical"}
        ]
        
        issue = issues[self.issues_handled % len(issues)]
        self.issues_handled += 1
        
        # Use smart agent to choose action
        action = self.smart_agent.choose_action(issue["error_type"])
        
        # Simulate execution (always success for demo)
        success = True
        self.success_count += 1 if success else 0
        
        # Update RL agent
        reward = 1 if success else -1
        self.smart_agent.update(issue["error_type"], action, reward)
        
        print(f"🚨 Issue: {issue['error_type']} → Action: {action} → {'✅' if success else '❌'}")
    
    def get_system_data(self):
        """Get current system data"""
        # Load RL table
        rl_data = []
        rl_path = os.path.join(self.project_root, "data", "rl_table.csv")
        try:
            if os.path.exists(rl_path):
                with open(rl_path, 'r') as f:
                    reader = csv.DictReader(f)
                    rl_data = list(reader)
        except:
            pass
        
        # Load planner logs
        log_data = []
        log_path = os.path.join(self.project_root, "logs", "planner_log.csv")
        try:
            if os.path.exists(log_path):
                with open(log_path, 'r') as f:
                    reader = csv.DictReader(f)
                    log_data = list(reader)
        except:
            pass
        
        success_rate = (self.success_count / max(self.issues_handled, 1)) * 100
        
        return {
            'stats': {
                'total_actions': len(rl_data),
                'issues_handled': self.issues_handled,
                'success_rate': round(success_rate, 1),
                'system_status': 'Running' if self.system_running else 'Stopped'
            },
            'rl_table': rl_data[-10:],
            'recent_logs': log_data[-10:],
            'live_data': {
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'uptime': f"{(time.time() - self.start_time) / 60:.1f} min" if hasattr(self, 'start_time') else "0 min"
            }
        }

class WebAppHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, app=None, **kwargs):
        self.app = app
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/' or parsed_path.path == '/dashboard':
            self.send_dashboard()
        elif parsed_path.path == '/api/data':
            self.send_api_data()
        elif parsed_path.path == '/api/trigger-issue':
            self.trigger_issue()
        else:
            self.send_response(404)
            self.end_headers()
    
    def send_dashboard(self):
        html = self.generate_dashboard_html()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_api_data(self):
        data = self.app.get_system_data()
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def trigger_issue(self):
        self.app.simulate_issue()
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "issue_triggered"}).encode())
    
    def generate_dashboard_html(self):
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Intelligent System - Live Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { 
            text-align: center; 
            color: white; 
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .header h1 { font-size: 3em; margin-bottom: 10px; }
        .header p { font-size: 1.3em; opacity: 0.9; }
        
        .controls { 
            text-align: center; 
            margin-bottom: 30px; 
        }
        .btn { 
            background: #28a745; 
            color: white; 
            border: none; 
            padding: 15px 30px; 
            border-radius: 25px; 
            cursor: pointer; 
            font-size: 1.1em;
            margin: 0 10px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.3); }
        .btn-danger { background: #dc3545; }
        .btn-info { background: #17a2b8; }
        
        .stats-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }
        .stat-card { 
            background: white; 
            padding: 25px; 
            border-radius: 15px; 
            text-align: center;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .stat-card:hover { transform: translateY(-5px); }
        .stat-number { 
            font-size: 2.5em; 
            font-weight: bold; 
            margin-bottom: 10px;
        }
        .stat-label { 
            color: #666; 
            font-size: 1.1em; 
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .running { color: #28a745; }
        .stopped { color: #dc3545; }
        
        .content-grid { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 30px; 
        }
        .card { 
            background: white; 
            padding: 25px; 
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }
        .card h2 { 
            color: #333; 
            margin-bottom: 20px; 
            font-size: 1.5em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        
        .table { 
            width: 100%; 
            border-collapse: collapse; 
        }
        .table th, .table td { 
            padding: 12px; 
            text-align: left; 
            border-bottom: 1px solid #eee; 
        }
        .table th { 
            background: #f8f9fa; 
            font-weight: 600;
        }
        .table tr:hover { background: #f8f9fa; }
        
        .live-indicator { 
            display: inline-block; 
            width: 12px; 
            height: 12px; 
            background: #28a745; 
            border-radius: 50%; 
            animation: pulse 2s infinite;
            margin-right: 8px;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .full-width { grid-column: 1 / -1; }
        .status-running { color: #28a745; font-weight: bold; }
        .status-stopped { color: #dc3545; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Intelligent System Dashboard</h1>
            <p><span class="live-indicator"></span>Live Production Monitoring & AI Learning</p>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="triggerIssue()">🚨 Trigger Test Issue</button>
            <button class="btn btn-info" onclick="refreshData()">🔄 Refresh Data</button>
            <button class="btn btn-danger" onclick="location.reload()">⚡ Full Reload</button>
        </div>
        
        <div class="stats-grid" id="statsGrid">
            <!-- Stats will be loaded here -->
        </div>
        
        <div class="content-grid">
            <div class="card">
                <h2>🤖 Q-Learning Progress</h2>
                <div id="rlTable">Loading...</div>
            </div>
            
            <div class="card">
                <h2>📋 Live Activity Log</h2>
                <div id="activityLog">Loading...</div>
            </div>
        </div>
    </div>
    
    <script>
        let refreshInterval;
        
        function loadData() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    updateStats(data.stats);
                    updateRLTable(data.rl_table);
                    updateActivityLog(data.recent_logs);
                })
                .catch(error => console.error('Error:', error));
        }
        
        function updateStats(stats) {
            const statsGrid = document.getElementById('statsGrid');
            statsGrid.innerHTML = `
                <div class="stat-card">
                    <div class="stat-number running">${stats.total_actions}</div>
                    <div class="stat-label">Actions Learned</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.issues_handled}</div>
                    <div class="stat-label">Issues Handled</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number running">${stats.success_rate}%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number ${stats.system_status === 'Running' ? 'running' : 'stopped'}">${stats.system_status}</div>
                    <div class="stat-label">System Status</div>
                </div>
            `;
        }
        
        function updateRLTable(rlData) {
            const rlTable = document.getElementById('rlTable');
            if (rlData.length === 0) {
                rlTable.innerHTML = '<p>No Q-learning data available yet.</p>';
                return;
            }
            
            let html = '<table class="table"><tr><th>State</th><th>Action</th><th>Q-Value</th></tr>';
            rlData.forEach(row => {
                html += `<tr><td>${row.state || 'N/A'}</td><td>${row.action || 'N/A'}</td><td>${row.q_value || 'N/A'}</td></tr>`;
            });
            html += '</table>';
            rlTable.innerHTML = html;
        }
        
        function updateActivityLog(logs) {
            const activityLog = document.getElementById('activityLog');
            if (logs.length === 0) {
                activityLog.innerHTML = '<p>No activity logs available yet.</p>';
                return;
            }
            
            let html = '<table class="table"><tr><th>Time</th><th>Action</th><th>Result</th></tr>';
            logs.forEach(log => {
                const time = log.timestamp ? log.timestamp.split(' ')[1] : 'N/A';
                const resultClass = log.result === 'True' ? 'status-running' : 'status-stopped';
                const resultIcon = log.result === 'True' ? '✅' : '❌';
                html += `<tr><td>${time}</td><td>${log.action || 'N/A'}</td><td class="${resultClass}">${resultIcon}</td></tr>`;
            });
            html += '</table>';
            activityLog.innerHTML = html;
        }
        
        function triggerIssue() {
            fetch('/api/trigger-issue')
                .then(response => response.json())
                .then(data => {
                    console.log('Issue triggered:', data);
                    setTimeout(loadData, 1000); // Refresh after 1 second
                });
        }
        
        function refreshData() {
            loadData();
        }
        
        // Initial load and auto-refresh
        loadData();
        refreshInterval = setInterval(loadData, 5000); // Refresh every 5 seconds
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', () => {
            if (refreshInterval) clearInterval(refreshInterval);
        });
    </script>
</body>
</html>
        """

def create_handler_with_app(app):
    def handler(*args, **kwargs):
        return WebAppHandler(*args, app=app, **kwargs)
    return handler

def main():
    PORT = 8080
    
    print("🚀 Starting Complete Intelligent System Web Application...")
    print("=" * 60)
    
    # Initialize the intelligent system
    app = IntelligentSystemWebApp()
    app.start_time = time.time()
    
    # Create HTTP server with custom handler
    handler = create_handler_with_app(app)
    
    try:
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            print(f"🌐 Web Application running at: http://localhost:{PORT}")
            print(f"📊 Dashboard available at: http://localhost:{PORT}/dashboard")
            print(f"🔗 API endpoint: http://localhost:{PORT}/api/data")
            print("🤖 Background AI system is running...")
            print("⚡ Press Ctrl+C to stop")
            print("=" * 60)
            
            # Auto-open browser
            webbrowser.open(f'http://localhost:{PORT}')
            
            # Start server
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n👋 Intelligent System Web Application stopped!")
        app.system_running = False

if __name__ == "__main__":
    main()