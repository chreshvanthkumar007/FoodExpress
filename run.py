"""
FoodExpress - Quick Launch Entry Point
Usage:
    python run.py
"""

import os
import sys
import socket
from app import create_app
from init_db import init_database

def get_local_ip():
    """Retrieve local network IPv4 address for Wi-Fi / LAN testing."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        # Connect to public DNS to determine default network interface IP
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    local_ip = get_local_ip()

    print("\n" + "=" * 60)
    print(" 🍔  FoodExpress - Online Food Delivery System")
    print("=" * 60)
    print(f" [*] Localhost Access:       http://127.0.0.1:{port}")
    if local_ip != '127.0.0.1':
        print(f" [*] Wi-Fi / Local Network:  http://{local_ip}:{port}")
    print(" [*] Admin Portal:           http://127.0.0.1:{port}/admin/login")
    print(" [*] Press Ctrl+C to stop the server.")
    print("=" * 60 + "\n")

    app.run(host='0.0.0.0', port=port, debug=debug)
