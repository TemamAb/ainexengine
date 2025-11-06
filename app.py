from flask import Flask, render_template, jsonify
import os
from src.dashboard.live_trading import LiveTradingSystem
from src.capital.dynamic_optimizer import DynamicCapitalOptimizer

app = Flask(__name__)

# Initialize core systems
trading_system = LiveTradingSystem()
capital_optimizer = DynamicCapitalOptimizer()

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'systems': {
            'trading': trading_system.get_status(),
            'capital_optimizer': capital_optimizer.get_status()
        }
    })

@app.route('/api/activate-trading', methods=['POST'])
def activate_trading():
    result = trading_system.activate_7_phase_system()
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
