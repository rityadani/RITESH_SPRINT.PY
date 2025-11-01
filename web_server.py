from flask import Flask, render_template_string, jsonify
import csv
import os
import json
from datetime import datetime

app = Flask(__name__)

class WebDashboardData:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        
    def load_rl_table(self):
        """Load RL table data"""
        rl_path = os.path.join(self.project_root, "data", "rl_table.csv")
        data = []
        try:
            if os.path.exists(rl_path):
                with open(rl_path, 'r') as f:
                    reader = csv.DictReader(f)
                    data = list(reader)
        except Exception as e:
            print(f"Error loading RL table: {e}")
        return data

    def load_planner_logs(self):
        """Load planner logs"""
        log_path = os.path.join(self.project_root, "logs", "planner_log.csv")
        data = []
        try:
            if os.path.exists(log_path):
                with open(log_path, 'r') as f:
                    reader = csv.DictReader(f)
                    data = list(reader)
        except Exception as e:
            print(f"Error loading planner logs: {e}")
        return data

    def load_human_feedback(self):
        """Load human feedback"""
        feedback_path = os.path.join(self.project_root, "data", "human_feedback.csv")
        data = []
        try:
            if os.path.exists(feedback_path):
                with open(feedback_path, 'r') as f:
                    reader = csv.DictReader(f)
                    data = list(reader)
        except Exception as e:
            print(f"Error loading feedback: {e}")
        return data

    def get_system_stats(self):
        """Calculate system statistics"""
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

dashboard_data = WebDashboardData()

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Intelligent System Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { 
            text-align: center; 
            color: white; 
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        
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
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }
        .stat-card:hover { transform: translateY(-5px); }
        .stat-number { 
            font-size: 2.5em; 
            font-weight: bold; 
            color: #667eea; 
            margin-bottom: 10px;
        }
        .stat-label { 
            color: #666; 
            font-size: 1.1em; 
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
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
            margin-top: 15px;
        }
        .table th, .table td { 
            padding: 12px; 
            text-align: left; 
            border-bottom: 1px solid #eee; 
        }
        .table th { 
            background: #f8f9fa; 
            font-weight: 600;
            color: #333;
        }
        .table tr:hover { background: #f8f9fa; }
        
        .success { color: #28a745; font-weight: bold; }
        .failed { color: #dc3545; font-weight: bold; }
        .refresh-btn { 
            background: #667eea; 
            color: white; 
            border: none; 
            padding: 12px 25px; 
            border-radius: 25px; 
            cursor: pointer; 
            font-size: 1em;
            margin: 20px 0;
            transition: background 0.3s ease;
        }
        .refresh-btn:hover { background: #5a6fd8; }
        
        .full-width { grid-column: 1 / -1; }
        .action-item { 
            display: flex; 
            justify-content: space-between; 
            padding: 10px 0; 
            border-bottom: 1px solid #eee;
        }
        .q-value { 
            background: #667eea; 
            color: white; 
            padding: 4px 12px; 
            border-radius: 15px; 
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Intelligent System Dashboard</h1>
            <p>Real-time monitoring of AI-powered deployment automation</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{ stats.total_actions }}</div>
                <div class="stat-label">Actions Learned</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.total_executions }}</div>
                <div class="stat-label">Total Executions</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.success_rate }}%</div>
                <div class="stat-label">Success Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.human_feedbacks }}</div>
                <div class="stat-label">Human Feedbacks</div>
            </div>
        </div>
        
        <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Data</button>
        
        <div class="content-grid">
            <div class="card">
                <h2>🏆 Top Performing Actions</h2>
                {% for action, q_value in stats.top_actions.items() %}
                <div class="action-item">
                    <span>{{ action }}</span>
                    <span class="q-value">{{ "%.3f"|format(q_value) }}</span>
                </div>
                {% endfor %}
            </div>
            
            <div class="card">
                <h2>📋 Recent Executions</h2>
                <table class="table">
                    <thead>
                        <tr><th>Time</th><th>Action</th><th>Result</th></tr>
                    </thead>
                    <tbody>
                        {% for log in recent_logs %}
                        <tr>
                            <td>{{ log.timestamp[-8:] if log.timestamp else 'N/A' }}</td>
                            <td>{{ log.action }}</td>
                            <td class="{{ 'success' if log.result == 'True' else 'failed' }}">
                                {{ '✅' if log.result == 'True' else '❌' }}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            <div class="card full-width">
                <h2>🤖 Q-Learning Table</h2>
                <table class="table">
                    <thead>
                        <tr><th>State</th><th>Action</th><th>Q-Value</th></tr>
                    </thead>
                    <tbody>
                        {% for row in rl_table %}
                        <tr>
                            <td>{{ row.state }}</td>
                            <td>{{ row.action }}</td>
                            <td><span class="q-value">{{ row.q_value }}</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Main dashboard route"""
    stats = dashboard_data.get_system_stats()
    rl_table = dashboard_data.load_rl_table()
    recent_logs = dashboard_data.load_planner_logs()[-10:]  # Last 10 logs
    
    return render_template_string(HTML_TEMPLATE, 
                                stats=stats, 
                                rl_table=rl_table, 
                                recent_logs=recent_logs)

@app.route('/api/stats')
def api_stats():
    """API endpoint for stats"""
    return jsonify(dashboard_data.get_system_stats())

@app.route('/api/rl-table')
def api_rl_table():
    """API endpoint for RL table"""
    return jsonify(dashboard_data.load_rl_table())

@app.route('/api/logs')
def api_logs():
    """API endpoint for logs"""
    return jsonify(dashboard_data.load_planner_logs())

if __name__ == '__main__':
    print("🚀 Starting Intelligent System Web Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🔄 Data refreshes automatically from CSV files")
    print("⚡ Press Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=5000, debug=True)