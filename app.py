from flask import Flask, jsonify
import os
import time

app = Flask(__name__)

@app.route('/')
def dashboard():
    return jsonify({
        "message": "Ainexus 36-Feature Engine - LIVE",
        "status": "running", 
        "features": 36,
        "version": "2.0.0",
        "stealth_mode": "active"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/features')
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
        "features": features_list
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# Import and setup control panel
from src.controls.user_panel import setup_control_panel_routes, get_control_panel_html, control_panel

# Setup control panel routes
setup_control_panel_routes(app)

@app.route('/control-panel')
def control_panel_html():
    """HTML Control Panel Interface"""
    return get_control_panel_html()

@app.route('/api/control-panel/strategies')
def get_strategies():
    """Get strategy information"""
    return jsonify({
        "strategies": control_panel.user_settings['strategies'],
        "total_enabled": sum(1 for s in control_panel.user_settings['strategies'].values() if s['enabled'])
    })
