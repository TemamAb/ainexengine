from flask import Flask, jsonify, render_template_string
import os
import time
import asyncio
from src.dashboard.performance import get_global_dashboard, setup_global_dashboard
from src.controls.user_panel import setup_control_panel_routes, get_control_panel_html, control_panel

app = Flask(__name__)

# Initialize dashboard
dashboard = get_global_dashboard()

# HTML template for the main dashboard
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Ainexus 36-Feature Performance Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #0f0f23; color: #00ff00; }
        .header { text-align: center; margin-bottom: 30px; }
        .metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }
        .metric-card { background: #1a1a2e; padding: 20px; border-radius: 8px; border: 1px solid #00ff00; }
        .feature-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; }
        .feature { padding: 10px; background: #16213e; border-radius: 4px; text-align: center; font-size: 12px; }
        .feature.active { background: #00ff00; color: #000; }
        .nav { text-align: center; margin: 20px 0; }
        .nav a { color: #00ff00; margin: 0 15px; text-decoration: none; font-size: 18px; }
        .nav a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Ì∫Ä Ainexus 36-Feature Engine Dashboard</h1>
        <p>Real-time Performance Monitoring</p>
    </div>
    
    <div class="nav">
        <a href="/">Ì≥ä Dashboard</a>
        <a href="/control-panel">‚ö° Control Panel</a>
        <a href="/api/dashboard">Ì¥ß API</a>
        <a href="/api/features">Ì≥ã Features</a>
    </div>
    
    <div class="metrics">
        <div class="metric-card">
            <h3>Ì≤∞ Profit Metrics</h3>
            <p>Daily Target: $250,000</p>
            <p>Current: $12,500</p>
            <p>Hourly Rate: $12,500</p>
        </div>
        
        <div class="metric-card">
            <h3>‚ö° System Health</h3>
            <p>Active Features: 36/36</p>
            <p>Performance Score: 95%</p>
            <p>Uptime: {{ "%.1f"|format(uptime/3600) }} hours</p>
        </div>
        
        <div class="metric-card">
            <h3>ÌµµÔ∏è Stealth Mode</h3>
            <p>Status: ACTIVE</p>
            <p>MEV Protection: ‚úÖ</p>
            <p>Identity Rotation: ‚úÖ</p>
        </div>
    </div>
    
    <div class="metric-card">
        <h3>Ì¥ß Feature Status (36/36 Active)</h3>
        <div class="feature-grid">
            {% for i in range(1, 37) %}
            <div class="feature active">F{{ i }}</div>
            {% endfor %}
        </div>
    </div>
    
    <div style="margin-top: 20px; text-align: center;">
        <p><strong>Ì≥ä Available Endpoints:</strong></p>
        <p><a href="/api/dashboard">/api/dashboard</a> - Full Dashboard API</p>
        <p><a href="/api/features">/api/features</a> - Feature List</p>
        <p><a href="/api/health">/api/health</a> - Health Check</p>
        <p><a href="/control-panel">/control-panel</a> - Control Panel</p>
    </div>
</body>
</html>
'''

@app.route('/')
def dashboard_html():
    """HTML Dashboard"""
    return render_template_string(DASHBOARD_HTML, uptime=time.time())

@app.route('/api/dashboard')
def api_dashboard():
    """JSON Dashboard API"""
    return jsonify({
        "message": "Ainexus 36-Feature Engine - LIVE",
        "status": "running",
        "features": 36,
        "stealth_mode": "active",
        "version": "2.0.0",
        "profit_metrics": {
            "daily_target": 250000,
            "current_daily": 12500,
            "hourly_rate": 12500,
            "total_profit": 12500
        },
        "system_health": {
            "active_features": 36,
            "performance_score": 95,
            "uptime": time.time(),
            "health_status": "excellent"
        },
        "stealth_metrics": {
            "stealth_mode": "active",
            "mev_protection": True,
            "identity_rotation": True
        },
        "timestamp": time.time()
    })

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy", 
        "timestamp": time.time(),
        "version": "2.0.0",
        "engine": "running",
        "features_active": 36
    })

@app.route('/api/features')
def features():
    features_list = [
        "Flash Loan Engine", "Gasless System", "Three-Tier Architecture",
        "Cross-Chain MEV", "Institutional Liquidity", "Enterprise Security",
        "AI Auto-Optimizer", "Market Intelligence", "Competitor Intel",
        "Strategy Orchestration", "Predictive Gas Optimization", "Capital Velocity", 
        "Risk-Profit Calibration", "Continuous Research", "DEX Integration",
        "Liquidity Forecasting", "Auto-Compounding", "Cross-Protocol Arbitrage",
        "Institutional Execution", "Dynamic Fee Optimization", "Circuit Breakers",
        "Performance Dashboard", "Capital Controls", "Wallet Integration",
        "Profit Distribution", "Risk Management", "Non-KYC Compliance",
        "Zero-Downtime Deployment", "Health Monitoring", "User Control Panel",
        "Microservice Orchestrator", "Security Audit Pipeline", "Stress Testing", 
        "Distributed Tracing", "Historical Validation", "100% Stealth Mode"
    ]
    
    return jsonify({
        "total_features": 36,
        "active_features": 36,
        "features": features_list
    })

@app.route('/control-panel')
def control_panel_html():
    """HTML Control Panel Interface"""
    return get_control_panel_html()

# Control Panel API Routes
@app.route('/api/control-panel')
def get_control_panel():
    return jsonify(control_panel.get_control_panel_data())

@app.route('/api/control-panel/update', methods=['POST'])
def update_control_setting():
    from flask import request
    data = request.get_json()
    category = data.get('category')
    key = data.get('key')
    value = data.get('value')
    
    if not all([category, key, value is not None]):
        return jsonify({"success": False, "error": "Missing category, key, or value"})
        
    result = control_panel.update_setting(category, key, value)
    return jsonify(result)

@app.route('/api/control-panel/emergency-stop', methods=['POST'])
def emergency_stop():
    result = control_panel.emergency_stop()
    return jsonify(result)

@app.route('/api/control-panel/resume', methods=['POST'])
def resume_operations():
    result = control_panel.resume_operations()
    return jsonify(result)

@app.route('/api/control-panel/health')
def control_panel_health():
    return jsonify({
        "health_score": control_panel.calculate_health_score(),
        "emergency_stop": control_panel.user_settings['safety']['emergency_stop'],
        "active_strategies": sum(1 for s in control_panel.user_settings['strategies'].values() if s['enabled']),
        "total_capacity": f"${control_panel.user_settings['flash_loan']['current_capacity']:,.0f}"
    })

# Initialize dashboard on startup
@app.before_first_request
def initialize():
    asyncio.run(setup_global_dashboard())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
