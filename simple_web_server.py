import http.server
import socketserver
import webbrowser
import os
import csv
import json
from urllib.parse import urlparse, parse_qs

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/dashboard':
            self.send_dashboard()
        elif self.path == '/api/data':
            self.send_json_data()
        else:
            super().do_GET()
    
    def send_dashboard(self):
        html_content = self.generate_dashboard_html()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def send_json_data(self):
        data = self.get_dashboard_data()
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def get_dashboard_data(self):
        """Get dashboard data from CSV files"""
        project_root = os.path.dirname(os.path.abspath(__file__))
        
        # Load RL table
        rl_data = []
        rl_path = os.path.join(project_root, "data", "rl_table.csv")
        try:
            if os.path.exists(rl_path):
                with open(rl_path, 'r') as f:
                    reader = csv.DictReader(f)
                    rl_data = list(reader)
        except:
            pass
        
        # Load planner logs
        log_data = []
        log_path = os.path.join(project_root, "logs", "planner_log.csv")
        try:
            if os.path.exists(log_path):
                with open(log_path, 'r') as f:
                    reader = csv.DictReader(f)
                    log_data = list(reader)
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
                'success_rate': success_rate
            },
            'rl_table': rl_data[-10:],  # Last 10 entries
            'recent_logs': log_data[-10:]  # Last 10 logs
        }
    
    def generate_dashboard_html(self):
        data = self.get_dashboard_data()
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>🚀 Intelligent System Dashboard</title>
    <meta charset="UTF-8">
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ 
            text-align: center; 
            color: white; 
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .stats {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }}
        .stat-card {{ 
            background: white; 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .stat-number {{ 
            font-size: 2em; 
            font-weight: bold; 
            color: #667eea; 
        }}
        .content {{ 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 20px; 
        }}
        .card {{ 
            background: white; 
            padding: 20px; 
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .table {{ 
            width: 100%; 
            border-collapse: collapse; 
        }}
        .table th, .table td {{ 
            padding: 10px; 
            text-align: left; 
            border-bottom: 1px solid #eee; 
        }}
        .table th {{ 
            background: #f8f9fa; 
            font-weight: bold;
        }}
        .refresh-btn {{ 
            background: #667eea; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            border-radius: 5px; 
            cursor: pointer; 
            margin: 10px 0;
        }}
        .success {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Intelligent System Dashboard</h1>
            <p>Real-time AI-powered deployment monitoring</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{data['stats']['total_actions']}</div>
                <div>Actions Learned</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{data['stats']['total_executions']}</div>
                <div>Total Executions</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{data['stats']['success_rate']}%</div>
                <div>Success Rate</div>
            </div>
        </div>
        
        <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Data</button>
        
        <div class="content">
            <div class="card">
                <h2>🤖 Q-Learning Table</h2>
                <table class="table">
                    <tr><th>State</th><th>Action</th><th>Q-Value</th></tr>
                    {''.join([f"<tr><td>{row.get('state', 'N/A')}</td><td>{row.get('action', 'N/A')}</td><td>{row.get('q_value', 'N/A')}</td></tr>" for row in data['rl_table']])}
                </table>
            </div>
            
            <div class="card">
                <h2>📋 Recent Executions</h2>
                <table class="table">
                    <tr><th>Time</th><th>Action</th><th>Result</th></tr>
                    {''.join([f"<tr><td>{row.get('timestamp', 'N/A')[-8:] if row.get('timestamp') else 'N/A'}</td><td>{row.get('action', 'N/A')}</td><td class=\"{'success' if row.get('result') == 'True' else 'failed'}\">{'✅' if row.get('result') == 'True' else '❌'}</td></tr>" for row in data['recent_logs']])}
                </table>
            </div>
        </div>
        
        <script>
            // Auto-refresh every 30 seconds
            setTimeout(function(){{ location.reload(); }}, 30000);
        </script>
    </div>
</body>
</html>
        """

def start_dashboard_server():
    PORT = 8000
    
    print("🚀 Starting Simple Dashboard Server...")
    print(f"📊 Dashboard available at: http://localhost:{PORT}")
    print("🔄 Auto-refreshes every 30 seconds")
    print("⚡ Press Ctrl+C to stop")
    
    try:
        with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
            # Auto-open browser
            webbrowser.open(f'http://localhost:{PORT}')
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Dashboard server stopped!")

if __name__ == "__main__":
    start_dashboard_server()