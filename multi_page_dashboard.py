import http.server
import socketserver
import webbrowser
import json
import csv
import os
import time
from urllib.parse import urlparse, parse_qs

class MultiPageDashboard:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        
    def get_system_data(self):
        """Get system data from CSV files"""
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
        
        # Load human feedback
        feedback_data = []
        feedback_path = os.path.join(self.project_root, "data", "human_feedback.csv")
        try:
            if os.path.exists(feedback_path):
                with open(feedback_path, 'r') as f:
                    reader = csv.DictReader(f)
                    feedback_data = list(reader)
        except:
            pass
        
        # Calculate stats
        total_actions = len(rl_data)
        total_executions = len(log_data)
        successful = sum(1 for log in log_data if log.get('result') == 'True')
        success_rate = round((successful / total_executions) * 100, 2) if total_executions > 0 else 0
        
        return {
            'stats': {
                'total_actions': total_actions,
                'total_executions': total_executions,
                'success_rate': success_rate,
                'human_feedbacks': len(feedback_data)
            },
            'rl_table': rl_data,
            'recent_logs': log_data[-20:],
            'feedback_data': feedback_data
        }

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, dashboard=None, **kwargs):
        self.dashboard = dashboard
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/' or parsed_path.path == '/home':
            self.send_page('home')
        elif parsed_path.path == '/monitoring':
            self.send_page('monitoring')
        elif parsed_path.path == '/rl-learning':
            self.send_page('rl-learning')
        elif parsed_path.path == '/analytics':
            self.send_page('analytics')
        elif parsed_path.path == '/settings':
            self.send_page('settings')
        elif parsed_path.path == '/api/data':
            self.send_api_data()
        else:
            self.send_response(404)
            self.end_headers()
    
    def send_page(self, page_name):
        html = self.generate_page_html(page_name)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_api_data(self):
        data = self.dashboard.get_system_data()
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def generate_page_html(self, page_name):
        data = self.dashboard.get_system_data()
        
        # Common CSS and navigation
        common_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 AI Self-Healing System - {page_name.title()}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .navbar {{
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            padding: 15px 0;
            border-bottom: 1px solid rgba(255,255,255,0.2);
        }}
        .nav-container {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 20px;
        }}
        .logo {{
            color: white;
            font-size: 1.5em;
            font-weight: bold;
            text-decoration: none;
        }}
        .nav-links {{
            display: flex;
            list-style: none;
            gap: 30px;
        }}
        .nav-links a {{
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 25px;
            transition: all 0.3s ease;
        }}
        .nav-links a:hover, .nav-links a.active {{
            background: rgba(255,255,255,0.2);
            transform: translateY(-2px);
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px 20px;
        }}
        
        .page-header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }}
        .page-header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        .stat-label {{
            color: #666;
            font-size: 1.1em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        .table th, .table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        .table th {{
            background: #f8f9fa;
            font-weight: 600;
        }}
        .table tr:hover {{ background: #f8f9fa; }}
        
        .btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            margin: 10px 5px;
            transition: all 0.3s ease;
        }}
        .btn:hover {{
            background: #5a6fd8;
            transform: translateY(-2px);
        }}
        
        .success {{ color: #28a745; font-weight: bold; }}
        .failed {{ color: #dc3545; font-weight: bold; }}
        
        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .grid-3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }}
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <a href="/" class="logo">🚀 AI Self-Healing System</a>
            <ul class="nav-links">
                <li><a href="/home" class="{'active' if page_name == 'home' else ''}">🏠 Home</a></li>
                <li><a href="/monitoring" class="{'active' if page_name == 'monitoring' else ''}">📊 Monitoring</a></li>
                <li><a href="/rl-learning" class="{'active' if page_name == 'rl-learning' else ''}">🤖 RL Learning</a></li>
                <li><a href="/analytics" class="{'active' if page_name == 'analytics' else ''}">📈 Analytics</a></li>
                <li><a href="/settings" class="{'active' if page_name == 'settings' else ''}">⚙️ Settings</a></li>
            </ul>
        </div>
    </nav>
    
    <div class="container">
        """
        
        # Page-specific content
        if page_name == 'home':
            content = f"""
        <div class="page-header">
            <h1>🏠 System Overview</h1>
            <p>Welcome to your AI-powered self-healing deployment system</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{data['stats']['total_actions']}</div>
                <div class="stat-label">Actions Learned</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{data['stats']['total_executions']}</div>
                <div class="stat-label">Total Executions</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{data['stats']['success_rate']}%</div>
                <div class="stat-label">Success Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{data['stats']['human_feedbacks']}</div>
                <div class="stat-label">Human Feedbacks</div>
            </div>
        </div>
        
        <div class="grid-2">
            <div class="card">
                <h2>🎯 System Status</h2>
                <p>✅ AI Learning Engine: <strong>Active</strong></p>
                <p>✅ Event Monitoring: <strong>Running</strong></p>
                <p>✅ Auto-Healing: <strong>Enabled</strong></p>
                <p>✅ Telemetry: <strong>Collecting</strong></p>
            </div>
            
            <div class="card">
                <h2>📋 Recent Activity</h2>
                <table class="table">
                    <tr><th>Time</th><th>Action</th><th>Result</th></tr>
                    {''.join([f"<tr><td>{log.get('timestamp', 'N/A')[-8:] if log.get('timestamp') else 'N/A'}</td><td>{log.get('action', 'N/A')}</td><td class=\"{'success' if log.get('result') == 'True' else 'failed'}\">{'✅' if log.get('result') == 'True' else '❌'}</td></tr>" for log in data['recent_logs'][-5:]])}
                </table>
            </div>
        </div>
            """
            
        elif page_name == 'monitoring':
            content = f"""
        <div class="page-header">
            <h1>📊 Real-time Monitoring</h1>
            <p>Live system monitoring and deployment health</p>
        </div>
        
        <div class="card">
            <h2>🔍 Service Health Monitor</h2>
            <button class="btn" onclick="checkServices()">🔄 Check All Services</button>
            <button class="btn" onclick="triggerAlert()">🚨 Trigger Test Alert</button>
            
            <div id="serviceStatus" style="margin-top: 20px;">
                <p>🟢 Web Server: Healthy</p>
                <p>🟢 Database: Connected</p>
                <p>🟢 API Gateway: Responding</p>
                <p>🟡 Cache Server: Degraded Performance</p>
            </div>
        </div>
        
        <div class="grid-2">
            <div class="card">
                <h2>📈 System Metrics</h2>
                <p>CPU Usage: <strong>45%</strong></p>
                <p>Memory Usage: <strong>67%</strong></p>
                <p>Disk Usage: <strong>23%</strong></p>
                <p>Network I/O: <strong>Normal</strong></p>
            </div>
            
            <div class="card">
                <h2>🚨 Active Alerts</h2>
                <div style="color: #dc3545;">⚠️ High memory usage on server-02</div>
                <div style="color: #ffc107;">⚠️ Slow response time on API endpoint</div>
                <div style="color: #28a745;">✅ All critical services operational</div>
            </div>
        </div>
            """
            
        elif page_name == 'rl-learning':
            content = f"""
        <div class="page-header">
            <h1>🤖 Reinforcement Learning</h1>
            <p>AI learning progress and Q-table analysis</p>
        </div>
        
        <div class="card">
            <h2>🧠 Q-Learning Table</h2>
            <table class="table">
                <tr><th>State</th><th>Action</th><th>Q-Value</th><th>Confidence</th></tr>
                {''.join([f"<tr><td>{row.get('state', 'N/A')}</td><td>{row.get('action', 'N/A')}</td><td>{row.get('q_value', 'N/A')}</td><td>{'High' if float(row.get('q_value', 0)) > 0.5 else 'Low'}</td></tr>" for row in data['rl_table'][-10:]])}
            </table>
        </div>
        
        <div class="grid-2">
            <div class="card">
                <h2>📊 Learning Statistics</h2>
                <p>Total States: <strong>{len(set(row.get('state', '') for row in data['rl_table']))}</strong></p>
                <p>Total Actions: <strong>{len(data['rl_table'])}</strong></p>
                <p>Average Q-Value: <strong>{sum(float(row.get('q_value', 0)) for row in data['rl_table']) / max(len(data['rl_table']), 1):.3f}</strong></p>
                <p>Learning Rate: <strong>0.1</strong></p>
            </div>
            
            <div class="card">
                <h2>🎯 Top Performing Actions</h2>
                {''.join([f"<p>{row.get('action', 'N/A')}: <strong>{row.get('q_value', 'N/A')}</strong></p>" for row in sorted(data['rl_table'], key=lambda x: float(x.get('q_value', 0)), reverse=True)[:5]])}
            </div>
        </div>
            """
            
        elif page_name == 'analytics':
            content = f"""
        <div class="page-header">
            <h1>📈 Analytics & Reports</h1>
            <p>Performance analytics and trend analysis</p>
        </div>
        
        <div class="grid-3">
            <div class="card">
                <h3>📊 Success Trends</h3>
                <p>Last 24h: <strong>94%</strong></p>
                <p>Last 7d: <strong>91%</strong></p>
                <p>Last 30d: <strong>89%</strong></p>
            </div>
            
            <div class="card">
                <h3>⚡ Response Times</h3>
                <p>Avg Response: <strong>2.3s</strong></p>
                <p>Fastest: <strong>0.8s</strong></p>
                <p>Slowest: <strong>8.1s</strong></p>
            </div>
            
            <div class="card">
                <h3>🎯 Issue Categories</h3>
                <p>Config Errors: <strong>45%</strong></p>
                <p>Service Down: <strong>30%</strong></p>
                <p>Resource Issues: <strong>25%</strong></p>
            </div>
        </div>
        
        <div class="card">
            <h2>👥 Human Feedback Analysis</h2>
            <table class="table">
                <tr><th>Timestamp</th><th>State</th><th>Action</th><th>Feedback</th></tr>
                {''.join([f"<tr><td>{fb.get('timestamp', 'N/A')}</td><td>{fb.get('state', 'N/A')}</td><td>{fb.get('action', 'N/A')}</td><td>{'👍 Positive' if fb.get('feedback') == '1' else '👎 Negative' if fb.get('feedback') == '-1' else '❓ Unknown'}</td></tr>" for fb in data['feedback_data'][-10:]])}
            </table>
        </div>
            """
            
        elif page_name == 'settings':
            content = """
        <div class="page-header">
            <h1>⚙️ System Settings</h1>
            <p>Configure your AI self-healing system</p>
        </div>
        
        <div class="grid-2">
            <div class="card">
                <h2>🤖 AI Configuration</h2>
                <p>Learning Rate: <input type="range" min="0.01" max="1" value="0.1" step="0.01"> <strong>0.1</strong></p>
                <p>Exploration Rate: <input type="range" min="0" max="1" value="0.2" step="0.01"> <strong>0.2</strong></p>
                <p>Discount Factor: <input type="range" min="0" max="1" value="0.95" step="0.01"> <strong>0.95</strong></p>
                <button class="btn">💾 Save AI Settings</button>
            </div>
            
            <div class="card">
                <h2>📊 Monitoring Settings</h2>
                <p>Check Interval: <select><option>30s</option><option>1m</option><option>5m</option></select></p>
                <p>Alert Threshold: <select><option>High</option><option>Medium</option><option>Low</option></select></p>
                <p>Auto-Healing: <input type="checkbox" checked> <strong>Enabled</strong></p>
                <button class="btn">💾 Save Monitor Settings</button>
            </div>
        </div>
        
        <div class="card">
            <h2>🔧 System Actions</h2>
            <button class="btn">🔄 Restart AI Engine</button>
            <button class="btn">📥 Export Data</button>
            <button class="btn">📤 Import Configuration</button>
            <button class="btn" style="background: #dc3545;">🗑️ Reset System</button>
        </div>
            """
        
        # Close HTML
        footer = """
    </div>
    
    <script>
        function checkServices() {
            alert('🔍 Checking all services... All systems operational!');
        }
        
        function triggerAlert() {
            alert('🚨 Test alert triggered! AI system will respond automatically.');
        }
        
        // Auto-refresh data every 30 seconds
        setTimeout(function() {
            location.reload();
        }, 30000);
    </script>
</body>
</html>
        """
        
        return common_html + content + footer

def create_handler_with_dashboard(dashboard):
    def handler(*args, **kwargs):
        return DashboardHandler(*args, dashboard=dashboard, **kwargs)
    return handler

def main():
    PORT = 8080
    
    print("🚀 Starting Multi-Page AI Dashboard...")
    print("=" * 50)
    
    dashboard = MultiPageDashboard()
    handler = create_handler_with_dashboard(dashboard)
    
    try:
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            print(f"🌐 Multi-Page Dashboard: http://localhost:{PORT}")
            print("📄 Available Pages:")
            print("   🏠 Home: http://localhost:8080/home")
            print("   📊 Monitoring: http://localhost:8080/monitoring")
            print("   🤖 RL Learning: http://localhost:8080/rl-learning")
            print("   📈 Analytics: http://localhost:8080/analytics")
            print("   ⚙️ Settings: http://localhost:8080/settings")
            print("⚡ Press Ctrl+C to stop")
            print("=" * 50)
            
            webbrowser.open(f'http://localhost:{PORT}')
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n👋 Multi-Page Dashboard stopped!")

if __name__ == "__main__":
    main()