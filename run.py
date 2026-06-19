import sys
import os
import socket

# Add local path to sys.path to guarantee modules load correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
import database

def get_local_ip():
    """Gets the local IP address of the computer on the Wi-Fi network."""
    try:
        # Create a dummy socket connection to find the primary network interface IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == '__main__':
    # Initialize database
    database.init_db()
    
    local_ip = get_local_ip()
    
    print("=" * 65)
    print("   Karnataka AO Revision Handbook Web Portal starting up...")
    print("   Access URLs:")
    print(f"     - Candidate Portal (Local):  http://127.0.0.1:8080/")
    print(f"     - Candidate Portal (Mobile): http://{local_ip}:8080/")
    print(f"     - Admin Dashboard (Local):   http://127.0.0.1:8080/admin")
    print(f"     - Admin Dashboard (Mobile):  http://{local_ip}:8080/admin")
    print("=" * 65)
    
    # Run server on 0.0.0.0 on port 8080 to enable mobile phone access on the same Wi-Fi
    app.run(host='0.0.0.0', port=8080, debug=True)
