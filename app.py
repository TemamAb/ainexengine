from flask import Flask, jsonify, render_template
import os
import asyncio
import threading
import time
from src.main_original import AINexusStealthEngine

app = Flask(__name__)
engine = None
engine_status = "initializing"
profit_data = {"hourly": 0, "daily": 0, "total": 0}
active_features = 0

def run_engine():
    """Run the Ainexus engine in a background thread"""
    global engine, engine_status, active_features
    
    try:
        engine = AINexusStealthEngine()
        engine_status = "running"
        
        # Get event loop and run engine
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(engine.start_35_feature_engine())
        
    except Exception as e:
        engine_status = f"error: {str(e)}"
        print(f"Engine error: {e}")

# Start engine in background thread
engine_thread = threading.Thread(target=run_engine, daemon=True)
engine_thread.start()

@app.route('/')
def dashboard():
    """Main dashboard showing Ainexus engine status"""
    return jsonify({
        "message": "íº€ Ainexus 35-Feature Engine - LIVE",
        "status": engine_status,
        "features_active": active_features,
        "daily_target": "$250,000",
        "profit_data": profit_data,
        "endpoints": {
            "health": "/health",
            "status": "/status", 
            "features": "/features",
            "profit": "/profit"
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "engine": engine_status})

@app.route('/status')
def status():
    """Detailed engine status"""
    return jsonify({
        "engine": "AINexus 35-Feature Stealth Engine",
        "status": engine_status,
        "target_profit": "$250,000/day",
        "active_since": time.time(),
        "version": "2.0.0"
    })

@app.route('/features')
def features():
    """Show available features"""
    return jsonify({
        "total_features": 35,
        "active_features": active_features,
        "categories": {
            "core_infrastructure": 8,
            "ai_optimization": 6, 
            "profit_acceleration": 7,
            "dashboard_controls": 9,
            "chief_architect": 5
        }
    })

@app.route('/profit')
def profit():
    """Profit tracking endpoint"""
    return jsonify({
        "hourly_profit": profit_data["hourly"],
        "daily_profit": profit_data["daily"], 
        "total_profit": profit_data["total"],
        "target_daily": 250000,
        "performance": "active" if engine_status == "running" else "paused"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
