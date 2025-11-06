from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "Ainexus Engine - DEPLOYED",
        "status": "running", 
        "features": 35,
        "version": "2.0.0"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/features')
def features():
    return jsonify({
        "total_features": 35,
        "categories": ["Flash Loan Engine", "Gasless System", "Cross-Chain MEV", "AI Optimization", "Stealth Mode"]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
