"""
Feature 30: Enterprise User Control Panel (Flask-Compatible Version)
Simplified for Render deployment while maintaining core functionality
"""
import json
import time
from datetime import datetime
from typing import Dict, List
from flask import jsonify, request

class EnterpriseUserControlPanel:
    def __init__(self):
        self.user_settings = self._load_default_settings()
        self.control_history = []
        
    def _load_default_settings(self) -> Dict:
        """Load default control panel settings"""
        return {
            'flash_loan': {
                'max_capacity': 500000000,
                'current_capacity': 100000000,
                'max_per_tx': 10000000
            },
            'reinvestment': {
                'auto_compound_rate': 80,
                'strategy_profile': 'balanced',
                'frequency': 'real_time'
            },
            'risk_management': {
                'profile': 'balanced',
                'dynamic_adjustment': True
            },
            'profit_targets': {
                'daily_target': 250000,
                'auto_scaling': True
            },
            'strategies': {
                'flash_loan_arbitrage': {'enabled': True, 'weight': 35},
                'cross_dex_arbitrage': {'enabled': True, 'weight': 25},
                'liquidity_provision': {'enabled': True, 'weight': 15},
                'yield_farming': {'enabled': True, 'weight': 10},
                'derivatives_arb': {'enabled': True, 'weight': 15}
            },
            'safety': {
                'emergency_stop': False,
                'capital_preservation_mode': False
            }
        }
    
    def get_control_panel_data(self) -> Dict:
        """Get complete control panel data for API"""
        return {
            "control_panel": {
                "settings": self.user_settings,
                "health_score": self.calculate_health_score(),
                "last_updated": datetime.now().isoformat(),
                "features": [
                    "Flash Loan Capacity Controls",
                    "Profit Reinvestment Intelligence", 
                    "Risk Level Management",
                    "Daily Profit Target System",
                    "Strategy-Specific Controls",
                    "Safety & Emergency Controls"
                ]
            }
        }
    
    def update_setting(self, category: str, key: str, value) -> Dict:
        """Update a specific setting"""
        try:
            if category in self.user_settings and key in self.user_settings[category]:
                self.user_settings[category][key] = value
                
                # Log the change
                self.control_history.append({
                    'timestamp': time.time(),
                    'category': category,
                    'key': key,
                    'value': value,
                    'health_score': self.calculate_health_score()
                })
                
                return {
                    "success": True,
                    "message": f"Updated {category}.{key} = {value}",
                    "health_score": self.calculate_health_score()
                }
            else:
                return {"success": False, "error": "Setting not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def calculate_health_score(self) -> int:
        """Calculate system health score"""
        score = 100
        
        # Risk profile adjustments
        if self.user_settings['risk_management']['profile'] == 'aggressive':
            score -= 15
        elif self.user_settings['risk_management']['profile'] == 'conservative':
            score += 5
            
        # Capacity adjustments  
        capacity_ratio = self.user_settings['flash_loan']['current_capacity'] / self.user_settings['flash_loan']['max_capacity']
        if capacity_ratio > 0.8:  # >80% capacity
            score -= 10
            
        # Strategy adjustments
        enabled_strategies = sum(1 for s in self.user_settings['strategies'].values() if s['enabled'])
        if enabled_strategies < 2:
            score -= 20
            
        return max(0, min(100, score))
    
    def emergency_stop(self) -> Dict:
        """Activate emergency stop"""
        self.user_settings['safety']['emergency_stop'] = True
        self.user_settings['safety']['capital_preservation_mode'] = True
        
        return {
            "emergency_stop": True,
            "message": "ÔøΩÔøΩ ALL TRADING HALTED - Capital Preservation Active",
            "timestamp": datetime.now().isoformat()
        }
    
    def resume_operations(self) -> Dict:
        """Resume normal operations"""
        self.user_settings['safety']['emergency_stop'] = False
        self.user_settings['safety']['capital_preservation_mode'] = False
        
        return {
            "emergency_stop": False,
            "message": "‚úÖ Operations Resumed - Trading Active",
            "timestamp": datetime.now().isoformat()
        }

# Global control panel instance
control_panel = EnterpriseUserControlPanel()

# Flask routes for the control panel
def setup_control_panel_routes(app):
    """Setup control panel API routes"""
    
    @app.route('/api/control-panel')
    def get_control_panel():
        return jsonify(control_panel.get_control_panel_data())
    
    @app.route('/api/control-panel/update', methods=['POST'])
    def update_control_setting():
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

# HTML interface for control panel
CONTROL_PANEL_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Ainexus Enterprise Control Panel</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #0f0f23; color: #00ff00; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .control-section { background: #1a1a2e; padding: 20px; margin: 10px 0; border-radius: 8px; border: 1px solid #00ff00; }
        .control-row { display: flex; justify-content: space-between; align-items: center; margin: 10px 0; }
        .health-score { font-size: 24px; font-weight: bold; text-align: center; margin: 20px 0; }
        .emergency-btn { background: #ff4444; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 18px; }
        .resume-btn { background: #00ff88; color: black; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 18px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Ì∫Ä Ainexus Enterprise Control Panel</h1>
            <p>Real-time Management for 36-Feature Engine</p>
        </div>
        
        <div class="health-score" id="health-score">
            System Health: Loading...
        </div>
        
        <div class="control-section">
            <h3>Ì∫® Emergency Controls</h3>
            <button class="emergency-btn" onclick="emergencyStop()">EMERGENCY STOP</button>
            <button class="resume-btn" onclick="resumeOperations()">RESUME OPERATIONS</button>
        </div>
        
        <div class="control-section">
            <h3>Ì≤∞ Flash Loan Controls</h3>
            <div class="control-row">
                <span>Current Capacity: $100M</span>
                <button onclick="updateSetting('flash_loan', 'current_capacity', 150000000)">Increase to $150M</button>
            </div>
        </div>
        
        <div class="control-section">
            <h3>Ì≥à Profit Reinvestment</h3>
            <div class="control-row">
                <span>Auto-Compound Rate: 80%</span>
                <button onclick="updateSetting('reinvestment', 'auto_compound_rate', 90)">Increase to 90%</button>
            </div>
        </div>
        
        <div class="control-section">
            <h3>Ìª°Ô∏è Risk Management</h3>
            <div class="control-row">
                <span>Current Profile: Balanced</span>
                <button onclick="updateSetting('risk_management', 'profile', 'aggressive')">Set Aggressive</button>
                <button onclick="updateSetting('risk_management', 'profile', 'conservative')">Set Conservative</button>
            </div>
        </div>
        
        <div class="control-section">
            <h3>Ì¥ß API Endpoints</h3>
            <p><a href="/api/control-panel">/api/control-panel</a> - Full settings</p>
            <p><a href="/api/control-panel/health">/api/control-panel/health</a> - Health status</p>
        </div>
    </div>
    
    <script>
        async function updateHealthScore() {
            const response = await fetch('/api/control-panel/health');
            const data = await response.json();
            document.getElementById('health-score').textContent = 
                `System Health: ${data.health_score}% | Emergency Stop: ${data.emergency_stop ? 'ACTIVE' : 'INACTIVE'} | Capacity: ${data.total_capacity}`;
        }
        
        async function updateSetting(category, key, value) {
            const response = await fetch('/api/control-panel/update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({category, key, value})
            });
            const result = await response.json();
            alert(result.message || result.error);
            updateHealthScore();
        }
        
        async function emergencyStop() {
            if(confirm('Ì∫® ACTIVATE EMERGENCY STOP? This will halt all trading.')) {
                const response = await fetch('/api/control-panel/emergency-stop', {method: 'POST'});
                const result = await response.json();
                alert(result.message);
                updateHealthScore();
            }
        }
        
        async function resumeOperations() {
            const response = await fetch('/api/control-panel/resume', {method: 'POST'});
            const result = await response.json();
            alert(result.message);
            updateHealthScore();
        }
        
        // Update health score every 5 seconds
        setInterval(updateHealthScore, 5000);
        updateHealthScore();
    </script>
</body>
</html>
'''

def get_control_panel_html():
    """Get HTML interface for control panel"""
    return CONTROL_PANEL_HTML
