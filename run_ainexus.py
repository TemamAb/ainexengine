import os
import socket
from app import app

def find_free_port():
    for port in range(5000, 6000):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return 8080  # fallback

if __name__ == '__main__':
    port = find_free_port()
    print(f"íº€ Starting Ainexus Engine on port {port}")
    print(f"í³Š Dashboard: http://localhost:{port}")
    print(f"í´§ Features: http://localhost:{port}/features")
    print(f"í´– AI: http://localhost:{port}/ai/optimizer")
    print("í²¡ Press Ctrl+C to stop the engine")
    
    # Set the port for Flask
    os.environ['PORT'] = str(port)
    app.run(host='0.0.0.0', port=port, debug=False)
